"""
LegalEase - Central Statutory Provisions & Acts Repository.
File: models/statutory_provisions.py

Authoritative directory of 35+ major central Indian Acts and over 120 verified statutory provisions.
Maintains full transition awareness between repealed codes (IPC, CrPC, IEA) and modern codes (BNS, BNSS, BSA).
References official government digital repositories (India Code, Supreme Court of India, eCourts).
"""

# Supported central Act identifiers and their official legislative details
SUPPORTED_ACTS = {
    "bns": {
        "name": "Bharatiya Nyaya Sanhita, 2023",
        "status": "Current Legislation (In force from July 1, 2024)",
        "replaced_law": "Indian Penal Code, 1860 (IPC)",
        "source_url": "https://www.indiacode.nic.in/"
    },
    "ipc": {
        "name": "Indian Penal Code, 1860",
        "status": "Repealed Legislation (Replaced by Bharatiya Nyaya Sanhita, 2023)",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "bnss": {
        "name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "status": "Current Legislation (In force from July 1, 2024)",
        "replaced_law": "Code of Criminal Procedure, 1973 (CrPC)",
        "source_url": "https://www.indiacode.nic.in/"
    },
    "crpc": {
        "name": "Code of Criminal Procedure, 1973",
        "status": "Repealed Legislation (Replaced by Bharatiya Nagarik Suraksha Sanhita, 2023)",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "bsa": {
        "name": "Bharatiya Sakshya Adhiniyam, 2023",
        "status": "Current Legislation (In force from July 1, 2024)",
        "replaced_law": "Indian Evidence Act, 1872 (IEA)",
        "source_url": "https://www.indiacode.nic.in/"
    },
    "iea": {
        "name": "Indian Evidence Act, 1872",
        "status": "Repealed Legislation (Replaced by Bharatiya Sakshya Adhiniyam, 2023)",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "cpc": {
        "name": "Code of Civil Procedure, 1908",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "constitution": {
        "name": "Constitution of India, 1950",
        "status": "Supreme Law of India",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "contract_act": {
        "name": "Indian Contract Act, 1872",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "cpa": {
        "name": "Consumer Protection Act, 2019",
        "status": "Current Legislation",
        "replaced_law": "Consumer Protection Act, 1986",
        "source_url": "https://consumerhelpline.gov.in/"
    },
    "it_act": {
        "name": "Information Technology Act, 2000",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "dpdp": {
        "name": "Digital Personal Data Protection Act, 2023",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.meity.gov.in/"
    },
    "dv_act": {
        "name": "Protection of Women from Domestic Violence Act, 2005",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "posh": {
        "name": "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://wcd.nic.in/"
    },
    "maternity_benefit": {
        "name": "Maternity Benefit Act, 1961",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://labour.gov.in/"
    },
    "hma": {
        "name": "Hindu Marriage Act, 1955",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "sma": {
        "name": "Special Marriage Act, 1954",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "hsa": {
        "name": "Hindu Succession Act, 1956",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "tpa": {
        "name": "Transfer of Property Act, 1882",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "model_tenancy": {
        "name": "Model Tenancy Act, 2021",
        "status": "Framework Legislation (Adopted by States)",
        "replaced_law": None,
        "source_url": "https://mohua.gov.in/"
    },
    "code_on_wages": {
        "name": "Code on Wages, 2019",
        "status": "Current Central Labour Code",
        "replaced_law": "Payment of Wages Act 1936, Minimum Wages Act 1948",
        "source_url": "https://labour.gov.in/"
    },
    "ida": {
        "name": "Industrial Disputes Act, 1947",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://labour.gov.in/"
    },
    "sarfaesi": {
        "name": "Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "rbi_act": {
        "name": "Reserve Bank of India Act, 1934",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.rbi.org.in/"
    },
    "mv_act": {
        "name": "Motor Vehicles Act, 1988 (Amended 2019)",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://parivahan.gov.in/"
    },
    "copyright_act": {
        "name": "Copyright Act, 1957",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://copyright.gov.in/"
    },
    "patents_act": {
        "name": "Patents Act, 1970",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://ipindia.gov.in/"
    },
    "trademarks_act": {
        "name": "Trade Marks Act, 1999",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://ipindia.gov.in/"
    },
    "rti": {
        "name": "Right to Information Act, 2005",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://rtionline.gov.in/"
    },
    "admin_tribunals": {
        "name": "Administrative Tribunals Act, 1985",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://cgat.gov.in/"
    },
    "epa": {
        "name": "Environment (Protection) Act, 1986",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://moef.gov.in/"
    },
    "ngt_act": {
        "name": "National Green Tribunal Act, 2010",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://greentribunal.gov.in/"
    },
    "rte": {
        "name": "Right of Children to Free and Compulsory Education Act, 2009",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.education.gov.in/"
    },
    "clinical_establishments": {
        "name": "Clinical Establishments (Registration and Regulation) Act, 2010",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://clinicalestablishments.gov.in/"
    },
    "senior_citizens_act": {
        "name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://socialjustice.gov.in/"
    },
    "pocso": {
        "name": "Protection of Children from Sexual Offences Act, 2012",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://ncpcr.gov.in/"
    },
    "jj_act": {
        "name": "Juvenile Justice (Care and Protection of Children) Act, 2015",
        "status": "Current Legislation",
        "replaced_law": "Juvenile Justice Act, 2000",
        "source_url": "https://ncpcr.gov.in/"
    },
    "sc_st_act": {
        "name": "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://socialjustice.gov.in/"
    },
    "poca": {
        "name": "Prevention of Corruption Act, 1988",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://cvc.gov.in/"
    },
    "ni_act": {
        "name": "Negotiable Instruments Act, 1881",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/"
    },
    "companies_act": {
        "name": "Companies Act, 2013",
        "status": "Current Legislation",
        "replaced_law": "Companies Act, 1956",
        "source_url": "https://www.mca.gov.in/"
    },
    "llp_act": {
        "name": "Limited Liability Partnership Act, 2008",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.mca.gov.in/"
    },
    "it_tax_act": {
        "name": "Income-tax Act, 1961",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://www.incometax.gov.in/"
    },
    "cgst_act": {
        "name": "Central Goods and Services Tax Act, 2017",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://cbic.gov.in/"
    },
    "citizenship_act": {
        "name": "Citizenship Act, 1955",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://mha.gov.in/"
    },
    "passports_act": {
        "name": "Passports Act, 1967",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://passportindia.gov.in/"
    },
    "arbitration_act": {
        "name": "Arbitration and Conciliation Act, 1996",
        "status": "Current Legislation",
        "replaced_law": "Arbitration Act, 1940",
        "source_url": "https://www.indiacode.nic.in/"
    },
    "mediation_act": {
        "name": "Mediation Act, 2023",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://lawmin.gov.in/"
    },
    "lsaa": {
        "name": "Legal Services Authorities Act, 1987",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://nalsa.gov.in/"
    },
    "rera": {
        "name": "Real Estate (Regulation and Development) Act, 2016",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://mohua.gov.in/"
    },
    "ibc": {
        "name": "Insolvency and Bankruptcy Code, 2016",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://ibbi.gov.in/"
    },
    "pmla": {
        "name": "Prevention of Money Laundering Act, 2002",
        "status": "Current Legislation",
        "replaced_law": None,
        "source_url": "https://enforcementdirectorate.gov.in/"
    },
    "payment_wages": {
        "name": "Payment of Wages Act, 1936",
        "status": "Current Legislation (In Force)",
        "replaced_law": "Transitional enforcement alongside Code on Wages, 2019",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2411"
    },
    "fssa": {
        "name": "Food Safety and Standards Act, 2006",
        "status": "Current Legislation (In Force)",
        "replaced_law": "Prevention of Food Adulteration Act, 1954",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2026"
    },
    "easements": {
        "name": "Indian Easements Act, 1882",
        "status": "Current Legislation (In Force)",
        "replaced_law": None,
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2339"
    },
    "tn_tenancy": {
        "name": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
        "status": "State Legislation (In Force)",
        "replaced_law": "Tamil Nadu Buildings (Lease and Rent Control) Act, 1960",
        "source_url": "https://www.tn.gov.in/"
    },
    "delhi_rent": {
        "name": "Delhi Rent Control Act, 1958",
        "status": "State Legislation (In Force)",
        "replaced_law": None,
        "source_url": "https://delhicourts.nic.in/"
    },
    "mh_rent": {
        "name": "Maharashtra Rent Control Act, 1999",
        "status": "State Legislation (In Force)",
        "replaced_law": "Bombay Rents, Hotel and Lodging House Rates Control Act, 1947",
        "source_url": "https://bombayhighcourt.nic.in/"
    }
}

# Convenient aliases for flexible multi-domain resolution
SUPPORTED_ACTS["trademark_act"] = SUPPORTED_ACTS["trademarks_act"]
SUPPORTED_ACTS["senior_citizens"] = SUPPORTED_ACTS["senior_citizens_act"]
SUPPORTED_ACTS["rti_act"] = SUPPORTED_ACTS["rti"]
SUPPORTED_ACTS["rte_act"] = SUPPORTED_ACTS["rte"]
SUPPORTED_ACTS["clinical_est"] = SUPPORTED_ACTS["clinical_establishments"]
SUPPORTED_ACTS["pwdva"] = SUPPORTED_ACTS["dv_act"]
SUPPORTED_ACTS["payment_of_wages"] = SUPPORTED_ACTS["payment_wages"]
SUPPORTED_ACTS["food_safety"] = SUPPORTED_ACTS["fssa"]
SUPPORTED_ACTS["easements_act"] = SUPPORTED_ACTS["easements"]
SUPPORTED_ACTS["tn_rent"] = SUPPORTED_ACTS["tn_tenancy"]
SUPPORTED_ACTS["delhi_rent_control"] = SUPPORTED_ACTS["delhi_rent"]
SUPPORTED_ACTS["maharashtra_rent"] = SUPPORTED_ACTS["mh_rent"]


# Curated, verified statutory provisions dictionary mapped by (act_slug, section_str)
VERIFIED_STATUTE_FALLBACK = {
    # 1. Constitution of India
    ("constitution", "14"): {
        "act_name": "Constitution of India, 1950",
        "section": "14",
        "heading": "Equality before law",
        "text": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "19"): {
        "act_name": "Constitution of India, 1950",
        "section": "19",
        "heading": "Protection of certain rights regarding freedom of speech, etc.",
        "text": "All citizens shall have the right to freedom of speech and expression, to assemble peaceably and without arms, to form associations or unions, to move freely throughout India, to reside and settle in any part of India, and to practise any profession, trade or business.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "21"): {
        "act_name": "Constitution of India, 1950",
        "section": "21",
        "heading": "Protection of life and personal liberty",
        "text": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "21a"): {
        "act_name": "Constitution of India, 1950",
        "section": "21A",
        "heading": "Right to education",
        "text": "The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "22"): {
        "act_name": "Constitution of India, 1950",
        "section": "22",
        "heading": "Protection against arrest and detention in certain cases",
        "text": "No person who is arrested shall be detained in custody without being informed of the grounds for such arrest nor denied the right to consult and be defended by a legal practitioner of his choice. Every arrested person shall be produced before the nearest magistrate within twenty-four hours.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "32"): {
        "act_name": "Constitution of India, 1950",
        "section": "32",
        "heading": "Remedies for enforcement of rights conferred by Part III",
        "text": "The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by Part III is guaranteed (Writs of Habeas Corpus, Mandamus, Prohibition, Quo Warranto, and Certiorari).",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "51a"): {
        "act_name": "Constitution of India, 1950",
        "section": "51A",
        "heading": "Fundamental duties",
        "text": "It shall be the duty of every citizen of India to abide by the Constitution, cherish noble ideals of freedom struggle, uphold sovereignty, unity and integrity of India, defend the country, promote harmony, preserve cultural heritage, protect the environment, and develop scientific temper.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "141"): {
        "act_name": "Constitution of India, 1950",
        "section": "141",
        "heading": "Law declared by Supreme Court to be binding on all courts (Common Law & Precedent)",
        "text": "The law declared by the Supreme Court shall be binding on all courts within the territory of India. This constitutional provision establishes the common law doctrine of binding judicial precedent (stare decisis) in India.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "226"): {
        "act_name": "Constitution of India, 1950",
        "section": "226",
        "heading": "Power of High Courts to issue certain writs",
        "text": "Every High Court shall have power, throughout the territories in relation to which it exercise jurisdiction, to issue to any person or authority directions, orders or writs for the enforcement of Fundamental Rights and for any other purpose.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "300a"): {
        "act_name": "Constitution of India, 1950",
        "section": "300A",
        "heading": "Persons not to be deprived of property save by authority of law",
        "text": "No person shall be deprived of his property save by authority of law. Property is a vital constitutional and human right in India.",
        "former_provision": None,
        "status": "Constitutional Provision"
    },
    ("constitution", "part3"): {
        "act_name": "Constitution of India, 1950",
        "section": "Part III (Articles 12 to 35)",
        "heading": "Fundamental Rights",
        "text": "Part III of the Constitution guarantees six categories of Fundamental Rights: Right to Equality (Arts 14-18), Right to Freedom (Arts 19-22), Right against Exploitation (Arts 23-24), Right to Freedom of Religion (Arts 25-28), Cultural and Educational Rights (Arts 29-30), and Right to Constitutional Remedies (Art 32).",
        "former_provision": None,
        "status": "Constitutional Provision"
    },

    # 2. Bharatiya Nyaya Sanhita, 2023 (BNS) & IPC
    ("bns", "103"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "103",
        "heading": "Punishment for murder",
        "text": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine. Section 103(2) introduces specific penalties for mob lynching or murder committed by 5 or more persons acting in concert on grounds of race, caste, sex, or religion.",
        "former_provision": "Section 302 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("ipc", "302"): {
        "act_name": "Indian Penal Code, 1860",
        "section": "302",
        "heading": "Punishment for murder",
        "text": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 103 of Bharatiya Nyaya Sanhita, 2023 for offences after July 1, 2024)"
    },
    ("bns", "106"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "106",
        "heading": "Causing death by negligence",
        "text": "Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide, shall be punished with imprisonment of either description for a term which may extend to five years, and shall also be liable to fine.",
        "former_provision": "Section 304A of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bns", "115"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "115",
        "heading": "Voluntarily causing hurt",
        "text": "Whoever does any act with the intention of thereby causing hurt to any person, or with the knowledge that he is likely thereby to cause hurt to any person, and does thereby cause hurt to any person, is said voluntarily to cause hurt.",
        "former_provision": "Section 323 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bns", "303"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "303",
        "heading": "Theft",
        "text": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft. Punishable with imprisonment up to three years, or fine, or both, with community service for minor first-time thefts.",
        "former_provision": "Section 378 & 379 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("ipc", "378"): {
        "act_name": "Indian Penal Code, 1860",
        "section": "378",
        "heading": "Theft",
        "text": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 303 of Bharatiya Nyaya Sanhita, 2023 for offences after July 1, 2024)"
    },
    ("ipc", "379"): {
        "act_name": "Indian Penal Code, 1860",
        "section": "379",
        "heading": "Punishment for theft",
        "text": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 303(2) of Bharatiya Nyaya Sanhita, 2023 for offences after July 1, 2024)"
    },
    ("bns", "316"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "316",
        "heading": "Criminal breach of trust",
        "text": "Whoever, being in any manner entrusted with property, or with any dominion over property, dishonestly misappropriates or converts to his own use that property, commits criminal breach of trust. Punishable with imprisonment up to five years, or fine, or both.",
        "former_provision": "Section 405 & 406 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bns", "318"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "318",
        "heading": "Cheating and dishonestly inducing delivery of property",
        "text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "former_provision": "Section 420 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("ipc", "420"): {
        "act_name": "Indian Penal Code, 1860",
        "section": "420",
        "heading": "Cheating and dishonestly inducing delivery of property",
        "text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person... shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 318 of Bharatiya Nyaya Sanhita, 2023 for offences after July 1, 2024)"
    },
    ("bns", "351"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "351",
        "heading": "Criminal intimidation",
        "text": "Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of any one in whom that person is interested, with intent to cause alarm, commits criminal intimidation.",
        "former_provision": "Section 503 & 506 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bns", "356"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "356",
        "heading": "Defamation",
        "text": "Whoever, by words either spoken or intended to be read, or by signs or visible representations, makes or publishes any imputation concerning any person intending to harm the reputation of such person, is said to defame that person. Punishable with simple imprisonment up to two years, or fine, or both, or community service.",
        "former_provision": "Section 499 & 500 of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bns", "78"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "78",
        "heading": "Stalking",
        "text": "Any man who follows a woman and contacts, or attempts to contact such woman repeatedly despite a clear indication of disinterest, or monitors the use by a woman of the internet, email or other electronic communication, commits the offence of stalking.",
        "former_provision": "Section 354D of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bns", "85"): {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "85",
        "heading": "Cruelty by husband or relatives of husband",
        "text": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
        "former_provision": "Section 498A of Indian Penal Code, 1860",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("ipc", "498a"): {
        "act_name": "Indian Penal Code, 1860",
        "section": "498A",
        "heading": "Husband or relative of husband of a woman subjecting her to cruelty",
        "text": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 85 of Bharatiya Nyaya Sanhita, 2023)"
    },

    # 3. Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) & CrPC
    ("bnss", "35"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "35",
        "heading": "When police may arrest without warrant",
        "text": "Specifies conditions under which a police officer may arrest without warrant, incorporating safeguards for offences punishable with imprisonment for less than 7 years where arrest is not mandatory without prior permission from an officer not below Deputy SP.",
        "former_provision": "Section 41 of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "43"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "43",
        "heading": "Arrest how made (Special safeguards for arrest of women)",
        "text": "Except in exceptional circumstances with prior permission of a Judicial Magistrate, no woman shall be arrested after sunset and before sunrise, and all arrests of women must be carried out by a female police officer.",
        "former_provision": "Section 46(4) of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "173"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "173",
        "heading": "Information in cognizable cases (Registration of FIR, Zero FIR, and e-FIR)",
        "text": "Every information relating to the commission of a cognizable offence, irrespective of the area where the offence was committed (Zero FIR), may be given orally or by electronic communication (e-FIR). For offences punishable with 3 to 7 years, preliminary enquiry may be conducted within 14 days.",
        "former_provision": "Section 154 of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("crpc", "154"): {
        "act_name": "Code of Criminal Procedure, 1973",
        "section": "154",
        "heading": "Information in cognizable cases (First Information Report)",
        "text": "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 173 of Bharatiya Nagarik Suraksha Sanhita, 2023)"
    },
    ("bnss", "175"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "175",
        "heading": "Police officer's power to investigate cognizable case / Magistrate directions",
        "text": "Any magistrate empowered under section 210 may order such an investigation as mentioned in subsection (1). Corresponds to applications made when police refuse registration.",
        "former_provision": "Section 156(3) of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "187"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "187",
        "heading": "Procedure when investigation cannot be completed in twenty-four hours (Remand)",
        "text": "Authorizes detention of an accused in custody for a term not exceeding 15 days in the whole, or in parts, during the initial 40 or 60 days of the total 60 or 90 days detention period before mandatory default bail.",
        "former_provision": "Section 167 of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "223"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "223",
        "heading": "Examination of complainant (Private Complaints before Magistrate)",
        "text": "A Magistrate taking cognizance of an offence on complaint shall examine upon oath the complainant and witnesses present, with a requirement that no cognizance shall be taken without giving the accused an opportunity of being heard.",
        "former_provision": "Section 200 of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "479"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "479",
        "heading": "Maximum period for which an undertrial prisoner can be detained",
        "text": "A first-time offender (who has never been previously convicted of any offence) shall be released on bond if he has undergone detention for one-third of the maximum period of imprisonment specified for that offence.",
        "former_provision": "Section 436A of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "478"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "478",
        "heading": "In what cases bail to be taken (Bail in Bailable Offences)",
        "text": "When any person other than a person accused of a non-bailable offence is arrested or detained without warrant by an officer in charge of a police station, or appears or is brought before a Court, and is prepared to give bail, such person shall be released on bail. In bailable offences, bail is an absolute statutory right, not a matter of court discretion.",
        "former_provision": "Section 436 of Code of Criminal Procedure, 1973 (CrPC)",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("crpc", "436"): {
        "act_name": "Code of Criminal Procedure, 1973",
        "section": "436",
        "heading": "In what cases bail to be taken (Bailable Offences)",
        "text": "When any person accused of a bailable offence is arrested or detained, he shall be released on bail as a matter of right upon executing a bail bond.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 478 of Bharatiya Nagarik Suraksha Sanhita, 2023)"
    },
    ("bnss", "480"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "480",
        "heading": "When bail may be taken in case of non-bailable offence (Regular Bail)",
        "text": "When any person accused of, or suspected of, the commission of any non-bailable offence is arrested or detained without warrant, or appears before a Court other than High Court or Court of Session, he may be released on bail, subject to statutory conditions.",
        "former_provision": "Section 437 of Code of Criminal Procedure, 1973 (CrPC)",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "482"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "482",
        "heading": "Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
        "text": "Where any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or Court of Session for a direction that in the event of such arrest, he shall be released on bail.",
        "former_provision": "Section 438 of Code of Criminal Procedure, 1973",
        "status": "Current Legislation (In force from July 1, 2024)"
    },

    # 4. Bharatiya Sakshya Adhiniyam, 2023 (BSA) & IEA
    ("bsa", "22"): {
        "act_name": "Bharatiya Sakshya Adhiniyam, 2023",
        "section": "22",
        "heading": "Confession to police officer not to be proved",
        "text": "No confession made to a police officer shall be proved as against a person accused of any offence. Enforces a vital safeguard against custodial self-incrimination.",
        "former_provision": "Section 25 of Indian Evidence Act, 1872",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bsa", "61"): {
        "act_name": "Bharatiya Sakshya Adhiniyam, 2023",
        "section": "61",
        "heading": "Admissibility of electronic or digital records",
        "text": "Nothing in this Adhiniyam shall apply to deny the admissibility of an electronic or digital record in evidence on the ground that it is an electronic or digital record. Prescribes certification standards for digital evidence.",
        "former_provision": "Section 65A & 65B of Indian Evidence Act, 1872",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("iea", "65b"): {
        "act_name": "Indian Evidence Act, 1872",
        "section": "65B",
        "heading": "Admissibility of electronic records",
        "text": "Notwithstanding anything contained in this Act, any information contained in an electronic record... shall be deemed to be also a document, if the conditions mentioned in this section are satisfied.",
        "former_provision": None,
        "status": "Repealed Legislation (Replaced by Section 61 to 63 of Bharatiya Sakshya Adhiniyam, 2023)"
    },

    # 5. Civil Procedure Code, 1908 (CPC)
    ("cpc", "9"): {
        "act_name": "Code of Civil Procedure, 1908",
        "section": "9",
        "heading": "Courts to try all civil suits unless barred",
        "text": "The Courts shall have jurisdiction to try all suits of a civil nature excepting suits of which their cognizance is either expressly or impliedly barred.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("cpc", "20"): {
        "act_name": "Code of Civil Procedure, 1908",
        "section": "20",
        "heading": "Other suits to be instituted where defendants reside or cause of action arises",
        "text": "Every suit shall be instituted in a Court within the local limits of whose jurisdiction the defendant resides, carries on business, or where the cause of action, wholly or in part, arises.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("cpc", "80"): {
        "act_name": "Code of Civil Procedure, 1908",
        "section": "80",
        "heading": "Notice before filing suit against Government or public officer",
        "text": "No suit shall be instituted against the Government or against a public officer in respect of any act purporting to be done by such public officer in his official capacity, until the expiration of two months next after notice in writing has been delivered.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("cpc", "89"): {
        "act_name": "Code of Civil Procedure, 1908",
        "section": "89",
        "heading": "Settlement of disputes outside the Court",
        "text": "Where it appears to the Court that there exist elements of a settlement which may be acceptable to the parties, the Court shall formulate the terms of settlement and refer the same for arbitration, conciliation, judicial settlement including Lok Adalat, or mediation.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("cpc", "order37"): {
        "act_name": "Code of Civil Procedure, 1908",
        "section": "Order 37",
        "heading": "Summary Procedure for recovery of debts",
        "text": "Provides an expedited summary procedure for recovery of debts upon bills of exchange, hundies, promissory notes, or written contracts where the defendant cannot defend as a matter of right without leave from the court.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("cpc", "order39"): {
        "act_name": "Code of Civil Procedure, 1908",
        "section": "Order 39, Rules 1-2",
        "heading": "Temporary injunctions and interlocutory orders",
        "text": "Where in any suit it is proved by affidavit that any property in dispute is in danger of being wasted, damaged or alienated, the Court may grant a temporary injunction to restrain such acts until the disposal of the suit.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 6. Indian Contract Act, 1872
    ("contract_act", "2h"): {
        "act_name": "Indian Contract Act, 1872",
        "section": "2(h)",
        "heading": "Contract defined",
        "text": "An agreement enforceable by law is a contract. Agreements lacking legal enforceability or lawful consideration are void.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("contract_act", "10"): {
        "act_name": "Indian Contract Act, 1872",
        "section": "10",
        "heading": "What agreements are contracts",
        "text": "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("contract_act", "27"): {
        "act_name": "Indian Contract Act, 1872",
        "section": "27",
        "heading": "Agreement in restraint of trade void",
        "text": "Every agreement by which anyone is restrained from exercising a lawful profession, trade or business of any kind, is to that extent void, subject to limited exceptions relating to the sale of goodwill.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("contract_act", "73"): {
        "act_name": "Indian Contract Act, 1872",
        "section": "73",
        "heading": "Compensation for loss or damage caused by breach of contract",
        "text": "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("contract_act", "124"): {
        "act_name": "Indian Contract Act, 1872",
        "section": "124",
        "heading": "Contract of indemnity defined",
        "text": "A contract by which one party promises to save the other from loss caused to him by the conduct of the promisor himself, or by the conduct of any other person, is called a contract of indemnity.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 7. Consumer Protection Act, 2019
    ("cpa", "2_7"): {
        "act_name": "Consumer Protection Act, 2019",
        "section": "2(7)",
        "heading": "Consumer defined",
        "text": "A consumer is any person who buys goods or hires services for consideration, whether offline or online, but does not include a person who obtains goods for resale or commercial purpose.",
        "former_provision": "Section 2(1)(d) of Consumer Protection Act, 1986",
        "status": "Current Legislation"
    },
    ("cpa", "35"): {
        "act_name": "Consumer Protection Act, 2019",
        "section": "35",
        "heading": "Manner in which complaint shall be made to District Commission",
        "text": "A complaint may be filed with the District Commission by a consumer, voluntary consumer association, or Central Authority. Complaints can be filed electronically through the e-Daakhil portal.",
        "former_provision": "Section 12 of Consumer Protection Act, 1986",
        "status": "Current Legislation"
    },
    ("cpa", "84"): {
        "act_name": "Consumer Protection Act, 2019",
        "section": "84",
        "heading": "Liability of product manufacturer",
        "text": "A product manufacturer shall be liable in a product liability action if the product contains a manufacturing defect, design defect, or deviation from manufacturing specifications, or fails to contain adequate instructions.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 8. Cybercrime, IT Act, 2000 & DPDP Act, 2023
    ("it_act", "43"): {
        "act_name": "Information Technology Act, 2000",
        "section": "43",
        "heading": "Penalty and compensation for damage to computer system",
        "text": "If any person without permission of the owner accesses, downloads, copies, introduces viruses, damages, or disrupts any computer system, he shall be liable to pay damages by way of compensation to the person so affected.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("it_act", "66"): {
        "act_name": "Information Technology Act, 2000",
        "section": "66",
        "heading": "Computer related offences (Hacking)",
        "text": "If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("it_act", "66c"): {
        "act_name": "Information Technology Act, 2000",
        "section": "66C",
        "heading": "Punishment for identity theft",
        "text": "Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification feature of any other person, shall be punished with imprisonment of either description for a term which may extend to three years and fine up to one lakh rupees.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("it_act", "66d"): {
        "act_name": "Information Technology Act, 2000",
        "section": "66D",
        "heading": "Punishment for cheating by personation by using computer resource",
        "text": "Whoever, by means of any communication device or computer resource cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("dpdp", "6"): {
        "act_name": "Digital Personal Data Protection Act, 2023",
        "section": "6",
        "heading": "Consent requirements for processing personal data",
        "text": "Consent given by the Data Principal must be free, specific, informed, unconditional and unambiguous with a clear affirmative action. Consent may be withdrawn at any time with the same ease as it was given.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 9. Women's Legal Rights & Family Law
    ("dv_act", "12"): {
        "act_name": "Protection of Women from Domestic Violence Act, 2005",
        "section": "12",
        "heading": "Application to Magistrate for protection, residence and monetary relief",
        "text": "An aggrieved woman, Protection Officer or service provider may present an application to the Magistrate seeking protection orders, residence orders, monetary relief, custody orders, or compensation orders.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("posh", "4"): {
        "act_name": "Sexual Harassment of Women at Workplace Act, 2013",
        "section": "4",
        "heading": "Constitution of Internal Complaints Committee (ICC)",
        "text": "Every employer of a workplace employing ten or more employees shall constitute an 'Internal Complaints Committee' headed by a senior woman employee to receive and redress complaints of sexual harassment.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("posh", "9"): {
        "act_name": "Sexual Harassment of Women at Workplace Act, 2013",
        "section": "9",
        "heading": "Complaint of sexual harassment",
        "text": "Any aggrieved woman may make, in writing, a complaint of sexual harassment at workplace to the Internal Committee or Local Committee within a period of three months from the date of incident.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("maternity_benefit", "5"): {
        "act_name": "Maternity Benefit Act, 1961",
        "section": "5",
        "heading": "Right to payment of maternity benefit",
        "text": "Every woman is entitled to paid maternity benefit for a maximum period of twenty-six weeks of which not more than eight weeks shall precede the expected date of delivery.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("hma", "9"): {
        "act_name": "Hindu Marriage Act, 1955",
        "section": "9",
        "heading": "Restitution of conjugal rights",
        "text": "When either the husband or the wife has, without reasonable excuse, withdrawn from the society of the other, the aggrieved party may apply, by petition to the district court, for restitution of conjugal rights.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("hma", "13"): {
        "act_name": "Hindu Marriage Act, 1955",
        "section": "13",
        "heading": "Divorce grounds",
        "text": "Any marriage solemnized may be dissolved by a decree of divorce on grounds of adultery, cruelty, desertion for not less than two years, conversion, unsoundness of mind, or virulent venereal disease.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("hma", "13b"): {
        "act_name": "Hindu Marriage Act, 1955",
        "section": "13B",
        "heading": "Divorce by mutual consent",
        "text": "A petition for dissolution of marriage by a decree of divorce may be presented to the district court by both the parties together on the ground that they have been living separately for a period of one year or more and have mutually agreed that the marriage should be dissolved.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("hsa", "6"): {
        "act_name": "Hindu Succession Act, 1956",
        "section": "6",
        "heading": "Devolution of interest in coparcenary property (Equal rights to daughters)",
        "text": "The daughter of a coparcener shall by birth become a coparcener in her own right in the same manner as the son, having the same rights and liabilities in the coparcenary property (2005 Amendment affirmed in Vineeta Sharma v. Rakesh Sharma).",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 10. Property, Tenancy & Real Estate
    ("tpa", "54"): {
        "act_name": "Transfer of Property Act, 1882",
        "section": "54",
        "heading": "Sale of immovable property defined",
        "text": "Sale is a transfer of ownership in exchange for a price paid or promised. In the case of tangible immovable property of value of one hundred rupees and upwards, transfer can be made only by a registered instrument.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("model_tenancy", "4"): {
        "act_name": "Model Tenancy Act, 2021",
        "section": "4",
        "heading": "Mandatory written tenancy agreement",
        "text": "No person shall let or take on rent any premises except by an agreement in writing, which shall be jointly informed to the Rent Authority within a period of two months from the date of tenancy agreement.",
        "former_provision": None,
        "status": "Framework Legislation"
    },
    ("model_tenancy", "8"): {
        "act_name": "Model Tenancy Act, 2021",
        "section": "8",
        "heading": "Security deposit limit",
        "text": "Security deposit shall not exceed two months' rent for residential premises and six months' rent for non-residential premises, and must be refunded to tenant after deductions on vacating premises.",
        "former_provision": None,
        "status": "Framework Legislation"
    },
    ("rera", "18"): {
        "act_name": "Real Estate (Regulation and Development) Act, 2016",
        "section": "18",
        "heading": "Return of amount and compensation for delayed possession",
        "text": "If the promoter fails to complete or is unable to give possession of an apartment in accordance with the agreement for sale, he shall be liable on demand to return the amount received with interest at prescribed rates.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 11. Labour, Employment & Service Law
    ("code_on_wages", "6"): {
        "act_name": "Code on Wages, 2019",
        "section": "6",
        "heading": "Fixation of minimum wages",
        "text": "The appropriate Government shall fix a minimum rate of wages for employees, taking into account skill levels, geographical areas, and arduous nature of work, payable without gender discrimination.",
        "former_provision": "Minimum Wages Act, 1948",
        "status": "Current Legislation"
    },
    ("ida", "25f"): {
        "act_name": "Industrial Disputes Act, 1947",
        "section": "25F",
        "heading": "Conditions precedent to retrenchment of workmen",
        "text": "No workman employed in any industry who has been in continuous service for not less than one year shall be retrenched until given one month's notice in writing and compensation equivalent to fifteen days' average pay for every completed year of service.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 12. Banking, Financial & Commercial Law
    ("sarfaesi", "13"): {
        "act_name": "SARFAESI Act, 2002",
        "section": "13",
        "heading": "Enforcement of security interest without court intervention",
        "text": "Where any borrower defaults and his account is classified as NPA, the secured creditor may require the borrower by notice in writing to discharge his liabilities within sixty days, failing which the creditor may take possession of the secured asset.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("ni_act", "138"): {
        "act_name": "Negotiable Instruments Act, 1881",
        "section": "138",
        "heading": "Dishonour of cheque for insufficiency of funds (Cheque Bounce)",
        "text": "Where any cheque drawn by a person is returned unpaid by the bank for insufficiency of funds, such person shall be deemed to have committed an offence punishable with imprisonment up to two years, or with fine up to twice the amount of the cheque, or with both. Requires statutory legal demand notice within 30 days and 15 days payment window.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("ni_act", "141"): {
        "act_name": "Negotiable Instruments Act, 1881",
        "section": "141",
        "heading": "Offences by companies (Vicarious liability of directors)",
        "text": "If the person committing an offence under section 138 is a company, every person who; at the time the offence was committed, was in charge of, and was responsible to the company for the conduct of the business, shall be deemed guilty of the offence.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("ni_act", "142"): {
        "act_name": "Negotiable Instruments Act, 1881",
        "section": "142",
        "heading": "Cognizance of offences (30-day filing limitation)",
        "text": "No court shall take cognizance of any offence punishable under section 138 except upon a complaint in writing made within one month of the date on which the cause of action arises under clause (c) of section 138.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("companies_act", "166"): {
        "act_name": "Companies Act, 2013",
        "section": "166",
        "heading": "Duties of directors",
        "text": "A director of a company shall act in accordance with the articles, act in good faith to promote the objects of the company for the benefit of its members, exercise due and reasonable care, skill and diligence, and avoid conflicts of interest.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("ibc", "7"): {
        "act_name": "Insolvency and Bankruptcy Code, 2016",
        "section": "7",
        "heading": "Initiation of corporate insolvency resolution process by financial creditor",
        "text": "A financial creditor either by itself or jointly with other financial creditors may file an application for initiating corporate insolvency resolution process against a corporate debtor before the Adjudicating Authority (NCLT) when a default has occurred.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("pmla", "3"): {
        "act_name": "Prevention of Money Laundering Act, 2002",
        "section": "3",
        "heading": "Offence of money-laundering",
        "text": "Whosoever directly or indirectly attempts to indulge or knowingly assists or knowingly is a party or is actually involved in any process or activity connected with proceeds of crime including its concealment, possession, acquisition or use and projecting it as untainted property commits money-laundering.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 13. Motor Vehicles & Traffic Law
    ("mv_act", "134a"): {
        "act_name": "Motor Vehicles Act, 1988 (Amended 2019)",
        "section": "134A",
        "heading": "Protection of Good Samaritans",
        "text": "A Good Samaritan who renders emergency medical or non-medical care or assistance to a victim of an accident shall not be liable for any civil or criminal action for any injury to or death of the victim, nor forced to disclose personal identity.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("mv_act", "166"): {
        "act_name": "Motor Vehicles Act, 1988",
        "section": "166",
        "heading": "Application for compensation before Motor Accidents Claims Tribunal (MACT)",
        "text": "An application for compensation arising out of an accident involving death or bodily injury may be made by the person injured or by legal representatives before the Claims Tribunal having jurisdiction over the area where the accident occurred or claimant resides.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("mv_act", "185"): {
        "act_name": "Motor Vehicles Act, 1988 (Amended 2019)",
        "section": "185",
        "heading": "Driving by a drunken person or by a person under the influence of drugs",
        "text": "Whoever drives or attempts to drive a motor vehicle having alcohol exceeding 30 mg per 100 ml of blood detected by a breath analyser shall be punishable for the first offence with imprisonment up to six months, or fine up to ten thousand rupees, or both.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 14. Intellectual Property Law
    ("copyright_act", "14"): {
        "act_name": "Copyright Act, 1957",
        "section": "14",
        "heading": "Meaning of copyright",
        "text": "Copyright means the exclusive right to do or authorize the doing of acts in respect of literary, dramatic, musical, or artistic works, including reproduction, issuing copies, performing in public, making translations or adaptations.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("copyright_act", "52"): {
        "act_name": "Copyright Act, 1957",
        "section": "52",
        "heading": "Certain acts not to be infringement of copyright (Fair Dealing)",
        "text": "Fair dealing with any work for private or personal use including research, criticism, review, reporting of current events, or educational instruction shall not constitute an infringement of copyright.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("patents_act", "48"): {
        "act_name": "Patents Act, 1970",
        "section": "48",
        "heading": "Rights of patentees",
        "text": "A patent granted shall confer upon the patentee the exclusive right to prevent third parties, who do not have his consent, from making, using, offering for sale, selling or importing the patented product or process in India.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("trademarks_act", "29"): {
        "act_name": "Trade Marks Act, 1999",
        "section": "29",
        "heading": "Infringement of registered trade marks",
        "text": "A registered trade mark is infringed by a person who, not being a registered proprietor, uses in the course of trade a mark which is identical with, or deceptively similar to, the registered trade mark in relation to goods or services.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 15. Right to Information (RTI)
    ("rti", "6"): {
        "act_name": "Right to Information Act, 2005",
        "section": "6",
        "heading": "Request for obtaining information",
        "text": "A person who desires to obtain any information under this Act shall make a request in writing or through electronic means in English or Hindi or in the official language of the area to the Central Public Information Officer (CPIO) or State PIO accompanied by prescribed fee.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("rti", "7"): {
        "act_name": "Right to Information Act, 2005",
        "section": "7",
        "heading": "Disposal of request (30-day timeline & 48-hour life/liberty rule)",
        "text": "The CPIO or SPIO shall provide information within thirty days of the receipt of the request. Provided that where the information sought concerns the life or liberty of a person, the same shall be provided within forty-eight hours of the receipt of the request.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("rti", "8"): {
        "act_name": "Right to Information Act, 2005",
        "section": "8",
        "heading": "Exemption from disclosure of information",
        "text": "Specifies exemptions from disclosure including sovereignty, national security, strategic scientific interests, contempt of court, commercial confidence, trade secrets, fiduciary relationship, and unwarranted invasion of privacy unless larger public interest justifies it.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 16. Environmental Law & NGT
    ("epa", "15"): {
        "act_name": "Environment (Protection) Act, 1986",
        "section": "15",
        "heading": "Penalty for contravention of the provisions of the Act",
        "text": "Whoever fails to comply with or contravenes any of the provisions of this Act shall, in respect of each such failure or contravention, be punishable with imprisonment for a term which may extend to five years with fine up to one lakh rupees.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("ngt_act", "14"): {
        "act_name": "National Green Tribunal Act, 2010",
        "section": "14",
        "heading": "Tribunal to settle environmental disputes",
        "text": "The National Green Tribunal shall have the jurisdiction over all civil cases where a substantial question relating to environment arises out of the implementation of the enactments specified in Schedule I, within six months from the cause of action.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 17. Education, Medical & Vulnerable Sections
    ("rte", "12"): {
        "act_name": "Right of Children to Free and Compulsory Education Act, 2009",
        "section": "12(1)(c)",
        "heading": "25% reservation in private unaided schools for disadvantaged groups",
        "text": "Private unaided schools shall admit in class I, to the extent of at least twenty-five per cent of the strength of that class, children belonging to disadvantaged group and weaker section in the neighbourhood and provide free and compulsory elementary education.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("clinical_establishments", "12"): {
        "act_name": "Clinical Establishments (Registration and Regulation) Act, 2010",
        "section": "12",
        "heading": "Condition for registration & duty to provide emergency care",
        "text": "Every clinical establishment shall undertake to provide within the staff and facilities available, such medical examination and treatment as may be required to stabilize the emergency medical condition of any individual who comes or is brought to such establishment.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("senior_citizens_act", "4"): {
        "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "section": "4",
        "heading": "Maintenance of parents and senior citizens",
        "text": "A senior citizen including parent who is unable to maintain himself from his own earning or out of property owned by him, is entitled to make an application for maintenance against one or more of his adult children or relatives.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("senior_citizens_act", "23"): {
        "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "section": "23",
        "heading": "Transfer of property to be void in certain circumstances",
        "text": "Where any senior citizen has transferred by way of gift or otherwise his property, subject to the condition that the transferee shall provide the basic amenities, and such transferee refuses or fails to provide such amenities, the said transfer of property shall be deemed to have been made by fraud or coercion and shall at the option of the transferor be declared void by the Tribunal.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("pocso", "19"): {
        "act_name": "Protection of Children from Sexual Offences Act, 2012",
        "section": "19",
        "heading": "Mandatory reporting of offences against children",
        "text": "Notwithstanding anything contained in the Code of Criminal Procedure, any person who has apprehension that an offence under this Act has been committed shall provide such information to the Special Juvenile Police Unit or local police. Failure to report is punishable under Section 21.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("sc_st_act", "3"): {
        "act_name": "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "section": "3",
        "heading": "Punishments for offences of atrocities",
        "text": "Whoever, not being a member of a Scheduled Caste or a Scheduled Tribe, commits specified atrocities against an SC or ST individual (including physical abuse, social boycotts, wrongful dispossession of land, or false criminal proceedings) shall be punishable with rigorous imprisonment.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("sc_st_act", "18"): {
        "act_name": "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "section": "18",
        "heading": "Section 438 of the Code (Anticipatory Bail) not to apply to persons committing offences under the Act",
        "text": "Nothing in section 438 of the Code of Criminal Procedure shall apply in relation to any case involving the arrest of any person on an accusation of having committed an offence under this Act, subject to judicial review where no prima facie case is made out.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("poca", "7"): {
        "act_name": "Prevention of Corruption Act, 1988",
        "section": "7",
        "heading": "Offence relating to public servant being bribed",
        "text": "Any public servant who obtains or accepts or attempts to obtain from any person an undue advantage, with the intention to perform or cause performance of public duty improperly or dishonestly, shall be punishable with imprisonment for a term which shall not be less than three years but which may extend to seven years.",
        "former_provision": None,
        "status": "Current Legislation"
    },

    # 18. ADR, Legal Aid & Taxation
    ("arbitration_act", "8"): {
        "act_name": "Arbitration and Conciliation Act, 1996",
        "section": "8",
        "heading": "Power of court to refer parties to arbitration where there is an arbitration agreement",
        "text": "A judicial authority, before which an action is brought in a matter which is the subject of an arbitration agreement shall, if a party to the arbitration agreement applies, refer the parties to arbitration unless it finds that prima facie no valid arbitration agreement exists.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("arbitration_act", "34"): {
        "act_name": "Arbitration and Conciliation Act, 1996",
        "section": "34",
        "heading": "Application for setting aside arbitral award",
        "text": "Recourse to a Court against an arbitral award may be made only by an application for setting aside such award in accordance with sub-section (2) and sub-section (3) on limited grounds including incapacity of parties, invalidity of agreement, or conflict with public policy of India.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("mediation_act", "5"): {
        "act_name": "Mediation Act, 2023",
        "section": "5",
        "heading": "Pre-litigation mediation",
        "text": "Any party may before filing any suit or proceeding of civil or commercial nature take steps to settle the dispute by pre-litigation mediation in accordance with the provisions of this Act.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("lsaa", "12"): {
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "12",
        "heading": "Criteria for giving free legal services",
        "text": "Every person who has to file or defend a case shall be entitled to free legal services if that person is a member of SC or ST, a woman or child, a person with disability, a victim of mass disaster or violence, an industrial workman, in custody, or earning below prescribed annual income thresholds.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("lsaa", "21"): {
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "21",
        "heading": "Award of Lok Adalat",
        "text": "Every award of the Lok Adalat shall be deemed to be a decree of a civil court or an order of any other court, and no appeal shall lie to any court against the award of the Lok Adalat (final and binding on all parties).",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("it_tax_act", "139"): {
        "act_name": "Income-tax Act, 1961",
        "section": "139",
        "heading": "Return of income (Filing obligations and deadlines)",
        "text": "Every person whose total income exceeds the maximum amount which is not chargeable to income-tax shall furnish a return of his income on or before the due date in the prescribed form and verified in the prescribed manner.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("cgst_act", "16"): {
        "act_name": "Central Goods and Services Tax Act, 2017",
        "section": "16",
        "heading": "Eligibility and conditions for taking input tax credit (ITC)",
        "text": "Every registered person shall be entitled to take credit of input tax charged on any supply of goods or services to him which are used or intended to be used in the course or furtherance of his business, subject to tax invoice possession and tax payment proof.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("citizenship_act", "5"): {
        "act_name": "Citizenship Act, 1955",
        "section": "5",
        "heading": "Citizenship by registration",
        "text": "Subject to provisions of this section, the Central Government may register as a citizen of India any person who is not an illegal migrant on application made in this behalf if they satisfy prescribed residence and marriage qualifications.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("passports_act", "10"): {
        "act_name": "Passports Act, 1967",
        "section": "10",
        "heading": "Variation, impounding and revocation of passports",
        "text": "The passport authority may impound or cause to be impounded or revoke a passport or travel document if the holder is in wrongful possession, obtained by suppression of material facts, or if proceedings in respect of an offence alleged to have been committed by the holder are pending before a criminal court in India.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("payment_wages", "15"): {
        "act_name": "Payment of Wages Act, 1936",
        "section": "15",
        "heading": "Claims arising out of deductions from wages or delay in payment of wages",
        "text": "Where contrary to the provisions of this Act any deduction has been made from the wages of an employed person, or any payment of wages has been delayed, the person may apply to the Authority appointed under Section 15. The Authority may direct refund of deduction or payment of delayed wages together with compensation up to ten times the amount deducted.",
        "former_provision": None,
        "status": "Current Legislation (In Force)"
    },
    ("fssa", "59"): {
        "act_name": "Food Safety and Standards Act, 2006",
        "section": "59",
        "heading": "Punishment for unsafe food (including food past expiry date)",
        "text": "Any person who, whether by himself or by any other person on his behalf, manufactures for sale, stores, sells, distributes or imports any article of food for human consumption which is unsafe, shall be punishable with imprisonment extending up to life imprisonment and fine extending up to ten lakh rupees based on the gravity of injury.",
        "former_provision": "Prevention of Food Adulteration Act, 1954",
        "status": "Current Legislation"
    },
    ("mv_act", "206"): {
        "act_name": "Motor Vehicles Act, 1988",
        "section": "206",
        "heading": "Power of police officer to impound document (Driving Licence Seizure)",
        "text": "Section 206(4): A police officer or other person authorized may seize the driving licence of a person who has committed specified dangerous offences (drunk driving, dangerous driving, overspeeding, not wearing helmet/seatbelt). The officer must give an official acknowledgement and cannot seize documents arbitrarily without issuing an acknowledgment receipt.",
        "former_provision": "Amended by Motor Vehicles (Amendment) Act, 2019",
        "status": "Current Legislation (In Force)"
    },
    ("easements", "15"): {
        "act_name": "Indian Easements Act, 1882",
        "section": "15",
        "heading": "Acquisition of easement by prescription (Right of access, light and air)",
        "text": "Where the access and use of light or air to and for any building have been peaceably enjoyed therewith, as an easement, without interruption, and for twenty years, the right shall become absolute. A neighbour cannot construct or erect structures blocking prescriptive customary access.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("hma", "24"): {
        "act_name": "Hindu Marriage Act, 1955",
        "section": "24",
        "heading": "Maintenance pendente lite and expenses of proceedings",
        "text": "Where in any proceeding under this Act it appears to the court that either the wife or the husband, as the case may be, has no independent income sufficient for her or his support and the necessary expenses of the proceeding, it may, on the application of the wife or the husband, order the respondent to pay to the petitioner the expenses of the proceeding, and monthly during the proceeding such sum as, having regard to the petitioner's own income and the income of the respondent, it may seem to the court to be reasonable. As ruled by the Supreme Court in Rajnesh v. Neha (2020), a working wife is not disentitled from seeking maintenance if her earnings are insufficient to maintain the standard of living she was accustomed to in the matrimonial home.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("hma", "25"): {
        "act_name": "Hindu Marriage Act, 1955",
        "section": "25",
        "heading": "Permanent alimony and maintenance",
        "text": "Any court exercising jurisdiction under this Act may, at the time of passing any decree or at any time subsequent thereto, on application made to it for the purpose by either the wife or the husband, order that the respondent shall pay to the applicant for her or his maintenance and support such gross sum or such monthly or periodical sum for a term not exceeding the life of the applicant having regard to the respondent's own income and other property.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("bnss", "144"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "144",
        "heading": "Order for maintenance of wives, children and parents",
        "text": "If any person having sufficient means neglects or refuses to maintain his wife, unable to maintain herself, a Magistrate of the first class may, upon proof of such neglect or refusal, order such person to make a monthly allowance for the maintenance of his wife. 'Wife' includes a woman who has been divorced by, or has obtained a divorce from, her husband and has not remarried. A working woman who cannot adequately maintain herself according to the husband's economic standard is legally entitled to claim maintenance.",
        "former_provision": "Section 125 of Code of Criminal Procedure, 1973 (CrPC)",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("crpc", "125"): {
        "act_name": "Code of Criminal Procedure, 1973",
        "section": "125",
        "heading": "Order for maintenance of wives, children and parents",
        "text": "Statutory summary remedy for monthly maintenance of wife, legitimate or illegitimate minor children, and father or mother unable to maintain themselves.",
        "former_provision": "Replaced by Section 144 of Bharatiya Nagarik Suraksha Sanhita, 2023",
        "status": "Repealed Legislation (Transitional)"
    },
    ("ida", "33c"): {
        "act_name": "Industrial Disputes Act, 1947",
        "section": "33C",
        "heading": "Recovery of money due from an employer",
        "text": "Where any workman is entitled to receive from the employer any money or any benefit which is capable of being computed in terms of money, the workman may apply to the Labour Court under Section 33C(2) for determination of the amount due, which shall be recovered in the same manner as an arrear of land revenue.",
        "former_provision": None,
        "status": "Current Legislation (In Force)"
    },
    ("cpa", "2"): {
        "act_name": "Consumer Protection Act, 2019",
        "section": "2",
        "heading": "Definitions of 'defect' in goods and 'deficiency' in services",
        "text": "Section 2(10) defines 'defect' as any fault, imperfection or shortcoming in the quality, quantity, potency, purity or standard required by law or contract. Section 2(11) defines 'deficiency' as any fault, imperfection, shortcoming or inadequacy in performance. A defective mobile phone or warranty refusal falls squarely under these provisions.",
        "former_provision": "Section 2(1)(f) and 2(1)(g) of Consumer Protection Act, 1986",
        "status": "Current Legislation"
    },
    ("cpa", "84"): {
        "act_name": "Consumer Protection Act, 2019",
        "section": "84",
        "heading": "Liability of product manufacturer in product liability action",
        "text": "A product manufacturer shall be liable in a product liability action if: (a) the product contains a manufacturing defect; (b) the product is defective in design; (c) there is a deviation from manufacturing specifications; (d) the product does not conform to the express warranty; or (e) the product fails to contain adequate instructions for correct usage.",
        "former_provision": None,
        "status": "Current Legislation"
    },
    ("tn_tenancy", "21"): {
        "act_name": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
        "section": "21",
        "heading": "Repossession of premises by landlord / Eviction safeguards",
        "text": "A landlord cannot evict a tenant or recover possession except by making a formal application to the Rent Court on specific statutory grounds under Section 21(2), such as failure to pay agreed rent within one month of notice, subletting without consent, misuse of premises, or bona fide requirement of the landlord for personal occupation. Unilateral extra-judicial eviction without notice is strictly unlawful.",
        "former_provision": "Tamil Nadu Buildings (Lease and Rent Control) Act, 1960",
        "status": "State Legislation (In Force in Tamil Nadu)"
    },
    ("tn_tenancy", "19"): {
        "act_name": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017",
        "section": "19",
        "heading": "Landlord not to cut off or withhold essential services",
        "text": "No landlord or tenant shall cut off or withhold any essential supply or service (water, electricity, passage, sanitary services) enjoyed in respect of the premises. If disconnected, the affected tenant can immediately petition the Rent Authority, who may order interim restoration within 24-48 hours and penalize the defaulting landlord under Section 19(3).",
        "former_provision": None,
        "status": "State Legislation (In Force in Tamil Nadu)"
    },
    ("delhi_rent", "14"): {
        "act_name": "Delhi Rent Control Act, 1958",
        "section": "14",
        "heading": "Protection of tenant against eviction",
        "text": "Notwithstanding anything to the contrary contained in any other law or contract, no order or decree for the recovery of possession of any premises shall be made by any court or Controller in favour of the landlord against a tenant, except on statutory grounds specified in Section 14(1) (e.g. non-payment of rent after 2 months statutory notice, unauthorized subletting, bona fide requirement).",
        "former_provision": None,
        "status": "State Legislation (In Force in Delhi)"
    },
    ("delhi_rent", "45"): {
        "act_name": "Delhi Rent Control Act, 1958",
        "section": "45",
        "heading": "Cutting off or withholding essential supply or service",
        "text": "No landlord shall without just and sufficient cause cut off or withhold any essential supply or service enjoyed by the tenant. The Rent Controller may order immediate interim restoration and direct the landlord to pay compensation to the tenant.",
        "former_provision": None,
        "status": "State Legislation (In Force in Delhi)"
    },
    ("mh_rent", "15"): {
        "act_name": "Maharashtra Rent Control Act, 1999",
        "section": "15",
        "heading": "No ejectment ordinarily so long as tenant pays standard rent",
        "text": "A landlord shall not be entitled to the recovery of possession of any premises so long as the tenant pays, or is ready and willing to pay, the amount of standard rent and permitted increases, and observes the other conditions of tenancy.",
        "former_provision": "Section 12 of Bombay Rent Act, 1947",
        "status": "State Legislation (In Force in Maharashtra)"
    },
    ("mh_rent", "29"): {
        "act_name": "Maharashtra Rent Control Act, 1999",
        "section": "29",
        "heading": "Landlord not to cut-off or withhold essential supply or service",
        "text": "No landlord shall either by himself or through any person acting on his behalf cut off or withhold any essential supply or service (water, electricity, lights in passages, lifts, conservancy) enjoyed by the tenant. Violation is a cognizable offence punishable with imprisonment up to 3 months or fine up to ₹1,000 or both.",
        "former_provision": "Section 24 of Bombay Rent Act, 1947",
        "status": "State Legislation (In Force in Maharashtra)"
    },
    ("model_tenancy", "21"): {
        "act_name": "Model Tenancy Act, 2021",
        "section": "21",
        "heading": "Eviction and recovery of possession of premises (Central Model Framework)",
        "text": "A landlord may apply to the Rent Court for recovery of possession on grounds of failure to pay agreed rent for two consecutive months, subletting without consent, misuse of premises, or expiration of tenancy period without renewal. States adopt this framework by enacting or amending their State tenancy legislation.",
        "former_provision": None,
        "status": "Central Model Guidance"
    },
    ("bnss", "47"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "47",
        "heading": "Search of arrested person (Safeguard for female arrestees)",
        "text": "Whenever it is necessary to cause a female to be searched, the search shall be made by another female with strict regard to decency. A receipt for all seized articles (other than necessary wearing apparel) must be given to the arrested person.",
        "former_provision": "Section 51 of Code of Criminal Procedure, 1973 (CrPC)",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "48"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "48",
        "heading": "Right of arrested person to meet an advocate of choice",
        "text": "When any person is arrested and interrogated by the police, he shall be entitled to meet an advocate of his choice during interrogation, though not throughout interrogation.",
        "former_provision": "Section 41D of Code of Criminal Procedure, 1973 (CrPC)",
        "status": "Current Legislation (In force from July 1, 2024)"
    },
    ("bnss", "58"): {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "58",
        "heading": "Person arrested to be taken before Magistrate within twenty-four hours",
        "text": "No police officer shall detain in custody a person arrested without warrant for a longer period than under all the circumstances of the case is reasonable, and such period shall not, in the absence of a special order of a Magistrate under Section 187 BNSS, exceed twenty-four hours, exclusive of the time necessary for the journey from the place of arrest to the Magistrate's Court.",
        "former_provision": "Section 57 of Code of Criminal Procedure, 1973 (CrPC)",
        "status": "Current Legislation (In force from July 1, 2024)"
    }
}

# Curated, strictly verified landmark Supreme Court decisions mapped by topic
VERIFIED_LANDMARK_JUDGMENTS = {
    "arrest_safeguards": [
        {
            "case_id": "sc_dk_basu_1997",
            "title": "D.K. Basu v. State of West Bengal",
            "court": "Supreme Court of India",
            "decision_date": "1996-12-18",
            "citation": "(1997) 1 SCC 416",
            "url": "https://www.sci.gov.in/",
            "summary": "Mandated 11 binding guidelines for police during arrest and detention, including clear identification tags for arresting officers, preparation of a contemporaneous arrest memo countersigned by a witness, right of arrestee to inform a friend/relative, and medical examination every 48 hours."
        },
        {
            "case_id": "sc_arnesh_kumar_2014",
            "title": "Arnesh Kumar v. State of Bihar",
            "court": "Supreme Court of India",
            "decision_date": "2014-07-02",
            "citation": "(2014) 8 SCC 273",
            "url": "https://www.sci.gov.in/",
            "summary": "Held that arrest should not be made automatically or routinely for offences punishable with imprisonment up to 7 years. Police officers must serve a notice of appearance (codified in Section 35(3) BNSS / 41A CrPC) and record specific reasons in writing before effecting an arrest."
        }
    ],
    "maintenance_working_wife": [
        {
            "case_id": "sc_rajnesh_neha_2020",
            "title": "Rajnesh v. Neha",
            "court": "Supreme Court of India",
            "decision_date": "2020-11-04",
            "citation": "(2021) 2 SCC 324",
            "url": "https://www.sci.gov.in/",
            "summary": "Landmark ruling laying down uniform national guidelines for maintenance under Hindu Marriage Act, CrPC/BNSS, and DV Act. Explicitly held that a wife capable of earning or earning a separate income is not disentitled from seeking maintenance if her earnings are insufficient to maintain the standard of living she enjoyed in the matrimonial home."
        },
        {
            "case_id": "sc_chaturbhuj_2008",
            "title": "Chaturbhuj v. Sita Bai",
            "court": "Supreme Court of India",
            "decision_date": "2007-11-27",
            "citation": "(2008) 2 SCC 316",
            "url": "https://www.sci.gov.in/",
            "summary": "Clarified that the phrase 'unable to maintain herself' does not mean absolute destitution or begging. Even if the wife earns some income, she is entitled to maintenance from her husband if her income is not sufficient to maintain herself comfortably."
        }
    ],
    "unpaid_salary_wages": [
        {
            "case_id": "sc_pudr_1982",
            "title": "People's Union for Democratic Rights (PUDR) v. Union of India",
            "court": "Supreme Court of India",
            "decision_date": "1982-09-18",
            "citation": "(1982) 3 SCC 235",
            "url": "https://www.sci.gov.in/",
            "summary": "Held that non-payment of minimum or agreed wages amounts to 'forced labour' violating Article 23 of the Constitution. Every employer is legally bound to disburse statutory earned wages without unauthorized deductions."
        }
    ],
    "defective_goods_consumer": [
        {
            "case_id": "sc_maruti_udyog_2006",
            "title": "Maruti Udyog Ltd. v. Susheel Kumar Gabgotra",
            "court": "Supreme Court of India",
            "decision_date": "2006-03-29",
            "citation": "(2006) 4 SCC 644",
            "url": "https://www.sci.gov.in/",
            "summary": "Held that when a manufactured good suffers from a manufacturing defect that cannot be rectified, the consumer is entitled to replacement of the defective part or product or full refund along with compensation for deficiency."
        }
    ],
    "tenancy_eviction_safeguards": [
        {
            "case_id": "sc_ramesh_gobindram_2010",
            "title": "Ramesh Gobindram v. Sugra Humayun Mirza Wakf",
            "court": "Supreme Court of India",
            "decision_date": "2010-09-01",
            "citation": "(2010) 8 SCC 726",
            "url": "https://www.sci.gov.in/",
            "summary": "Reiterated that a tenant in settled possession cannot be dispossessed or evicted forcibly without due process of law. A landlord must obtain an order or decree from the competent statutory Rent Court / Civil Court before executing repossession."
        }
    ]
}

# Cross-populate provision fallback aliases
for (act, sec), val in list(VERIFIED_STATUTE_FALLBACK.items()):
    if act == "senior_citizens_act":
        VERIFIED_STATUTE_FALLBACK[("senior_citizens", sec)] = val
    elif act == "trademarks_act":
        VERIFIED_STATUTE_FALLBACK[("trademark_act", sec)] = val
    elif act == "rti":
        VERIFIED_STATUTE_FALLBACK[("rti_act", sec)] = val
    elif act == "rte":
        VERIFIED_STATUTE_FALLBACK[("rte_act", sec)] = val
    elif act == "clinical_establishments":
        VERIFIED_STATUTE_FALLBACK[("clinical_est", sec)] = val
    elif act == "dv_act":
        VERIFIED_STATUTE_FALLBACK[("pwdva", sec)] = val

