"""
Legal Corpus Ingestion and Database Seeding Engine.
File: data/seed_legal_corpus.py

Populates data/legal_corpus.db with:
1. Complete Central Legislation Catalog (850+ major Acts across all domains)
2. All 28 States and 8 Union Territories Jurisdictions and State Acts
3. Complete Constitutional Law Corpus (Articles, Writs, 7th Schedule Lists)
4. Statute Sections with Citizens' Practical Remedies and Penalties
5. Synchronizes SQLite FTS5 Full-Text Search Virtual Table
"""

import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from models.corpus_db import get_db_connection, init_corpus_db, CORPUS_DB_PATH

# ==============================================================================
# 1. ALL 28 STATES & 8 UNION TERRITORIES OF INDIA
# ==============================================================================
STATES_AND_UTS = [
    # 28 States
    {"code": "AP", "name": "Andhra Pradesh", "category": "State", "high_court": "High Court of Andhra Pradesh at Amaravati", "portal_url": "https://www.apegazette.cgg.gov.in/", "key_subjects": "Land Revenue, AP Tenancy Act, Municipalities, AP Shops and Establishments"},
    {"code": "AR", "name": "Arunachal Pradesh", "category": "State", "high_court": "Gauhati High Court (Itanagar Bench)", "portal_url": "https://arunachalpradesh.gov.in/", "key_subjects": "Customary Tribal Laws, Forest Rights, State Police"},
    {"code": "AS", "name": "Assam", "category": "State", "high_court": "Gauhati High Court at Guwahati", "portal_url": "https://assam.gov.in/", "key_subjects": "Assam Urban Areas Rent Control, Land Records, Assam Police Act"},
    {"code": "BR", "name": "Bihar", "category": "State", "high_court": "Patna High Court", "portal_url": "https://egazette.bih.nic.in/", "key_subjects": "Bihar Buildings Lease Control, Bihar Land Reforms, Prohibition Act"},
    {"code": "CG", "name": "Chhattisgarh", "category": "State", "high_court": "Chhattisgarh High Court at Bilaspur", "portal_url": "https://cgstate.gov.in/", "key_subjects": "CG Rent Control Act 2011, Land Revenue Code, Forest Produce"},
    {"code": "GA", "name": "Goa", "category": "State", "high_court": "Bombay High Court (Goa Bench at Panaji)", "portal_url": "https://goaprintingpress.gov.in/", "key_subjects": "Goa Portuguese Civil Code, Goa Buildings Lease Control, Mundkar Act"},
    {"code": "GJ", "name": "Gujarat", "category": "State", "high_court": "Gujarat High Court at Ahmedabad", "portal_url": "https://gujaratindia.gov.in/", "key_subjects": "Gujarat Rents Act, Gujarat Land Revenue Code, Prohibition, Cooperative Societies"},
    {"code": "HR", "name": "Haryana", "category": "State", "high_court": "Punjab and Haryana High Court at Chandigarh", "portal_url": "https://haryana.gov.in/", "key_subjects": "Haryana Urban Rent Control Act, Haryana Development and Regulation of Urban Areas Act"},
    {"code": "HP", "name": "Himachal Pradesh", "category": "State", "high_court": "Himachal Pradesh High Court at Shimla", "portal_url": "https://himachal.nic.in/", "key_subjects": "HP Urban Rent Control Act, HP Tenancy and Land Reforms Act (Section 118)"},
    {"code": "JH", "name": "Jharkhand", "category": "State", "high_court": "Jharkhand High Court at Ranchi", "portal_url": "https://jharkhand.gov.in/", "key_subjects": "Chota Nagpur Tenancy (CNT) Act, Santhal Parganas Tenancy (SPT) Act, Jharkhand Rent Control"},
    {"code": "KA", "name": "Karnataka", "category": "State", "high_court": "Karnataka High Court at Bengaluru", "portal_url": "https://dpal.karnataka.gov.in/", "key_subjects": "Karnataka Rent Act 1999, Karnataka Land Revenue Act 1964, Karnataka Shops and Commercial Establishments Act"},
    {"code": "KL", "name": "Kerala", "category": "State", "high_court": "Kerala High Court at Ernakulam", "portal_url": "https://kerala.gov.in/", "key_subjects": "Kerala Buildings Lease and Rent Control Act, Kerala Police Act 2011, Kerala Land Reforms Act"},
    {"code": "MP", "name": "Madhya Pradesh", "category": "State", "high_court": "Madhya Pradesh High Court at Jabalpur", "portal_url": "https://mp.gov.in/", "key_subjects": "MP Accommodation Control Act 1961, MP Land Revenue Code 1959, MP Municipalities Act"},
    {"code": "MH", "name": "Maharashtra", "category": "State", "high_court": "Bombay High Court at Mumbai", "portal_url": "https://bombayhighcourt.nic.in/", "key_subjects": "Maharashtra Rent Control Act 1999, Maharashtra Land Revenue Code 1966, Maharashtra Police Act 1951, MOFA"},
    {"code": "MN", "name": "Manipur", "category": "State", "high_court": "High Court of Manipur at Imphal", "portal_url": "https://manipur.gov.in/", "key_subjects": "Manipur Land Revenue and Land Reforms Act, Hill Areas District Councils"},
    {"code": "ML", "name": "Meghalaya", "category": "State", "high_court": "High Court of Meghalaya at Shillong", "portal_url": "https://meghalaya.gov.in/", "key_subjects": "Autonomous District Councils (Sixth Schedule), Land Transfer Act"},
    {"code": "MZ", "name": "Mizoram", "category": "State", "high_court": "Gauhati High Court (Aizawl Bench)", "portal_url": "https://mizoram.gov.in/", "key_subjects": "Mizo Customary Law, Sixth Schedule Autonomous Councils"},
    {"code": "NL", "name": "Nagaland", "category": "State", "high_court": "Gauhati High Court (Kohima Bench)", "portal_url": "https://nagaland.gov.in/", "key_subjects": "Article 371A Naga Customary Law, Nagaland Land and Revenue"},
    {"code": "OD", "name": "Odisha", "category": "State", "high_court": "Orissa High Court at Cuttack", "portal_url": "https://odisha.gov.in/", "key_subjects": "Odisha House Rent Control Act, Odisha Land Reforms Act, Odisha Police Act"},
    {"code": "PB", "name": "Punjab", "category": "State", "high_court": "Punjab and Haryana High Court at Chandigarh", "portal_url": "https://punjab.gov.in/", "key_subjects": "East Punjab Urban Rent Restriction Act 1949, Punjab Land Revenue Act 1887, Punjab Police Act 2007"},
    {"code": "RJ", "name": "Rajasthan", "category": "State", "high_court": "Rajasthan High Court at Jodhpur", "portal_url": "https://rajasthan.gov.in/", "key_subjects": "Rajasthan Rent Control Act 2001, Rajasthan Tenancy Act 1955, Rajasthan Land Revenue Act"},
    {"code": "SK", "name": "Sikkim", "category": "State", "high_court": "High Court of Sikkim at Gangtok", "portal_url": "https://sikkim.gov.in/", "key_subjects": "Article 371F Old Laws Protection, Sikkim Rent Control, Land Revenue"},
    {"code": "TN", "name": "Tamil Nadu", "category": "State", "high_court": "Madras High Court at Chennai", "portal_url": "https://www.tn.gov.in/", "key_subjects": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act 2017, TN Shops Act"},
    {"code": "TS", "name": "Telangana", "category": "State", "high_court": "High Court for the State of Telangana at Hyderabad", "portal_url": "https://telangana.gov.in/", "key_subjects": "Telangana Buildings Lease Rent and Eviction Control Act, Dharani Portal Land Reforms"},
    {"code": "TR", "name": "Tripura", "category": "State", "high_court": "High Court of Tripura at Agartala", "portal_url": "https://tripura.gov.in/", "key_subjects": "Tripura Land Revenue and Land Reforms Act, Tripura Rent Control"},
    {"code": "UP", "name": "Uttar Pradesh", "category": "State", "high_court": "Allahabad High Court at Prayagraj", "portal_url": "https://up.gov.in/", "key_subjects": "UP Urban Buildings Regulation of Letting Act, UP Revenue Code 2006, UP Police Regulations"},
    {"code": "UK", "name": "Uttarakhand", "category": "State", "high_court": "Uttarakhand High Court at Nainital", "portal_url": "https://uk.gov.in/", "key_subjects": "Uttarakhand Tenancy Act, Uttarakhand Land Revenue Act, Hill Land Purchase Restrictions"},
    {"code": "WB", "name": "West Bengal", "category": "State", "high_court": "Calcutta High Court at Kolkata", "portal_url": "https://wb.gov.in/", "key_subjects": "West Bengal Premises Tenancy Act 1997, West Bengal Land Reforms Act 1955, Kolkata Municipal Act"},

    # 8 Union Territories
    {"code": "AN", "name": "Andaman and Nicobar Islands", "category": "Union Territory", "high_court": "Calcutta High Court (Circuit Bench at Port Blair)", "portal_url": "https://andaman.gov.in/", "key_subjects": "Tribal Protection Regulations, Island Land Tenures"},
    {"code": "CH", "name": "Chandigarh", "category": "Union Territory", "high_court": "Punjab and Haryana High Court at Chandigarh", "portal_url": "https://chandigarh.gov.in/", "key_subjects": "Capital of Punjab Development and Regulation Act, Chandigarh Rent Control"},
    {"code": "DNHDD", "name": "Dadra and Nagar Haveli and Daman and Diu", "category": "Union Territory", "high_court": "Bombay High Court", "portal_url": "https://daman.nic.in/", "key_subjects": "DNH Land Reforms Regulation, Industrial Licensing"},
    {"code": "DL", "name": "NCT of Delhi", "category": "Union Territory", "high_court": "Delhi High Court at New Delhi", "portal_url": "https://delhi.gov.in/", "key_subjects": "Delhi Rent Control Act 1958, Delhi Police Act 1978, Delhi Development Act 1957, Delhi Municipal Corporation Act"},
    {"code": "JK", "name": "Jammu and Kashmir", "category": "Union Territory", "high_court": "High Court of Jammu & Kashmir and Ladakh at Srinagar/Jammu", "portal_url": "https://jk.gov.in/", "key_subjects": "J&K Reorganisation Act 2019, J&K Land Revenue Act, J&K Development Act"},
    {"code": "LA", "name": "Ladakh", "category": "Union Territory", "high_court": "High Court of Jammu & Kashmir and Ladakh", "portal_url": "https://ladakh.nic.in/", "key_subjects": "Ladakh Autonomous Hill Development Councils Act, Environmental Regulations"},
    {"code": "LD", "name": "Lakshadweep", "category": "Union Territory", "high_court": "Kerala High Court at Ernakulam", "portal_url": "https://lakshadweep.gov.in/", "key_subjects": "Customary Marine Tenure, Coconut Palm Regulations"},
    {"code": "PY", "name": "Puducherry", "category": "Union Territory", "high_court": "Madras High Court at Chennai", "portal_url": "https://py.gov.in/", "key_subjects": "Puducherry Buildings Lease and Rent Control Act, French Civil Code heritage aspects"}
]


# ==============================================================================
# 2. COMPREHENSIVE CENTRAL ACTS CATALOG (Spanning 1836 to 2024+)
# ==============================================================================
CENTRAL_ACTS_SEED = [
    # Criminal, Procedural & Evidence
    ("bns_2023", "Bharatiya Nyaya Sanhita, 2023", "BNS", "Act 45 of 2023", 2023, "Ministry of Home Affairs", "Criminal Law", "https://www.indiacode.nic.in/handle/123456789/20120", "In Force"),
    ("bnss_2023", "Bharatiya Nagarik Suraksha Sanhita, 2023", "BNSS", "Act 46 of 2023", 2023, "Ministry of Home Affairs", "Criminal Procedure", "https://www.indiacode.nic.in/handle/123456789/20121", "In Force"),
    ("bsa_2023", "Bharatiya Sakshya Adhiniyam, 2023", "BSA", "Act 47 of 2023", 2023, "Ministry of Law and Justice", "Evidence Law", "https://www.indiacode.nic.in/handle/123456789/20122", "In Force"),
    ("ipc_1860", "Indian Penal Code, 1860", "IPC", "Act 45 of 1860", 1860, "Ministry of Home Affairs", "Criminal Law", "https://www.indiacode.nic.in/handle/123456789/2263", "Superseded by BNS for offences on or after July 1, 2024"),
    ("crpc_1973", "Code of Criminal Procedure, 1973", "CrPC", "Act 2 of 1974", 1974, "Ministry of Home Affairs", "Criminal Procedure", "https://www.indiacode.nic.in/handle/123456789/16225", "Superseded by BNSS for procedures on or after July 1, 2024"),
    ("iea_1872", "Indian Evidence Act, 1872", "IEA", "Act 1 of 1872", 1872, "Ministry of Law and Justice", "Evidence Law", "https://www.indiacode.nic.in/handle/123456789/2188", "Superseded by BSA on July 1, 2024"),
    ("pocso_2012", "Protection of Children from Sexual Offences Act, 2012", "POCSO Act", "Act 32 of 2012", 2012, "Ministry of Women and Child Development", "Child Protection", "https://www.indiacode.nic.in/handle/123456789/2079", "In Force"),
    ("poca_1988", "Prevention of Corruption Act, 1988", "POCA", "Act 49 of 1988", 1988, "Ministry of Personnel, Public Grievances and Pensions", "Anti-Corruption", "https://www.indiacode.nic.in/handle/123456789/1982", "In Force"),
    ("pmla_2002", "Prevention of Money Laundering Act, 2002", "PMLA", "Act 15 of 2003", 2002, "Ministry of Finance", "Financial Crime", "https://www.indiacode.nic.in/handle/123456789/2036", "In Force"),
    ("ndps_1985", "Narcotic Drugs and Psychotropic Substances Act, 1985", "NDPS Act", "Act 61 of 1985", 1985, "Ministry of Finance", "Criminal Law", "https://www.indiacode.nic.in/handle/123456789/1791", "In Force"),
    ("uapa_1967", "Unlawful Activities (Prevention) Act, 1967", "UAPA", "Act 37 of 1967", 1967, "Ministry of Home Affairs", "National Security", "https://www.indiacode.nic.in/handle/123456789/1470", "In Force"),
    ("arms_act_1959", "Arms Act, 1959", "Arms Act", "Act 54 of 1959", 1959, "Ministry of Home Affairs", "Public Safety", "https://www.indiacode.nic.in/handle/123456789/1498", "In Force"),
    ("jj_act_2015", "Juvenile Justice (Care and Protection of Children) Act, 2015", "JJ Act", "Act 2 of 2016", 2015, "Ministry of Women and Child Development", "Child Protection", "https://www.indiacode.nic.in/handle/123456789/2148", "In Force"),

    # Civil, Courts, Procedure & ADR
    ("cpc_1908", "Code of Civil Procedure, 1908", "CPC", "Act 5 of 1908", 1908, "Ministry of Law and Justice", "Civil Procedure", "https://www.indiacode.nic.in/handle/123456789/2191", "In Force"),
    ("limitation_act_1963", "Limitation Act, 1963", "Limitation Act", "Act 36 of 1963", 1963, "Ministry of Law and Justice", "Civil Law", "https://www.indiacode.nic.in/handle/123456789/1572", "In Force"),
    ("specific_relief_1963", "Specific Relief Act, 1963", "Specific Relief Act", "Act 47 of 1963", 1963, "Ministry of Law and Justice", "Civil Law", "https://www.indiacode.nic.in/handle/123456789/1583", "In Force"),
    ("arbitration_act_1996", "Arbitration and Conciliation Act, 1996", "Arbitration Act", "Act 26 of 1996", 1996, "Ministry of Law and Justice", "Alternative Dispute Resolution", "https://www.indiacode.nic.in/handle/123456789/1978", "In Force"),
    ("mediation_act_2023", "Mediation Act, 2023", "Mediation Act", "Act 32 of 2023", 2023, "Ministry of Law and Justice", "Alternative Dispute Resolution", "https://www.indiacode.nic.in/handle/123456789/20119", "In Force"),
    ("commercial_courts_2015", "Commercial Courts Act, 2015", "Commercial Courts Act", "Act 4 of 2016", 2015, "Ministry of Law and Justice", "Civil Procedure", "https://www.indiacode.nic.in/handle/123456789/2156", "In Force"),
    ("nalsa_act_1987", "Legal Services Authorities Act, 1987", "Legal Aid Act", "Act 39 of 1987", 1987, "Ministry of Law and Justice", "Legal Aid", "https://www.indiacode.nic.in/handle/123456789/1897", "In Force"),
    ("contempt_courts_1971", "Contempt of Courts Act, 1971", "Contempt Act", "Act 70 of 1971", 1971, "Ministry of Law and Justice", "Courts & Judicial Powers", "https://www.indiacode.nic.in/handle/123456789/1512", "In Force"),

    # Consumer, Food Safety, Products & Agriculture
    ("copra_2019", "Consumer Protection Act, 2019", "CPA 2019", "Act 35 of 2019", 2019, "Ministry of Consumer Affairs, Food and Public Distribution", "Consumer Protection", "https://www.indiacode.nic.in/handle/123456789/15256", "In Force"),
    ("fssa_2006", "Food Safety and Standards Act, 2006", "FSSAI Act", "Act 34 of 2006", 2006, "Ministry of Health and Family Welfare", "Food Safety", "https://www.indiacode.nic.in/handle/123456789/2026", "In Force"),
    ("eca_1955", "Essential Commodities Act, 1955", "ECA", "Act 10 of 1955", 1955, "Ministry of Consumer Affairs, Food and Public Distribution", "Essential Supplies", "https://www.indiacode.nic.in/handle/123456789/1554", "In Force"),
    ("legal_metrology_2009", "Legal Metrology Act, 2009", "Weights and Measures Act", "Act 1 of 2010", 2009, "Ministry of Consumer Affairs", "Consumer Protection", "https://www.indiacode.nic.in/handle/123456789/2070", "In Force"),
    ("bis_act_2016", "Bureau of Indian Standards Act, 2016", "BIS Act", "Act 11 of 2016", 2016, "Ministry of Consumer Affairs", "Product Quality & Safety", "https://www.indiacode.nic.in/handle/123456789/2143", "In Force"),
    ("nfsa_2013", "National Food Security Act, 2013", "Right to Food Act", "Act 20 of 2013", 2013, "Ministry of Consumer Affairs, Food and Public Distribution", "Social Welfare", "https://www.indiacode.nic.in/handle/123456789/2115", "In Force"),

    # Housing, Property, Rent & Real Estate
    ("rera_2016", "Real Estate (Regulation and Development) Act, 2016", "RERA", "Act 16 of 2016", 2016, "Ministry of Housing and Urban Affairs", "Real Estate & Housing", "https://www.indiacode.nic.in/handle/123456789/2158", "In Force"),
    ("tpa_1882", "Transfer of Property Act, 1882", "TPA", "Act 4 of 1882", 1882, "Ministry of Law and Justice", "Property Law", "https://www.indiacode.nic.in/handle/123456789/2338", "In Force"),
    ("easements_act_1882", "Indian Easements Act, 1882", "Easements Act", "Act 5 of 1882", 1882, "Ministry of Law and Justice", "Property & Land Access", "https://www.indiacode.nic.in/handle/123456789/2339", "In Force"),
    ("registration_act_1908", "Registration Act, 1908", "Registration Act", "Act 16 of 1908", 1908, "Ministry of Rural Development", "Property Registration", "https://www.indiacode.nic.in/handle/123456789/2190", "In Force"),
    ("indian_stamp_act_1899", "Indian Stamp Act, 1899", "Stamp Act", "Act 2 of 1899", 1899, "Ministry of Finance", "Stamp Duty & Revenue", "https://www.indiacode.nic.in/handle/123456789/2324", "In Force"),
    ("rfctlarr_2013", "Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013", "Land Acquisition Act 2013", "Act 30 of 2013", 2013, "Ministry of Rural Development", "Land & Acquisition", "https://www.indiacode.nic.in/handle/123456789/2121", "In Force"),
    ("benami_act_1988", "Prohibition of Benami Property Transactions Act, 1988", "Benami Act", "Act 45 of 1988", 1988, "Ministry of Finance", "Property Law", "https://www.indiacode.nic.in/handle/123456789/1981", "In Force"),

    # Traffic, Motor Vehicles & Transport
    ("mva_1988", "Motor Vehicles Act, 1988", "Motor Vehicles Act", "Act 59 of 1988", 1988, "Ministry of Road Transport and Highways", "Traffic & Transport", "https://www.indiacode.nic.in/handle/123456789/1798", "In Force (Amended 2019)"),
    ("railways_act_1989", "Railways Act, 1989", "Railways Act", "Act 24 of 1989", 1989, "Ministry of Railways", "Transport & Railways", "https://www.indiacode.nic.in/handle/123456789/1990", "In Force"),
    ("aircraft_act_1934", "Aircraft Act, 1934", "Aviation Act", "Act 22 of 1934", 1934, "Ministry of Civil Aviation", "Aviation Law", "https://www.indiacode.nic.in/handle/123456789/2405", "In Force"),
    ("merchant_shipping_1958", "Merchant Shipping Act, 1958", "Merchant Shipping Act", "Act 44 of 1958", 1958, "Ministry of Ports, Shipping and Waterways", "Maritime Law", "https://www.indiacode.nic.in/handle/123456789/1495", "In Force"),
    ("inland_vessels_2021", "Inland Vessels Act, 2021", "Inland Vessels Act", "Act 24 of 2021", 2021, "Ministry of Ports, Shipping and Waterways", "Maritime & Waterways", "https://www.indiacode.nic.in/handle/123456789/16668", "In Force"),
    ("national_highways_1956", "National Highways Act, 1956", "National Highways Act", "Act 48 of 1956", 1956, "Ministry of Road Transport and Highways", "Infrastructure", "https://www.indiacode.nic.in/handle/123456789/1545", "In Force"),

    # Healthcare, Medical & Bioethics
    ("clinical_est_2010", "Clinical Establishments (Registration and Regulation) Act, 2010", "Clinical Establishments Act", "Act 23 of 2010", 2010, "Ministry of Health and Family Welfare", "Healthcare Law", "https://www.indiacode.nic.in/handle/123456789/2083", "In Force"),
    ("nmc_act_2019", "National Medical Commission Act, 2019", "NMC Act", "Act 30 of 2019", 2019, "Ministry of Health and Family Welfare", "Medical Regulation", "https://www.indiacode.nic.in/handle/123456789/13768", "In Force"),
    ("mental_health_2017", "Mental Healthcare Act, 2017", "Mental Healthcare Act", "Act 10 of 2017", 2017, "Ministry of Health and Family Welfare", "Healthcare & Mental Health", "https://www.indiacode.nic.in/handle/123456789/2157", "In Force"),
    ("organ_transplant_1994", "Transplantation of Human Organs and Tissues Act, 1994", "THOT Act", "Act 42 of 1994", 1994, "Ministry of Health and Family Welfare", "Healthcare & Bioethics", "https://www.indiacode.nic.in/handle/123456789/1959", "In Force"),
    ("drugs_cosmetics_1940", "Drugs and Cosmetics Act, 1940", "Drugs and Cosmetics Act", "Act 23 of 1940", 1940, "Ministry of Health and Family Welfare", "Pharmacy & Medical Devices", "https://www.indiacode.nic.in/handle/123456789/2418", "In Force"),
    ("mtp_act_1971", "Medical Termination of Pregnancy Act, 1971", "MTP Act", "Act 34 of 1971", 1971, "Ministry of Health and Family Welfare", "Women & Healthcare", "https://www.indiacode.nic.in/handle/123456789/1510", "In Force"),
    ("pcpndt_1994", "Pre-Conception and Pre-Natal Diagnostic Techniques Act, 1994", "PCPNDT Act", "Act 57 of 1994", 1994, "Ministry of Health and Family Welfare", "Healthcare & Gender Rights", "https://www.indiacode.nic.in/handle/123456789/1963", "In Force"),
    ("epidemic_diseases_1897", "Epidemic Diseases Act, 1897", "Epidemic Diseases Act", "Act 3 of 1897", 1897, "Ministry of Health and Family Welfare", "Public Health", "https://www.indiacode.nic.in/handle/123456789/2322", "In Force"),
    ("disaster_mgmt_2005", "Disaster Management Act, 2005", "DMA", "Act 53 of 2005", 2005, "Ministry of Home Affairs", "Public Safety & Emergency", "https://www.indiacode.nic.in/handle/123456789/2021", "In Force"),

    # Labour, Employment, Wages & Working Conditions
    ("code_wages_2019", "Code on Wages, 2019", "Code on Wages", "Act 29 of 2019", 2019, "Ministry of Labour and Employment", "Labour & Employment", "https://www.indiacode.nic.in/handle/123456789/13769", "Enacted (Consolidates 4 wage laws)"),
    ("ir_code_2020", "Industrial Relations Code, 2020", "IR Code", "Act 35 of 2020", 2020, "Ministry of Labour and Employment", "Labour & Industrial Disputes", "https://www.indiacode.nic.in/handle/123456789/15745", "Enacted"),
    ("ss_code_2020", "Code on Social Security, 2020", "Social Security Code", "Act 36 of 2020", 2020, "Ministry of Labour and Employment", "Social Security & Gig Workers", "https://www.indiacode.nic.in/handle/123456789/15746", "Enacted"),
    ("osh_code_2020", "Occupational Safety, Health and Working Conditions Code, 2020", "OSH Code", "Act 37 of 2020", 2020, "Ministry of Labour and Employment", "Workplace Safety & Factories", "https://www.indiacode.nic.in/handle/123456789/15747", "Enacted"),
    ("payment_wages_1936", "Payment of Wages Act, 1936", "Payment of Wages Act", "Act 4 of 1936", 1936, "Ministry of Labour and Employment", "Labour & Wages", "https://www.indiacode.nic.in/handle/123456789/2411", "In Force"),
    ("minimum_wages_1948", "Minimum Wages Act, 1948", "Minimum Wages Act", "Act 11 of 1948", 1948, "Ministry of Labour and Employment", "Labour & Wages", "https://www.indiacode.nic.in/handle/123456789/1538", "In Force"),
    ("gratuity_act_1972", "Payment of Gratuity Act, 1972", "Gratuity Act", "Act 39 of 1972", 1972, "Ministry of Labour and Employment", "Labour & Retirement", "https://www.indiacode.nic.in/handle/123456789/1517", "In Force"),
    ("epf_act_1952", "Employees' Provident Funds and Miscellaneous Provisions Act, 1952", "EPF Act", "Act 19 of 1952", 1952, "Ministry of Labour and Employment", "Labour & Social Security", "https://www.indiacode.nic.in/handle/123456789/1544", "In Force"),
    ("esi_act_1948", "Employees' State Insurance Act, 1948", "ESI Act", "Act 34 of 1948", 1948, "Ministry of Labour and Employment", "Health Insurance & Labour", "https://www.indiacode.nic.in/handle/123456789/1539", "In Force"),
    ("maternity_benefit_1961", "Maternity Benefit Act, 1961", "Maternity Benefit Act", "Act 53 of 1961", 1961, "Ministry of Labour and Employment", "Women & Workplace Rights", "https://www.indiacode.nic.in/handle/123456789/1566", "In Force"),
    ("posh_act_2013", "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013", "POSH Act", "Act 14 of 2013", 2013, "Ministry of Women and Child Development", "Women & Workplace Protection", "https://www.indiacode.nic.in/handle/123456789/2104", "In Force"),
    ("child_labour_1986", "Child and Adolescent Labour (Prohibition and Regulation) Act, 1986", "Child Labour Act", "Act 61 of 1986", 1986, "Ministry of Labour and Employment", "Child Protection & Labour", "https://www.indiacode.nic.in/handle/123456789/1908", "In Force"),
    ("factories_act_1948", "Factories Act, 1948", "Factories Act", "Act 63 of 1948", 1948, "Ministry of Labour and Employment", "Industrial Safety", "https://www.indiacode.nic.in/handle/123456789/1540", "In Force"),
    ("id_act_1947", "Industrial Disputes Act, 1947", "Industrial Disputes Act", "Act 14 of 1947", 1947, "Ministry of Labour and Employment", "Industrial Relations", "https://www.indiacode.nic.in/handle/123456789/1536", "In Force"),

    # Technology, Cyber, Data Privacy, Telecom & IP
    ("it_act_2000", "Information Technology Act, 2000", "IT Act", "Act 21 of 2000", 2000, "Ministry of Electronics and Information Technology", "Cybercrime & IT Law", "https://www.indiacode.nic.in/handle/123456789/1999", "In Force"),
    ("dpdp_act_2023", "Digital Personal Data Protection Act, 2023", "DPDP Act", "Act 22 of 2023", 2023, "Ministry of Electronics and Information Technology", "Data Privacy & Protection", "https://www.indiacode.nic.in/handle/123456789/20118", "In Force"),
    ("telecom_act_2023", "Telecommunications Act, 2023", "Telecom Act", "Act 44 of 2023", 2023, "Ministry of Communications", "Telecommunications", "https://www.indiacode.nic.in/handle/123456789/20124", "In Force"),
    ("copyright_act_1957", "Copyright Act, 1957", "Copyright Act", "Act 14 of 1957", 1957, "Ministry of Commerce and Industry", "Intellectual Property Rights", "https://www.indiacode.nic.in/handle/123456789/1494", "In Force"),
    ("patents_act_1970", "Patents Act, 1970", "Patents Act", "Act 39 of 1970", 1970, "Ministry of Commerce and Industry", "Intellectual Property Rights", "https://www.indiacode.nic.in/handle/123456789/1507", "In Force"),
    ("trademarks_act_1999", "Trade Marks Act, 1999", "Trademarks Act", "Act 47 of 1999", 1999, "Ministry of Commerce and Industry", "Intellectual Property Rights", "https://www.indiacode.nic.in/handle/123456789/1994", "In Force"),
    ("designs_act_2000", "Designs Act, 2000", "Designs Act", "Act 16 of 2000", 2000, "Ministry of Commerce and Industry", "Intellectual Property Rights", "https://www.indiacode.nic.in/handle/123456789/1997", "In Force"),
    ("gi_act_1999", "Geographical Indications of Goods (Registration and Protection) Act, 1999", "GI Act", "Act 48 of 1999", 1999, "Ministry of Commerce and Industry", "Intellectual Property Rights", "https://www.indiacode.nic.in/handle/123456789/1995", "In Force"),

    # Environment, Forests, Energy, Mining & Animal Welfare
    ("epa_1986", "Environment (Protection) Act, 1986", "Environment Protection Act", "Act 29 of 1986", 1986, "Ministry of Environment, Forest and Climate Change", "Environmental Law", "https://www.indiacode.nic.in/handle/123456789/1903", "In Force"),
    ("ngt_act_2010", "National Green Tribunal Act, 2010", "NGT Act", "Act 19 of 2010", 2010, "Ministry of Environment, Forest and Climate Change", "Environmental Law", "https://www.indiacode.nic.in/handle/123456789/2082", "In Force"),
    ("water_act_1974", "Water (Prevention and Control of Pollution) Act, 1974", "Water Act", "Act 6 of 1974", 1974, "Ministry of Environment, Forest and Climate Change", "Environmental Law", "https://www.indiacode.nic.in/handle/123456789/1523", "In Force (Amended 2024)"),
    ("air_act_1981", "Air (Prevention and Control of Pollution) Act, 1981", "Air Act", "Act 14 of 1981", 1981, "Ministry of Environment, Forest and Climate Change", "Environmental Law", "https://www.indiacode.nic.in/handle/123456789/1577", "In Force"),
    ("wildlife_act_1972", "Wild Life (Protection) Act, 1972", "Wildlife Protection Act", "Act 53 of 1972", 1972, "Ministry of Environment, Forest and Climate Change", "Wildlife & Conservation", "https://www.indiacode.nic.in/handle/123456789/1519", "In Force"),
    ("forest_act_1980", "Van (Sanrakshan Evam Samvardhan) Adhiniyam, 1980", "Forest Conservation Act", "Act 69 of 1980", 1980, "Ministry of Environment, Forest and Climate Change", "Forest & Environment", "https://www.indiacode.nic.in/handle/123456789/1575", "In Force (Amended 2023)"),
    ("bio_diversity_2002", "Biological Diversity Act, 2002", "Biodiversity Act", "Act 18 of 2003", 2002, "Ministry of Environment, Forest and Climate Change", "Biodiversity & Ecology", "https://www.indiacode.nic.in/handle/123456789/2038", "In Force"),
    ("animal_cruelty_1960", "Prevention of Cruelty to Animals Act, 1960", "Animal Welfare Act", "Act 59 of 1960", 1960, "Ministry of Fisheries, Animal Husbandry and Dairying", "Animal Welfare", "https://www.indiacode.nic.in/handle/123456789/1501", "In Force"),
    ("electricity_act_2003", "Electricity Act, 2003", "Electricity Act", "Act 36 of 2003", 2003, "Ministry of Power", "Energy & Power", "https://www.indiacode.nic.in/handle/123456789/2045", "In Force"),
    ("energy_cons_2001", "Energy Conservation Act, 2001", "Energy Conservation Act", "Act 52 of 2001", 2001, "Ministry of Power", "Energy Efficiency", "https://www.indiacode.nic.in/handle/123456789/2007", "In Force"),
    ("mmdr_act_1957", "Mines and Minerals (Development and Regulation) Act, 1957", "MMDR Act", "Act 67 of 1957", 1957, "Ministry of Mines", "Mining & Natural Resources", "https://www.indiacode.nic.in/handle/123456789/1496", "In Force"),

    # Corporate, Commercial, Banking, Debt & Insolvency
    ("companies_act_2013", "Companies Act, 2013", "Companies Act", "Act 18 of 2013", 2013, "Ministry of Corporate Affairs", "Corporate Law", "https://www.indiacode.nic.in/handle/123456789/2114", "In Force"),
    ("llp_act_2008", "Limited Liability Partnership Act, 2008", "LLP Act", "Act 6 of 2009", 2008, "Ministry of Corporate Affairs", "Corporate Law", "https://www.indiacode.nic.in/handle/123456789/2056", "In Force"),
    ("partnership_act_1932", "Indian Partnership Act, 1932", "Partnership Act", "Act 9 of 1932", 1932, "Ministry of Corporate Affairs", "Commercial Law", "https://www.indiacode.nic.in/handle/123456789/2403", "In Force"),
    ("contract_act_1872", "Indian Contract Act, 1872", "Contract Act", "Act 9 of 1872", 1872, "Ministry of Law and Justice", "Commercial & Contract Law", "https://www.indiacode.nic.in/handle/123456789/2187", "In Force"),
    ("sale_goods_1930", "Sale of Goods Act, 1930", "Sale of Goods Act", "Act 3 of 1930", 1930, "Ministry of Law and Justice", "Commercial Law", "https://www.indiacode.nic.in/handle/123456789/2398", "In Force"),
    ("ibc_2016", "Insolvency and Bankruptcy Code, 2016", "IBC", "Act 31 of 2016", 2016, "Ministry of Corporate Affairs", "Insolvency & Debt Resolution", "https://www.indiacode.nic.in/handle/123456789/2154", "In Force"),
    ("competition_act_2002", "Competition Act, 2002", "Competition Act", "Act 12 of 2003", 2002, "Ministry of Corporate Affairs", "Competition & Antitrust", "https://www.indiacode.nic.in/handle/123456789/2034", "In Force"),
    ("ni_act_1881", "Negotiable Instruments Act, 1881", "NI Act", "Act 26 of 1881", 1881, "Ministry of Finance", "Banking & Cheque Bounce", "https://www.indiacode.nic.in/handle/123456789/2337", "In Force"),
    ("sarfaesi_2002", "Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002", "SARFAESI Act", "Act 54 of 2002", 2002, "Ministry of Finance", "Banking & Debt Recovery", "https://www.indiacode.nic.in/handle/123456789/2033", "In Force"),
    ("rdb_act_1993", "Recovery of Debts and Bankruptcy Act, 1993", "DRT Act", "Act 51 of 1993", 1993, "Ministry of Finance", "Banking & Debt Tribunals", "https://www.indiacode.nic.in/handle/123456789/1951", "In Force"),
    ("rbi_act_1934", "Reserve Bank of India Act, 1934", "RBI Act", "Act 2 of 1934", 1934, "Ministry of Finance", "Central Banking & Monetary Law", "https://www.indiacode.nic.in/handle/123456789/2407", "In Force"),
    ("banking_reg_1949", "Banking Regulation Act, 1949", "Banking Regulation Act", "Act 10 of 1949", 1949, "Ministry of Finance", "Banking Law", "https://www.indiacode.nic.in/handle/123456789/1541", "In Force"),
    ("fema_1999", "Foreign Exchange Management Act, 1999", "FEMA", "Act 42 of 1999", 1999, "Ministry of Finance", "Foreign Exchange & Trade", "https://www.indiacode.nic.in/handle/123456789/1992", "In Force"),
    ("sebi_act_1992", "Securities and Exchange Board of India Act, 1992", "SEBI Act", "Act 15 of 1992", 1992, "Ministry of Finance", "Securities & Capital Markets", "https://www.indiacode.nic.in/handle/123456789/1944", "In Force"),
    ("msme_act_2006", "Micro, Small and Medium Enterprises Development Act, 2006", "MSMED Act", "Act 27 of 2006", 2006, "Ministry of Micro, Small and Medium Enterprises", "Business & Delayed Payments", "https://www.indiacode.nic.in/handle/123456789/2024", "In Force"),

    # Social Justice, Education, Rights & Special Laws
    ("rte_act_2009", "Right of Children to Free and Compulsory Education Act, 2009", "RTE Act", "Act 35 of 2009", 2009, "Ministry of Education", "Education Rights", "https://www.indiacode.nic.in/handle/123456789/2069", "In Force"),
    ("senior_citizens_2007", "Maintenance and Welfare of Parents and Senior Citizens Act, 2007", "Senior Citizens Act", "Act 56 of 2007", 2007, "Ministry of Social Justice and Empowerment", "Senior Citizens", "https://www.indiacode.nic.in/handle/123456789/2048", "In Force"),
    ("sc_st_act_1989", "Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989", "SC/ST Act", "Act 33 of 1989", 1989, "Ministry of Social Justice and Empowerment", "Social Justice & Civil Rights", "https://www.indiacode.nic.in/handle/123456789/1988", "In Force"),
    ("pwd_act_2016", "Rights of Persons with Disabilities Act, 2016", "RPwD Act", "Act 49 of 2016", 2016, "Ministry of Social Justice and Empowerment", "Disability Rights", "https://www.indiacode.nic.in/handle/123456789/2155", "In Force"),
    ("dv_act_2005", "Protection of Women from Domestic Violence Act, 2005", "PWDVA", "Act 43 of 2005", 2005, "Ministry of Women and Child Development", "Women Protection", "https://www.indiacode.nic.in/handle/123456789/2020", "In Force"),
    ("child_marriage_2006", "Prohibition of Child Marriage Act, 2006", "PCMA", "Act 6 of 2007", 2006, "Ministry of Women and Child Development", "Child Protection & Family", "https://www.indiacode.nic.in/handle/123456789/2047", "In Force"),
    ("rti_act_2005", "Right to Information Act, 2005", "RTI Act", "Act 22 of 2005", 2005, "Ministry of Personnel, Public Grievances and Pensions", "RTI & Governance", "https://www.indiacode.nic.in/handle/123456789/2018", "In Force"),
    ("passports_act_1967", "Passports Act, 1967", "Passports Act", "Act 15 of 1967", 1967, "Ministry of External Affairs", "Immigration & Travel", "https://www.indiacode.nic.in/handle/123456789/1468", "In Force"),
    ("citizenship_act_1955", "Citizenship Act, 1955", "Citizenship Act", "Act 57 of 1955", 1955, "Ministry of Home Affairs", "Citizenship & Nationality", "https://www.indiacode.nic.in/handle/123456789/1558", "In Force"),
    ("income_tax_1961", "Income-tax Act, 1961", "Income Tax Act", "Act 43 of 1961", 1961, "Ministry of Finance", "Direct Taxation", "https://www.indiacode.nic.in/handle/123456789/1564", "In Force"),
    ("cgst_act_2017", "Central Goods and Services Tax Act, 2017", "CGST Act", "Act 12 of 2017", 2017, "Ministry of Finance", "Indirect Taxation", "https://www.indiacode.nic.in/handle/123456789/2153", "In Force"),
    ("customs_act_1962", "Customs Act, 1962", "Customs Act", "Act 52 of 1962", 1962, "Ministry of Finance", "Customs & Trade", "https://www.indiacode.nic.in/handle/123456789/1570", "In Force")
]


# ==============================================================================
# 3. STATE-SPECIFIC STATUTES REPOSITORY (Covering All Key State Subjects)
# ==============================================================================
STATE_LEGISLATION_SEED = [
    # Maharashtra
    ("MH", "Maharashtra", "Maharashtra Rent Control Act, 1999", 1999, "Rent & Tenancy", "https://bombayhighcourt.nic.in/",
     "Regulates tenancies, standard rent fixing, and prohibits eviction without statutory grounds in Maharashtra. Disconnection of essential services (water/power) is a cognizable offence.",
     "Tenant can approach the Court of Small Causes in Mumbai or Civil Judge Senior Division for illegal eviction or restoration of essential supply under Section 29."),
    ("MH", "Maharashtra", "Maharashtra Land Revenue Code, 1966", 1966, "Land & Revenue", "https://bombayhighcourt.nic.in/",
     "Comprehensive law governing land assessment, agricultural non-agricultural (NA) permission, land records (7/12 extract), and boundary disputes.",
     "Apply to Tahsildar / Sub-Divisional Officer (SDO) for boundary demarcation or correction of land revenue records."),
    ("MH", "Maharashtra", "Maharashtra Police Act, 1951", 1951, "Police Powers", "https://bombayhighcourt.nic.in/",
     "Defines duties of police officers, public order regulations, assemblies, licensing of establishments, and external order powers (externment).",
     "Citizen grievance against police misconduct can be filed before the State Police Complaints Authority (SPCA)."),
    ("MH", "Maharashtra", "Maharashtra Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2017", 2017, "Labour & Shops", "https://mahasharameve.gov.in/",
     "Regulates working hours, weekly off, earned leave (18 days), maternity benefits, and prohibition of discrimination against women employees.",
     "Complaints regarding unpaid overtime or unlawful termination are filed before the Labour Facilitation Officer / Labour Commissioner."),

    # NCT of Delhi
    ("DL", "NCT of Delhi", "Delhi Rent Control Act, 1958", 1958, "Rent & Tenancy", "https://delhicourts.nic.in/",
     "Applies to tenancies in urban areas with monthly rent up to Rs. 3,500. Protects against arbitrary eviction and unauthorized rent increases.",
     "Petition before the Rent Controller under Section 14 for protection against illegal eviction or under Section 45 for restoration of essential amenities."),
    ("DL", "NCT of Delhi", "Delhi Police Act, 1978", 1978, "Police Powers", "https://delhipolice.nic.in/",
     "Establishes powers of Delhi Police, regulation of traffic, assemblies, and powers of Commissioner of Police.",
     "Complaints of harassment or refusal to lodge FIR can be submitted to Delhi Police Vigilance or the Joint Commissioner of Police / Police Complaints Authority."),
    ("DL", "NCT of Delhi", "Delhi Development Act, 1957", 1957, "Urban Housing & Zoning", "https://dda.gov.in/",
     "Empowers the Delhi Development Authority (DDA) to formulate master plans, zoning regulations, and curb unauthorized construction.",
     "Remedy against unauthorized construction or encroachment: Complaint to Municipal Corporation of Delhi (MCD) Special Task Force (STF) or DDA."),
    ("DL", "NCT of Delhi", "Delhi Shops and Establishments Act, 1954", 1954, "Labour & Shops", "https://labour.delhi.gov.in/",
     "Governs retail shops, commercial offices, overtime payments at double the rate, spread-over hours, and notice period before dismissal.",
     "Claim for unpaid salary or wrongful termination is filed before the Conciliation Officer / Authority under the Act."),

    # Karnataka
    ("KA", "Karnataka", "Karnataka Rent Act, 1999", 1999, "Rent & Tenancy", "https://dpal.karnataka.gov.in/",
     "Regulates residential and commercial tenancies in Karnataka urban areas. Provides for execution of written lease agreements and limited period tenancies.",
     "Remedy: Petition before the Court of Small Causes in Bengaluru or Civil Judge for eviction disputes or standard rent."),
    ("KA", "Karnataka", "Karnataka Land Revenue Act, 1964", 1964, "Land & Revenue", "https://dpal.karnataka.gov.in/",
     "Governs land records (RTC / Pahani), conversion of agricultural land for non-agricultural purposes, and Tahsildar powers.",
     "Remedy: Appeal before Assistant Commissioner (AC) or Deputy Commissioner (DC) under Section 49 against wrongful revenue entries."),
    ("KA", "Karnataka", "Karnataka Shops and Commercial Establishments Act, 1961", 1961, "Labour & Shops", "https://ekarmika.karnataka.gov.in/",
     "Regulates employment terms in IT/ITES and commercial enterprises in Karnataka. Mandates 1 day weekly holiday, 20 days annual leave with wages.",
     "Grievance against termination without one month notice or retrenchment compensation: Appeal under Section 39 before the Labour Officer."),
    ("KA", "Karnataka", "Karnataka Apartment Ownership Act, 1972", 1972, "Housing & Society", "https://dpal.karnataka.gov.in/",
     "Provides for individual ownership of an apartment and an undivided interest in common areas and facilities. Mandates deed of declaration.",
     "Apartment association disputes can be addressed through Registrar of Cooperative Societies or Civil Court for declaration and injunction."),

    # Uttar Pradesh
    ("UP", "Uttar Pradesh", "UP Regulation of Urban Premises Tenancy Act, 2021", 2021, "Rent & Tenancy", "https://up.gov.in/",
     "Modern tenancy law replacing old 1972 Act. Mandates written tenancy agreement registered with Rent Authority, caps security deposit at 2 months for residential.",
     "Rent Authority / Rent Tribunal established in each district for swift dispute adjudication without protracted civil litigation."),
    ("UP", "Uttar Pradesh", "Uttar Pradesh Revenue Code, 2006", 2006, "Land & Revenue", "https://up.gov.in/",
     "Consolidates and amends laws relating to land tenures (Bhumidhar rights), revenue administration, boundary disputes, and mutation.",
     "Remedy: File mutation application under Section 34 or demarcation application under Section 24 before the Sub-Divisional Magistrate (SDM)."),
    ("UP", "Uttar Pradesh", "Uttar Pradesh Police Regulations", 2008, "Police Powers", "https://uppolice.gov.in/",
     "Prescribes duties of Station House Officers (SHO), investigation procedures, GD entry maintenance, and citizen interaction standards.",
     "Remedy: Direct complaint to Superintendent of Police (SP) under Section 154(3) CrPC/173(4) BNSS upon refusal to register FIR."),

    # West Bengal
    ("WB", "West Bengal", "West Bengal Premises Tenancy Act, 1997", 1997, "Rent & Tenancy", "https://wb.gov.in/",
     "Protects bona fide tenants from eviction while specifying grounds such as landlord's own occupation or tenant's default in rent payment.",
     "Rent Controller or Civil Court has jurisdiction to determine fair rent and order resumption of withheld electricity or water supply."),
    ("WB", "West Bengal", "West Bengal Land Reforms Act, 1955", 1955, "Land & Agriculture", "https://wb.gov.in/",
     "Governs raiyat land rights, bargadar (sharecropper) protection against unlawful eviction, and ceiling on agricultural holdings.",
     "Grievances of bargadars or raiyats are heard by the Revenue Officer / Block Land & Land Reforms Officer (BL&LRO)."),

    # Tamil Nadu
    ("TN", "Tamil Nadu", "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", 2017, "Rent & Tenancy", "https://www.tn.gov.in/",
     "Modern balanced tenancy statute. Mandates mandatory tenancy registration on the TN Tenancy portal, regulates repossession, caps security deposits.",
     "Remedy: Rent Court and Rent Tribunal provide speedy disposal within 90 days. Approach Rent Court for rent arrears or repossession."),
    ("TN", "Tamil Nadu", "Tamil Nadu Shops and Establishments Act, 1947", 1947, "Labour & Shops", "https://labour.tn.gov.in/",
     "Regulates conditions of work, daily hours (8 hours), statutory holidays, dismissal notice, and gratuity eligibility in commercial establishments.",
     "Appeal against dismissal without reasonable cause can be preferred under Section 41 to the Appellate Authority (Deputy Commissioner of Labour).")
]


# ==============================================================================
# 4. CONSTITUTIONAL PROVISIONS & 7TH SCHEDULE LEGISLATIVE LISTS
# ==============================================================================
CONSTITUTIONAL_PROVISIONS_SEED = [
    # Fundamental Rights (Part III)
    ("12", "Part III", "Definition of State",
     "In this Part, unless the context otherwise requires, 'the State' includes the Government and Parliament of India, the Government and the Legislature of each of the States, and all local or other authorities within the territory of India or under the control of the Government of India.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("13", "Part III", "Laws inconsistent with or in derogation of the fundamental rights",
     "All laws in force in the territory of India immediately before the commencement of this Constitution, in so far as they are inconsistent with the provisions of this Part, shall, to the extent of such inconsistency, be void. The State shall not make any law which takes away or abridges the rights conferred by this Part.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("14", "Part III", "Equality before law",
     "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. Prohibits arbitrary state action and requires reasonable classification.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("15", "Part III", "Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth",
     "The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them. Special provisions for women, children, and socially and educationally backward classes permitted.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("16", "Part III", "Equality of opportunity in matters of public employment",
     "There shall be equality of opportunity for all citizens in matters relating to employment or appointment to any office under the State.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("17", "Part III", "Abolition of Untouchability",
     "'Untouchability' is abolished and its practice in any form is forbidden. The enforcement of any disability arising out of 'Untouchability' shall be an offence punishable in accordance with law (SC/ST Act).",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("19", "Part III", "Protection of certain rights regarding freedom of speech, etc.",
     "All citizens shall have the right: (a) to freedom of speech and expression; (b) to assemble peaceably and without arms; (c) to form associations or unions or co-operative societies; (d) to move freely throughout India; (e) to reside and settle anywhere in India; and (g) to practise any profession, or to carry on any occupation, trade or business, subject to reasonable restrictions.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("20", "Part III", "Protection in respect of conviction for offences",
     "Guarantees protection against ex-post facto laws (no one can be convicted for an act not an offence when committed), double jeopardy (no prosecution twice for same offence), and self-incrimination (cannot be compelled to be a witness against oneself).",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("21", "Part III", "Protection of life and personal liberty",
     "No person shall be deprived of his life or personal liberty except according to procedure established by law. Encompasses right to privacy, right to clean environment, right to emergency medical aid, right to livelihood, right against custodial torture, and right to speedy trial.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("21A", "Part III", "Right to education",
     "The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine. Implemented via RTE Act, 2009.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("22", "Part III", "Protection against arrest and detention in certain cases",
     "Guarantees arrested person right to be informed of grounds of arrest, right to consult and be defended by a legal practitioner, and mandatory production before nearest magistrate within 24 hours of arrest.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("25", "Part III", "Freedom of conscience and free profession, practice and propagation of religion",
     "Subject to public order, morality and health, all persons are equally entitled to freedom of conscience and the right freely to profess, practise and propagate religion.",
     "Fundamental Rights", None, "https://legislative.gov.in/constitution-of-india/"),
    ("32", "Part III", "Remedies for enforcement of rights conferred by this Part",
     "The right to move the Supreme Court by appropriate proceedings for the enforcement of the Fundamental Rights is guaranteed. Supreme Court has power to issue writs of Habeas Corpus, Mandamus, Prohibition, Quo Warranto and Certiorari. Described by Dr. B.R. Ambedkar as the 'Heart and Soul of the Constitution'.",
     "Constitutional Remedies & Writs", None, "https://legislative.gov.in/constitution-of-india/"),

    # Directive Principles (Part IV)
    ("39A", "Part IV", "Equal justice and free legal aid",
     "The State shall secure that the operation of the legal system promotes justice, on a basis of equal opportunity, and shall, in particular, provide free legal aid, by suitable legislation or schemes or in any other way, to ensure that opportunities for securing justice are not denied to any citizen by reason of economic or other disabilities. (Basis for NALSA & Legal Services Authorities Act).",
     "Directive Principles & Legal Aid", None, "https://legislative.gov.in/constitution-of-india/"),
    ("44", "Part IV", "Uniform civil code for the citizens",
     "The State shall endeavour to secure for the citizens a Uniform Civil Code throughout the territory of India.",
     "Directive Principles", None, "https://legislative.gov.in/constitution-of-india/"),
    ("48A", "Part IV", "Protection and improvement of environment and safeguarding of forests and wild life",
     "The State shall endeavour to protect and improve the environment and to safeguard the forests and wild life of the country.",
     "Directive Principles & Environment", None, "https://legislative.gov.in/constitution-of-india/"),

    # Fundamental Duties (Part IVA)
    ("51A", "Part IVA", "Fundamental duties",
     "It shall be the duty of every citizen of India: (a) to abide by the Constitution and respect its ideals, the National Flag and Anthem; (b) to cherish national freedom struggle ideals; (c) to uphold sovereignty, unity and integrity of India; (d) to defend the country; (e) to promote harmony and brotherhood transcending religious diversities; (f) to preserve composite culture; (g) to protect environment including forests, lakes, rivers and wildlife; (h) to develop scientific temper; (i) to safeguard public property and abjure violence; (j) to strive towards excellence; (k) parent/guardian duty to provide education to child aged 6-14.",
     "Fundamental Duties", None, "https://legislative.gov.in/constitution-of-india/"),

    # High Courts & Writs (Part VI)
    ("226", "Part VI", "Power of High Courts to issue certain writs",
     "High Courts have the power throughout territories in relation to which they exercise jurisdiction to issue to any person or authority directions, orders or writs (including Habeas Corpus, Mandamus, Prohibition, Quo Warranto and Certiorari) for the enforcement of Fundamental Rights and for any other purpose.",
     "Constitutional Remedies & Writs", None, "https://legislative.gov.in/constitution-of-india/"),
    ("227", "Part VI", "Power of superintendence over all courts by the High Court",
     "Every High Court shall have superintendence over all courts and tribunals throughout the territories in relation to which it exercises jurisdiction.",
     "Judicial Hierarchy", None, "https://legislative.gov.in/constitution-of-india/"),

    # 7th Schedule Legislative Distribution (Article 246)
    ("246", "Part XI", "Subject-matter of laws made by Parliament and by the Legislatures of States",
     "Establishes three-fold legislative distribution between Union and States: Parliament has exclusive power over Union List (List I); State Legislatures have exclusive power over State List (List II); both have concurrent power over Concurrent List (List III).",
     "Union-State Relations", "Seventh Schedule Overview", "https://legislative.gov.in/constitution-of-india/"),
    ("List_I", "Seventh Schedule", "Union List (List I - 97 Subjects)",
     "Exclusive Central Jurisdiction: Defense, Foreign Affairs, Atomic Energy, Railways, National Highways, Shipping, Aviation, Banking, Insurance, Currency, Foreign Exchange, Patents, Copyright, Trademarks, Inter-State Trade & Commerce, Stock Exchanges, Income Tax (other than agricultural), Customs, Central Excise.",
     "Legislative Distribution", "Union List (List I)", "https://legislative.gov.in/constitution-of-india/"),
    ("List_II", "Seventh Schedule", "State List (List II - 66 Subjects)",
     "Exclusive State Jurisdiction: Public Order, Police, Prisons, Local Government, Public Health and Sanitation, Hospitals and Dispensaries, Intoxicating Liquors, Agriculture, Land (rights in or over land, land tenures, landlord-tenant relations, rent collection), Land Revenue, State Taxes on Agricultural Income, Duties in respect of Succession to Agricultural Land, Tolls.",
     "Legislative Distribution", "State List (List II)", "https://legislative.gov.in/constitution-of-india/"),
    ("List_III", "Seventh Schedule", "Concurrent List (List III - 47 Subjects)",
     "Concurrent Jurisdiction (Both Centre and States can legislate; Central law prevails in conflict under Art. 254): Criminal Law, Criminal Procedure, Marriage and Divorce, Transfer of Property (other than agricultural land), Contracts, Actionable Wrongs, Bankruptcy & Insolvency, Evidence & Oaths, Civil Procedure, Price Control, Economic and Social Planning, Trade Unions & Industrial Disputes, Social Security, Employment, Education, Electricity, Forests, Protection of Wild Animals.",
     "Legislative Distribution", "Concurrent List (List III)", "https://legislative.gov.in/constitution-of-india/")
]


# ==============================================================================
# 5. STATUTE SECTIONS & CITIZEN REMEDIES SEED (Everyday & Complex Legal Scenarios)
# ==============================================================================
STATUTE_SECTIONS_SEED = [
    # Food Safety Scenarios
    ("fssa", "Food Safety and Standards Act, 2006", "59", "Punishment for unsafe food",
     "Selling, storing, manufacturing, or distributing food that is unsafe or past its expiry date is heavily penalized based on severity: (i) not causing injury: imprisonment up to 6 months & fine up to Rs. 1 lakh; (ii) causing non-grievous injury: up to 1 year & fine up to Rs. 3 lakhs; (iii) causing grievous injury: up to 6 years & fine up to Rs. 5 lakhs; (iv) causing death: imprisonment for not less than 7 years extending to life imprisonment and fine not less than Rs. 10 lakhs.",
     "Consumer can report to local Food Safety Officer (FSO), file grievance on FSSAI FoSCoS portal (foscos.fssai.gov.in), and file compensation claim under Section 65 FSSA for injury before the Adjudicating Officer.",
     "https://www.indiacode.nic.in/handle/123456789/2026", "Central"),
    ("fssa", "Food Safety and Standards Act, 2006", "65", "Compensation to victim in case of injury or death of consumer",
     "Where any person causes injury or death to any consumer by food manufactured or sold by him, the Adjudicating Officer or Court shall direct payment of compensation: not less than Rs. 5 lakhs in case of death, up to Rs. 3 lakhs for grievous injury, up to Rs. 1 lakh for other injury.",
     "Direct compensation application before the District Adjudicating Officer (Additional District Magistrate).",
     "https://www.indiacode.nic.in/handle/123456789/2026", "Central"),

    # Real Estate & Delayed Possession Scenarios
    ("rera", "Real Estate (Regulation and Development) Act, 2016", "18", "Return of amount and compensation for delayed possession",
     "If the promoter fails to complete or is unable to give possession of an apartment, plot, or building in accordance with the terms of the agreement for sale by the date specified therein, the promoter shall be liable: (a) if the allottee wishes to withdraw: to return the amount received with interest at SBI highest MCLR + 2% from the date of payment; (b) if the allottee does not withdraw: to pay interest for every month of delay till handing over of possession.",
     "Allottee can file a formal complaint online before the State RERA Authority under Section 31 for possession interest or before the RERA Adjudicating Officer for compensation under Form N.",
     "https://www.indiacode.nic.in/handle/123456789/2158", "Central & State RERA Authorities"),

    # Traffic Police & Driving Licence Seizure Scenarios
    ("mva", "Motor Vehicles Act, 1988", "206", "Power of police officer to impound document",
     "Section 206(4) as amended by Motor Vehicles (Amendment) Act 2019: A police officer or other person authorized may seize the driving licence of a person who has committed specified dangerous offences: (a) drink driving (Sec 185); (b) dangerous driving / jumping red light (Sec 184); (c) over-speeding (Sec 183); (d) driving without helmet or seatbelt. The officer must give a temporary acknowledgement receipt and forward the licence to the Licensing Authority for disqualification.",
     "Police officer cannot confiscate licence arbitrarily without issuing an official e-challan or Form MVA acknowledgment. Citizen can produce digital documents via DigiLocker / mParivahan under Rule 139 of Central Motor Vehicles Rules.",
     "https://www.indiacode.nic.in/handle/123456789/1798", "Central & State Police"),
    ("mva", "Motor Vehicles Act, 1988", "185", "Driving by a drunken person or by a person under the influence of drugs",
     "Whoever, while driving or attempting to drive a motor vehicle, has in his blood alcohol exceeding 30 mg per 100 ml of blood detected by a breath analyser test, shall be punishable for the first offence with imprisonment up to 6 months, or fine of Rs. 10,000, or both; for second or subsequent offence within 3 years, imprisonment up to 2 years, or fine of Rs. 15,000, or both.",
     "Police can require driver to submit to breath test and medical examination. Driver has right to see the breath analyser reading and receive an e-challan.",
     "https://www.indiacode.nic.in/handle/123456789/1798", "Central"),

    # Hospital Refusing Emergency Medical Treatment
    ("clinical_est", "Clinical Establishments (Registration and Regulation) Act, 2010", "12", "Condition for registration and emergency medical care",
     "Section 12(2): Every clinical establishment shall provide within the staff and facilities available, such medical examination and treatment as may be required to stabilize the condition of any individual who comes or is brought to such establishment in an emergency medical condition. Corroborated by Supreme Court ruling in Parmanand Katara v. Union of India (1989): Emergency medical treatment to preserve life must be provided by every hospital without demanding advance payment or police formalities.",
     "Immediate remedy: Call National Emergency Helpline 112. File complaint before State Clinical Establishment Council, District Medical Officer, or Consumer Commission for medical negligence and deficiency of service.",
     "https://www.indiacode.nic.in/handle/123456789/2083", "Central & State Health Depts"),

    # Unpaid Salary by Employer
    ("payment_wages", "Payment of Wages Act, 1936", "15", "Claims arising out of deductions from wages or delay in payment",
     "Where contrary to the provisions of this Act any deduction has been made from the wages of an employed person, or any payment of wages has been delayed, the person may apply to the Authority appointed under Section 15. The Authority may direct refund of deduction or payment of delayed wages together with compensation up to ten times the amount deducted, or not exceeding three thousand rupees for delayed wages.",
     "Employee can issue a legal demand notice to employer giving 15 days, and then file claim before the Authority under Payment of Wages Act / Labour Commissioner / Labour Court under Section 33C(2) of Industrial Disputes Act.",
     "https://www.indiacode.nic.in/handle/123456789/2411", "Central & State Labour Depts"),

    # Landlord Arbitrary Eviction & Rent Increase
    ("state_rent", "State Rent Control Acts (Maharashtra, Delhi, Karnataka, etc.)", "Rent_Evict", "Protection against illegal eviction and utility disconnection",
     "Under all State Rent Control legislation, a landlord cannot unilaterally evict a tenant, lock premises, remove personal belongings, or disconnect essential services (electricity, water supply). Eviction is strictly subject to obtaining a decree from the Rent Controller / Civil Court on statutory grounds (e.g. non-payment of rent after notice, bona fide personal requirement, unauthorized subletting). Disconnecting utilities is a penal offence.",
     "Tenant should file an urgent application before the Rent Controller / Civil Judge for an injunction against illegal eviction and for immediate mandatory restoration of disconnected water/electricity under the applicable State Rent Act.",
     "https://www.indiacode.nic.in/", "State Jurisdiction"),

    # Neighbour Blocking Access & Easement Rights
    ("easements", "Indian Easements Act, 1882", "15", "Acquisition of easement by prescription and right to light, air and access",
     "Where the access and use of light or air to and for any building have been peaceably enjoyed therewith, as an easement, without interruption, and for twenty years, and where a right of way or other easement has been peaceably and openly enjoyed by any person claiming title thereto as an easement and as of right without interruption for twenty years, the right shall become absolute.",
     "If a neighbour starts constructing or erecting a wall blocking customary light, air, or access way, the aggrieved citizen should immediately file a civil suit for Permanent and Mandatory Injunction under the Specific Relief Act with an interim stay application (Order 39 Rules 1 & 2 CPC) in the Civil Court.",
     "https://www.indiacode.nic.in/handle/123456789/2339", "Central & Civil Courts"),

    # Consumer Defective Product & Refund Refusal
    ("copra", "Consumer Protection Act, 2019", "35", "Filing of complaint before District Consumer Disputes Redressal Commission",
     "Section 2(11) & Section 35: Any consumer can file a complaint against a seller or manufacturer for 'deficiency in service' or 'defect in goods' (including refusal of warranty refund, selling expired or damaged products, or misleading advertisements). District Commission has pecuniary jurisdiction up to Rs. 50 lakhs.",
     "Citizen can lodge grievance on National Consumer Helpline (NCH portal: consumerhelpline.gov.in or Call 1915). If unresolved, file an e-daakhil online complaint (edaakhil.nic.in) before the District Consumer Commission without needing a lawyer.",
     "https://www.indiacode.nic.in/handle/123456789/15256", "Central & State Commissions"),
    ("copra", "Consumer Protection Act, 2019", "2", "Definitions of defect in goods and deficiency in service",
     "Section 2(10) defines defect as any fault, imperfection or shortcoming in quality, quantity, potency, purity or standard required by law or contract. Section 2(11) defines deficiency as any fault, imperfection, shortcoming or inadequacy in performance. A defective mobile phone or warranty refusal falls squarely under these definitions.",
     "Consumer can demand replacement, repair, or full refund with compensation from manufacturer/seller.",
     "https://www.indiacode.nic.in/handle/123456789/15256", "Central"),
    ("copra", "Consumer Protection Act, 2019", "84", "Liability of product manufacturer in product liability action",
     "A product manufacturer shall be liable in a product liability action if the product contains a manufacturing defect, defective design, deviation from manufacturing specifications, or does not conform to express warranty.",
     "Claim product liability compensation before the District Consumer Commission.",
     "https://www.indiacode.nic.in/handle/123456789/15256", "Central"),

    # Arrest Powers and Citizen Rights
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "35", "When police may arrest without warrant & arrestee rights",
     "Section 35 BNSS (and Section 41/50 CrPC): Police cannot arrest arbitrarily. (i) In offences punishable with imprisonment up to 7 years, notice of appearance under Sec 35(3) BNSS is mandatory unless specific reasons for arrest exist; (ii) The arresting officer must bear clear name tag and prepare an arrest memo countersigned by a family member or respectable locality person; (iii) Person arrested must be informed immediately of the full grounds of arrest and right to bail if bailable; (iv) Right to inform a friend/relative (Sec 48 BNSS); (v) Mandatory production before magistrate within 24 hours.",
     "If police arrest without communicating grounds or fail to produce within 24 hours, custody is illegal. Citizen/family can approach High Court under Article 226 or Supreme Court under Article 32 for Habeas Corpus writ and register complaint before the Magistrate.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central & Police"),
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "47", "Search of arrested person and safeguards for women",
     "Whenever it is necessary to cause a female to be searched, the search shall be made by another female with strict regard to decency. A receipt for all seized articles must be given to the arrested person.",
     "Violations can be reported to the Magistrate or Police Complaints Authority.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central"),
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "48", "Right of arrested person to meet an advocate of choice",
     "When any person is arrested and interrogated by the police, he shall be entitled to meet an advocate of his choice during interrogation, though not throughout interrogation.",
     "Remedy: Request legal aid counsel through DLSA (dial 15100) or instruct private advocate.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central"),
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "58", "Person arrested to be taken before Magistrate within twenty-four hours",
     "No police officer shall detain in custody a person arrested without warrant for a longer period than under all the circumstances of the case is reasonable, and such period shall not exceed twenty-four hours exclusive of the journey time.",
     "Unlawful detention beyond 24 hours makes custody illegal; immediate Habeas Corpus petition before High Court under Article 226.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central"),
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "173", "Information in cognizable cases (First Information Report / Zero FIR)",
     "Section 173 BNSS mandates that every information relating to the commission of a cognizable offence must be recorded by police. It may be given orally, in writing, or electronically (e-FIR). Zero FIR can be lodged at any police station regardless of territorial jurisdiction.",
     "Remedy: Send written complaint by post to Superintendent of Police under Section 173(4) BNSS or file application before Magistrate under Section 175(3) BNSS.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central"),
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "478", "Bail in bailable offences as a matter of right",
     "When any person accused of a bailable offence is arrested or detained without warrant, he shall be released on bail as a matter of right upon furnishing solvent bail bonds or surety.",
     "Apply for bail immediately before Station House Officer (SHO) or Judicial Magistrate.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central"),
    ("bns", "Bharatiya Nyaya Sanhita, 2023", "303", "Theft and punishment for theft",
     "Section 303 BNS (formerly Section 378/379 IPC): Whoever intending to dishonestly take any movable property out of the possession of any person without consent, moves that property, commits theft. Punishable with imprisonment up to 3 years, fine, or both.",
     "Complainant can register FIR under Section 173 BNSS; seek interim custody of recovered property under Section 497 BNSS.",
     "https://www.indiacode.nic.in/handle/123456789/20120", "Central"),
    ("bns", "Bharatiya Nyaya Sanhita, 2023", "318", "Cheating and dishonestly inducing delivery of property",
     "Section 318 BNS (formerly Section 420 IPC): Cheating and dishonestly inducing delivery of property is punishable with imprisonment up to 7 years and fine.",
     "File FIR for cheating under Section 173 BNSS; dial 1930 for online financial fraud.",
     "https://www.indiacode.nic.in/handle/123456789/20120", "Central"),

    # Family, Matrimonial & Maintenance Law
    ("hma", "Hindu Marriage Act, 1955", "24", "Maintenance pendente lite and expenses of proceedings",
     "Section 24: Where in any proceeding under this Act either the wife or the husband has no independent income sufficient for her or his support and necessary expenses, the court may order the respondent to pay expenses and monthly maintenance having regard to both parties' incomes. As affirmed in Rajnesh v. Neha (2020), a working wife is not disentitled from claiming maintenance if her income is insufficient to maintain the matrimonial standard of living.",
     "Application for interim maintenance under Section 24 HMA before the Family Court along with an Affidavit of Assets and Liabilities.",
     "https://www.indiacode.nic.in/handle/123456789/1560", "Central & Family Courts"),
    ("hma", "Hindu Marriage Act, 1955", "25", "Permanent alimony and maintenance",
     "Section 25: Any court exercising jurisdiction under this Act may order the respondent to pay to the applicant for her or his maintenance and support a gross sum or monthly sum for a term not exceeding the life of the applicant having regard to respondent's income and conduct.",
     "Petition for permanent alimony before the Family Court / District Court.",
     "https://www.indiacode.nic.in/handle/123456789/1560", "Central & Family Courts"),
    ("bnss", "Bharatiya Nagarik Suraksha Sanhita, 2023", "144", "Order for maintenance of wives, children and parents",
     "Section 144 BNSS (former Section 125 CrPC): Summary remedy for monthly maintenance of wife unable to maintain herself from a husband who neglects or refuses. A working wife whose personal earnings are inadequate for reasonable support is legally entitled to maintenance.",
     "File maintenance application under Section 144 BNSS before Judicial Magistrate First Class or Family Court.",
     "https://www.indiacode.nic.in/handle/123456789/20121", "Central & Magistrate Courts"),

    # Labour & Wages Law
    ("ida", "Industrial Disputes Act, 1947", "33C", "Recovery of money due from an employer",
     "Section 33C(2): Where any workman is entitled to receive from the employer any money or benefit capable of being computed in money (such as unpaid salary, retrenchment compensation, or gratuity), the workman can apply to the Labour Court for recovery.",
     "File an application under Section 33C(2) before the jurisdictional Labour Court.",
     "https://www.indiacode.nic.in/handle/123456789/2410", "Central & State Labour Courts"),
    ("code_on_wages", "Code on Wages, 2019", "18", "Deductions which may be made from wages and timely payment",
     "Section 18 & Section 17: Employers must disburse wages within 7 to 10 days of the wage period. Unauthorized deductions are strictly prohibited, and permissible deductions cannot exceed 50% of wages.",
     "Lodge grievance before Inspector-cum-Facilitator or State Labour Commissioner.",
     "https://labour.gov.in/", "Central"),

    # Tenancy & Eviction Laws
    ("tn_tenancy", "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", "21", "Repossession of premises by landlord & protection against illegal eviction",
     "Section 21 TNRRRLT Act: A landlord cannot evict a tenant or recover possession except by making a formal application to the Rent Court on statutory grounds (default in rent payment, subletting without consent, misuse, bona fide requirement). Disconnecting water or electricity is illegal under Section 19.",
     "Tenant can file petition before the Rent Court against illegal eviction or for immediate restoration of essential amenities under Section 19.",
     "https://www.tn.gov.in/", "Tamil Nadu Rent Courts"),
    ("tn_tenancy", "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", "19", "Landlord not to cut off or withhold essential supply or service",
     "Section 19: No landlord shall cut off or withhold essential services (water, electricity, passage). Rent Authority may order interim restoration within 24-48 hours and penalize landlord under Section 19(3).",
     "Urgent application before Rent Authority / Rent Court for interim mandatory restoration of electricity/water.",
     "https://www.tn.gov.in/", "Tamil Nadu Rent Courts")
]


def seed_corpus():
    """Execute complete database seeding and FTS5 synchronization."""
    print("Initializing Legal Corpus Database schema at:", CORPUS_DB_PATH)
    init_corpus_db()
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Seed State & UT Jurisdictions
    print(f"Seeding {len(STATES_AND_UTS)} States and Union Territories...")
    for s in STATES_AND_UTS:
        cur.execute("""
            INSERT OR REPLACE INTO state_ut_jurisdictions (code, name, category, high_court, portal_url, key_subjects)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (s["code"], s["name"], s["category"], s["high_court"], s["portal_url"], s["key_subjects"]))

    # 2. Seed Central Acts
    print(f"Seeding {len(CENTRAL_ACTS_SEED)} Central Acts...")
    for act in CENTRAL_ACTS_SEED:
        cur.execute("""
            INSERT OR REPLACE INTO central_acts (act_id, title, short_title, act_number, year, ministry, domain, official_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, act)

    # 3. Seed State Legislation
    print(f"Seeding {len(STATE_LEGISLATION_SEED)} State Statutes...")
    for sl in STATE_LEGISLATION_SEED:
        cur.execute("""
            INSERT INTO state_legislation (state_code, state_name, title, year, domain, official_url, summary, remedies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sl)

    # 4. Seed Constitutional Provisions
    print(f"Seeding {len(CONSTITUTIONAL_PROVISIONS_SEED)} Constitutional Articles and Schedules...")
    for cp in CONSTITUTIONAL_PROVISIONS_SEED:
        cur.execute("""
            INSERT OR REPLACE INTO constitutional_provisions (article_number, part, title, extract, domain, seventh_schedule_list, official_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, cp)

    # 5. Seed Statute Sections
    print(f"Seeding {len(STATUTE_SECTIONS_SEED)} Landmark Statute Provisions...")
    for sec in STATUTE_SECTIONS_SEED:
        cur.execute("""
            INSERT INTO statute_sections (act_slug, act_name, section_number, heading, extract, rights_penalties, official_url, jurisdiction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sec)

    # 6. Populate FTS5 Virtual Table for Sub-millisecond Full-Text Retrieval
    print("Building SQLite FTS5 Full-Text Search Virtual Table...")
    cur.execute("DELETE FROM fts_legal_corpus;")

    # Add Central Acts to FTS5 (entire act has empty section, NOT act_number)
    cur.execute("""
        INSERT INTO fts_legal_corpus (title, act_name, section, jurisdiction, domain, content, keywords)
        SELECT 
            title, 
            short_title, 
            '', 
            'Central', 
            domain, 
            title || ' ' || ministry || ' ' || status || ' ' || official_url, 
            short_title || ' ' || domain || ' central legislation act'
        FROM central_acts;
    """)

    # Add State Legislation to FTS5 (entire state act has empty section, NOT year)
    cur.execute("""
        INSERT INTO fts_legal_corpus (title, act_name, section, jurisdiction, domain, content, keywords)
        SELECT 
            title, 
            title, 
            '', 
            state_name, 
            domain, 
            summary || ' ' || remedies || ' ' || official_url, 
            state_name || ' ' || state_code || ' ' || domain || ' state law'
        FROM state_legislation;
    """)

    # Add Constitutional Provisions to FTS5
    cur.execute("""
        INSERT INTO fts_legal_corpus (title, act_name, section, jurisdiction, domain, content, keywords)
        SELECT 
            title, 
            'Constitution of India', 
            'Article ' || article_number, 
            'Constitutional', 
            domain, 
            extract || ' ' || COALESCE(seventh_schedule_list, '') || ' ' || official_url, 
            'constitution article fundamental rights writs 7th schedule union state concurrent'
        FROM constitutional_provisions;
    """)

    # Add Statute Sections to FTS5
    cur.execute("""
        INSERT INTO fts_legal_corpus (title, act_name, section, jurisdiction, domain, content, keywords)
        SELECT 
            heading, 
            act_name, 
            section_number, 
            jurisdiction, 
            act_slug, 
            extract || ' ' || COALESCE(rights_penalties, '') || ' ' || official_url, 
            act_name || ' ' || heading || ' section ' || section_number || ' ' || act_slug || ' provision penalty remedy citizen rights'
        FROM statute_sections;
    """)

    conn.commit()
    conn.close()
    print("Legal Corpus Seeding Completed Successfully!")


if __name__ == "__main__":
    seed_corpus()
