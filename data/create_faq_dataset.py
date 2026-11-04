"""
Script to generate the initial Legal FAQ dataset for LegalEase.
Contains 100 high-quality, legally accurate question-answer pairs
covering all 20 Indian legal awareness topics with verified sections and official URLs.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "legal_faq.csv"

FAQ_DATA = [
    # Topic 1: Indian Constitution
    {
        "id": 1,
        "question": "What is the Preamble of the Indian Constitution and what does it declare?",
        "answer": "The Preamble is the introductory statement of the Constitution that outlines its philosophy and objectives. It declares India to be a Sovereign, Socialist, Secular, Democratic Republic, committed to securing Justice, Liberty, Equality for all citizens and promoting Fraternity.",
        "topic": "Indian Constitution",
        "act_name": "Constitution of India",
        "section": "Preamble",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 2,
        "question": "What is the significance of Article 32 of the Constitution?",
        "answer": "Article 32 confers the Right to Constitutional Remedies, allowing individuals to move the Supreme Court directly to enforce their Fundamental Rights. Dr. B.R. Ambedkar famously called Article 32 the 'heart and soul of the Constitution'. The Court can issue writs including Habeas Corpus, Mandamus, Prohibition, Quo Warranto, and Certiorari.",
        "topic": "Indian Constitution",
        "act_name": "Constitution of India",
        "section": "Article 32",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 3,
        "question": "How can the Indian Constitution be amended?",
        "answer": "Article 368 outlines the procedure for constitutional amendment. Most provisions require a special majority in both Houses of Parliament (two-thirds of members present and voting and a majority of total membership). Certain federal provisions also require ratification by at least half of the State Legislatures. Amendments cannot violate the 'Basic Structure' of the Constitution.",
        "topic": "Indian Constitution",
        "act_name": "Constitution of India",
        "section": "Article 368",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 4,
        "question": "What is the difference between Fundamental Rights and Directive Principles of State Policy?",
        "answer": "Fundamental Rights (Part III, Articles 12-35) are justiciable and enforceable by courts against the State. Directive Principles of State Policy (Part IV, Articles 36-51) are non-justiciable guidelines for governance, intended to establish social and economic democracy, though they cannot be directly enforced through a court writ.",
        "topic": "Indian Constitution",
        "act_name": "Constitution of India",
        "section": "Part III & Part IV",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 5,
        "question": "What are the plenary powers of the Supreme Court under Article 142?",
        "answer": "Article 142 empowers the Supreme Court to pass any decree or order necessary for doing 'complete justice' in any cause or matter pending before it. Such orders are enforceable throughout the territory of India until provisions are enacted by Parliament.",
        "topic": "Indian Constitution",
        "act_name": "Constitution of India",
        "section": "Article 142",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },

    # Topic 2: Fundamental Rights
    {
        "id": 6,
        "question": "What are the six Fundamental Rights guaranteed to Indian citizens?",
        "answer": "The Constitution guarantees six broad categories of Fundamental Rights: Right to Equality (Articles 14-18), Right to Freedom (Articles 19-22), Right against Exploitation (Articles 23-24), Right to Freedom of Religion (Articles 25-28), Cultural and Educational Rights (Articles 29-30), and Right to Constitutional Remedies (Articles 32-35).",
        "topic": "Fundamental Rights",
        "act_name": "Constitution of India",
        "section": "Articles 12-35",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 7,
        "question": "What does the Right to Equality guarantee under Article 14?",
        "answer": "Article 14 guarantees that the State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. It applies to citizens and foreigners alike, prohibiting arbitrary discrimination while permitting reasonable classification based on intelligible differentia.",
        "topic": "Fundamental Rights",
        "act_name": "Constitution of India",
        "section": "Article 14",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 8,
        "question": "What is the scope of Right to Life and Personal Liberty under Article 21?",
        "answer": "Article 21 provides that no person shall be deprived of their life or personal liberty except according to procedure established by law. The Supreme Court has expansively interpreted Article 21 to include rights to privacy, dignified life, clean environment, health, speedy trial, and legal aid.",
        "topic": "Fundamental Rights",
        "act_name": "Constitution of India",
        "section": "Article 21",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 9,
        "question": "What protections does Article 22 offer against arbitrary arrest?",
        "answer": "Article 22 guarantees that an arrested person must be informed of the grounds of arrest, has the right to consult and be defended by a legal practitioner of choice, and must be produced before the nearest magistrate within 24 hours of arrest, excluding travel time.",
        "topic": "Fundamental Rights",
        "act_name": "Constitution of India",
        "section": "Article 22",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 10,
        "question": "What is the Right to Education under the Indian Constitution?",
        "answer": "Article 21A guarantees free and compulsory education to all children aged 6 to 14 years as a Fundamental Right. It is operationalized through the Right of Children to Free and Compulsory Education (RTE) Act, 2009.",
        "topic": "Fundamental Rights",
        "act_name": "Constitution of India",
        "section": "Article 21A",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 3: Fundamental Duties
    {
        "id": 11,
        "question": "What are Fundamental Duties under the Indian Constitution and where are they listed?",
        "answer": "Fundamental Duties are moral obligations expected of every citizen to promote patriotism and uphold the unity of India. They are listed under Article 51A in Part IVA of the Constitution, originally introduced by the 42nd Amendment in 1976 and expanded to 11 duties by the 86th Amendment in 2002.",
        "topic": "Fundamental Duties",
        "act_name": "Constitution of India",
        "section": "Article 51A",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 12,
        "question": "Are Fundamental Duties legally enforceable in a court of law?",
        "answer": "Fundamental Duties under Article 51A are not directly enforceable through court writs like Fundamental Rights. However, courts reference them to interpret ambiguous statutory provisions, and Parliament has enacted specific laws (such as the Prevention of Insults to National Honour Act) that make certain violations punishable.",
        "topic": "Fundamental Duties",
        "act_name": "Constitution of India",
        "section": "Article 51A",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 13,
        "question": "Is respecting the National Flag and National Anthem a Fundamental Duty?",
        "answer": "Yes, Article 51A(a) mandates that every citizen shall abide by the Constitution and respect its ideals and institutions, the National Flag, and the National Anthem. Disrespecting them is also an offence under the Prevention of Insults to National Honour Act, 1971.",
        "topic": "Fundamental Duties",
        "act_name": "Constitution of India",
        "section": "Article 51A(a)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 14,
        "question": "What is the duty of citizens regarding environmental protection?",
        "answer": "Article 51A(g) states that it is the duty of every citizen to protect and improve the natural environment, including forests, lakes, rivers, and wildlife, and to have compassion for living creatures.",
        "topic": "Fundamental Duties",
        "act_name": "Constitution of India",
        "section": "Article 51A(g)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 15,
        "question": "What duty do parents have regarding the education of their children?",
        "answer": "Under Article 51A(k), added by the 86th Constitutional Amendment Act, 2002, it is the duty of a parent or guardian to provide opportunities for education to their child or ward between the ages of 6 and 14 years.",
        "topic": "Fundamental Duties",
        "act_name": "Constitution of India",
        "section": "Article 51A(k)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 4: Consumer Protection
    {
        "id": 16,
        "question": "Who is considered a 'consumer' under the Consumer Protection Act, 2019?",
        "answer": "Under Section 2(7) of the Consumer Protection Act, 2019, a consumer is any person who buys goods or hires services for consideration. It includes offline and online transactions, but expressly excludes individuals who obtain goods or services for commercial purposes or resale.",
        "topic": "Consumer Protection",
        "act_name": "Consumer Protection Act, 2019",
        "section": "Section 2(7)",
        "source_title": "National Consumer Helpline",
        "source_url": "https://consumerhelpline.gov.in/"
    },
    {
        "id": 17,
        "question": "What are the three tiers of Consumer Dispute Redressal Commissions in India?",
        "answer": "The Act establishes a three-tier quasi-judicial system: District Consumer Disputes Redressal Commission (District Commission) for claims up to Rs 50 lakh; State Consumer Disputes Redressal Commission (State Commission) for claims between Rs 50 lakh and Rs 2 crore; and National Consumer Disputes Redressal Commission (NCDRC) for claims exceeding Rs 2 crore.",
        "topic": "Consumer Protection",
        "act_name": "Consumer Protection Act, 2019",
        "section": "Sections 28, 42, 53",
        "source_title": "National Consumer Helpline",
        "source_url": "https://consumerhelpline.gov.in/"
    },
    {
        "id": 18,
        "question": "Can a consumer file a consumer grievance online in India?",
        "answer": "Yes, consumers can file grievances online via the National Consumer Helpline portal (consumerhelpline.gov.in) or helpline number 1915. For formal legal complaints before Consumer Commissions, consumers can file digitally through the 'e-Daakhil' portal (edaakhil.nic.in) without requiring an advocate.",
        "topic": "Consumer Protection",
        "act_name": "Consumer Protection Act, 2019",
        "section": "Section 35",
        "source_title": "National Consumer Helpline",
        "source_url": "https://consumerhelpline.gov.in/"
    },
    {
        "id": 19,
        "question": "What is product liability under the Consumer Protection Act, 2019?",
        "answer": "Product liability under Chapter VI (Sections 82-87) makes manufacturers, service providers, and product sellers responsible for compensating consumers for harm, injury, or property damage caused by a defective product or deficiency in service.",
        "topic": "Consumer Protection",
        "act_name": "Consumer Protection Act, 2019",
        "section": "Sections 82-87",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 20,
        "question": "What remedies can a Consumer Commission grant to an aggrieved consumer?",
        "answer": "Under Section 39, a Consumer Commission can order removal of defects, replacement of goods, refund of the price paid with interest, award compensation for loss or injury (including mental agony), order discontinuation of unfair trade practices, and award punitive damages.",
        "topic": "Consumer Protection",
        "act_name": "Consumer Protection Act, 2019",
        "section": "Section 39",
        "source_title": "National Consumer Helpline",
        "source_url": "https://consumerhelpline.gov.in/"
    },

    # Topic 5: Cybercrime and Online Fraud
    {
        "id": 21,
        "question": "How do I report online financial fraud or cybercrime in India?",
        "answer": "Online cybercrime and financial frauds can be immediately reported to the National Cyber Crime Reporting Portal at cybercrime.gov.in or by dialling the national cyber helpline 1930. Quick reporting within the 'golden hour' enables law enforcement and banks to freeze fraudulent fund transfers.",
        "topic": "Cybercrime and Online Fraud",
        "act_name": "Information Technology Act, 2000",
        "section": "Section 66D",
        "source_title": "National Cyber Crime Reporting Portal",
        "source_url": "https://cybercrime.gov.in/"
    },
    {
        "id": 22,
        "question": "What is the 'Golden Hour' in cyber financial fraud reporting?",
        "answer": "The 'Golden Hour' refers to the first 1 to 2 hours immediately following an unauthorized bank transaction or cyber fraud. Calling helpline 1930 immediately enables the Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS) to alert victim banks and destination banks to freeze the money before fraudsters withdraw it.",
        "topic": "Cybercrime and Online Fraud",
        "act_name": "Information Technology Act, 2000",
        "section": "",
        "source_title": "National Cyber Crime Reporting Portal",
        "source_url": "https://cybercrime.gov.in/"
    },
    {
        "id": 23,
        "question": "What is identity theft and how is it penalized under the IT Act?",
        "answer": "Under Section 66C of the Information Technology Act, fraudulently or dishonestly making use of the electronic signature, password, or any other unique identification feature of another person constitutes identity theft, punishable with imprisonment up to 3 years and a fine up to Rs 1 lakh.",
        "topic": "Cybercrime and Online Fraud",
        "act_name": "Information Technology Act, 2000",
        "section": "Section 66C",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 24,
        "question": "What legal action can be taken against cyberstalking and online harassment?",
        "answer": "Cyberstalking, monitoring a woman's internet activity, or sending persistent unwanted electronic messages is punishable under Section 78 of the Bharatiya Nyaya Sanhita, 2023 (formerly Section 354D of the IPC) with imprisonment up to 3 years on first conviction. Victims can also lodge a complaint on cybercrime.gov.in under the 'Report Women/Child Related Crime' category.",
        "topic": "Cybercrime and Online Fraud",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "Section 78 (formerly Section 354D IPC)",
        "source_title": "National Cyber Crime Reporting Portal",
        "source_url": "https://cybercrime.gov.in/"
    },
    {
        "id": 25,
        "question": "Is unauthorized access to a computer system or hacking illegal in India?",
        "answer": "Yes, accessing a computer, computer system, or network without permission, downloading or copying data, or introducing computer viruses is illegal under Section 43 (civil liability with compensation) and Section 66 (criminal offence with imprisonment up to 3 years or fine up to Rs 5 lakh) of the Information Technology Act, 2000.",
        "topic": "Cybercrime and Online Fraud",
        "act_name": "Information Technology Act, 2000",
        "section": "Sections 43, 66",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 6: Women's Rights and Legal Protection
    {
        "id": 26,
        "question": "What legal protections are provided by the Protection of Women from Domestic Violence Act (PWDVA), 2005?",
        "answer": "The PWDVA protects women from physical, sexual, verbal, emotional, and economic abuse within a domestic relationship. Victims can seek Protection Orders (stopping abuse), Residence Orders (right not to be evicted), Monetary Relief (medical costs, maintenance), and temporary Custody Orders for children from a Magistrate.",
        "topic": "Women's Rights and Legal Protection",
        "act_name": "Protection of Women from Domestic Violence Act, 2005",
        "section": "Sections 12, 18, 19, 20",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 27,
        "question": "What is the POSH Act and how does it protect women at workplaces?",
        "answer": "The Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013 (POSH Act) mandates every workplace with 10 or more employees to constitute an Internal Complaints Committee (ICC). It provides a confidential, time-bound mechanism to handle complaints of unwelcome physical, verbal, or non-verbal sexual conduct.",
        "topic": "Women's Rights and Legal Protection",
        "act_name": "Sexual Harassment of Women at Workplace Act, 2013",
        "section": "Sections 4, 9, 11",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 28,
        "question": "What are the legal rules regarding the arrest of a woman in India?",
        "answer": "Under Section 43(1) proviso of the Bharatiya Nagarik Suraksha Sanhita, 2023 (formerly Section 46(4) CrPC), no woman can be arrested after sunset and before sunrise, except in extraordinary circumstances with prior written permission of a Judicial Magistrate. Furthermore, the arrest must be carried out by a female police officer.",
        "topic": "Women's Rights and Legal Protection",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 43(1) (formerly Section 46(4) CrPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 29,
        "question": "Does a married woman have a legal right of residence in her matrimonial home?",
        "answer": "Yes, under Section 17 of the Protection of Women from Domestic Violence Act, 2005, every woman in a domestic relationship has the right to reside in the shared household, regardless of whether she has any legal right, title, or beneficial interest in the property.",
        "topic": "Women's Rights and Legal Protection",
        "act_name": "Protection of Women from Domestic Violence Act, 2005",
        "section": "Section 17",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 30,
        "question": "What maternity benefits are guaranteed to working women in India?",
        "answer": "Under the Maternity Benefit (Amendment) Act, 2017, working women are entitled to 26 weeks of paid maternity leave for up to two surviving children. Establishments with 50 or more employees must also provide a creche facility within a prescribed distance.",
        "topic": "Women's Rights and Legal Protection",
        "act_name": "Maternity Benefit Act, 1961",
        "section": "Section 5",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 7: Family Law
    {
        "id": 31,
        "question": "What is the legal framework governing maintenance for senior citizens and elderly parents in India?",
        "answer": "The Maintenance and Welfare of Parents and Senior Citizens Act, 2007 enables senior citizens or parents unable to maintain themselves to apply before a Maintenance Tribunal for a monthly maintenance allowance from children or legal heirs possessing their property.",
        "topic": "Family Law",
        "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "section": "Sections 4, 5",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 32,
        "question": "What is the difference between ancestral property and self-acquired property?",
        "answer": "Ancestral property is inherited up to four generations of male lineage without partition, in which coparceners acquire a right by birth. Self-acquired property is purchased or acquired by an individual using their own funds or inherited via a Will/gift; the owner has full freedom to sell or gift it to anyone without family consent.",
        "topic": "Family Law",
        "act_name": "Hindu Succession Act, 1956",
        "section": "",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 33,
        "question": "How do Indian courts determine child custody during family disputes?",
        "answer": "Under the Guardians and Wards Act, 1890 and Indian personal laws, the paramount consideration is always the 'welfare of the minor child' rather than the legal rights of either parent. Courts assess emotional bonding, moral environment, educational opportunities, and the child's preference if of sufficient age.",
        "topic": "Family Law",
        "act_name": "Guardians and Wards Act, 1890",
        "section": "Sections 7, 17",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 34,
        "question": "Can a senior citizen cancel a gift deed of property given to children if they refuse to care for them?",
        "answer": "Yes, under Section 23 of the Maintenance and Welfare of Parents and Senior Citizens Act, 2007, if a senior citizen transfers property subject to the condition that the transferee provides basic amenities and physical needs, and the transferee fails to do so, the transfer can be declared void by the Maintenance Tribunal.",
        "topic": "Family Law",
        "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "section": "Section 23",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 35,
        "question": "What is the legal process for child adoption in India?",
        "answer": "Adoptions in India are governed primarily by the Juvenile Justice (Care and Protection of Children) Act, 2015 and CARA (Central Adoption Resource Authority) guidelines. Prospective adoptive parents must register through the CARINGS portal, undergo home study assessments, and receive formal approval from District Magistrates.",
        "topic": "Family Law",
        "act_name": "Juvenile Justice (Care and Protection of Children) Act, 2015",
        "section": "Sections 56-70",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 8: Marriage and Divorce
    {
        "id": 36,
        "question": "What is the Special Marriage Act, 1954 and who can marry under it?",
        "answer": "The Special Marriage Act, 1954 provides a civil marriage framework for any two persons in India or Indian nationals abroad, irrespective of their respective religions, castes, or faiths. It does not require either party to convert or renounce their religion.",
        "topic": "Marriage and Divorce",
        "act_name": "Special Marriage Act, 1954",
        "section": "Sections 4, 5",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 37,
        "question": "What are the conditions for divorce by mutual consent under the Hindu Marriage Act?",
        "answer": "Under Section 13B of the Hindu Marriage Act, 1955, both spouses may jointly petition for divorce on grounds that they have been living separately for a period of one year or more, have not been able to live together, and have mutually agreed that the marriage should be dissolved.",
        "topic": "Marriage and Divorce",
        "act_name": "Hindu Marriage Act, 1955",
        "section": "Section 13B",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 38,
        "question": "What is the legal age of marriage for men and women in India?",
        "answer": "Under Section 2(a) of the Prohibition of Child Marriage Act, 2006, the legal minimum age of marriage is 18 years for females and 21 years for males. Marriages solemnized below these ages are punishable offences under the Act.",
        "topic": "Marriage and Divorce",
        "act_name": "Prohibition of Child Marriage Act, 2006",
        "section": "Section 2(a)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 39,
        "question": "Can a spouse claim permanent alimony and maintenance upon divorce?",
        "answer": "Yes, under Section 25 of the Hindu Marriage Act, 1955 (and corresponding provisions in other personal laws and Section 144 of BNSS, 2023 / formerly Section 125 CrPC), the court can direct payment of gross sum or monthly maintenance taking into account the applicant's property, financial status, and conduct of parties.",
        "topic": "Marriage and Divorce",
        "act_name": "Hindu Marriage Act, 1955",
        "section": "Section 25",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 40,
        "question": "Is marriage registration mandatory in India?",
        "answer": "Yes, the Supreme Court of India in the landmark Seema v. Ashwani Kumar judgment ruled that marriage registration is mandatory across all religions to protect the rights of spouses, safeguard against bigamy, and facilitate succession, child custody, and passport documentation.",
        "topic": "Marriage and Divorce",
        "act_name": "Special Marriage Act, 1954 / State Registration Acts",
        "section": "",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },

    # Topic 9: Property and Inheritance
    {
        "id": 41,
        "question": "Do daughters have equal inheritance rights in ancestral Hindu property?",
        "answer": "Yes. Following the Hindu Succession (Amendment) Act, 2005 and the Supreme Court judgment in Vineeta Sharma v. Rakesh Sharma (2020), daughters have equal coparcenary rights by birth in ancestral property, with the same rights and liabilities as sons, irrespective of whether the father was alive in 2005.",
        "topic": "Property and Inheritance",
        "act_name": "Hindu Succession Act, 1956",
        "section": "Section 6",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 42,
        "question": "What is a Will and is registration of a Will compulsory in India?",
        "answer": "A Will is a legal declaration of an individual's intention regarding the distribution of their property after death. Under Section 18 of the Registration Act, 1908, registering a Will is optional, not mandatory. However, registering it with the Sub-Registrar provides strong evidence of authenticity in case of dispute.",
        "topic": "Property and Inheritance",
        "act_name": "Indian Succession Act, 1925",
        "section": "Section 59",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 43,
        "question": "What happens if an individual dies intestate without leaving a Will?",
        "answer": "If a person dies intestate (without a Will), their property is distributed among legal heirs according to personal succession laws. For a Hindu male, under Section 8 of the Hindu Succession Act, property passes first to Class I heirs (mother, widow, sons, daughters) in equal shares.",
        "topic": "Property and Inheritance",
        "act_name": "Hindu Succession Act, 1956",
        "section": "Section 8",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 44,
        "question": "What is an Encumbrance Certificate (EC) and why is it essential when buying real estate?",
        "answer": "An Encumbrance Certificate (EC) issued by the Sub-Registrar confirms that a property is free from legal liabilities, registered mortgages, charges, or liens during a specified period, proving clean title for the prospective buyer.",
        "topic": "Property and Inheritance",
        "act_name": "Transfer of Property Act, 1882",
        "section": "Section 54",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 45,
        "question": "What remedies does a homebuyer have under RERA if a builder delays possession?",
        "answer": "Under Section 18 of the Real Estate (Regulation and Development) Act, 2016 (RERA), if a promoter fails to give possession according to agreement, the homebuyer can either withdraw from the project with full refund plus interest, or choose to stay in the project and receive monthly interest for every month of delay.",
        "topic": "Property and Inheritance",
        "act_name": "Real Estate (Regulation and Development) Act, 2016",
        "section": "Section 18",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 10: Employment and Labour Rights
    {
        "id": 46,
        "question": "What are an employee's rights regarding notice period and retrenchment compensation under Indian labour law?",
        "answer": "Under Section 25F of the Industrial Disputes Act, 1947, a workman who has been in continuous service for not less than one year cannot be retrenched without one month's notice in writing (or pay in lieu thereof) and retrenchment compensation equivalent to 15 days average pay for every completed year of service.",
        "topic": "Employment and Labour Rights",
        "act_name": "Industrial Disputes Act, 1947",
        "section": "Section 25F",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 47,
        "question": "What is the Employee Provident Fund (EPF) and who is covered?",
        "answer": "Under the Employees' Provident Funds and Miscellaneous Provisions Act, 1952, establishments with 20 or more employees are required to enroll eligible employees. Both employer and employee contribute 12% of basic wage and dearness allowance towards retirement savings.",
        "topic": "Employment and Labour Rights",
        "act_name": "Employees' Provident Funds and Miscellaneous Provisions Act, 1952",
        "section": "Section 6",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 48,
        "question": "What are the legal rules regarding overtime wages under Indian labour laws?",
        "answer": "Under Section 59 of the Factories Act, 1948 and state Shops and Establishments Acts, when an employee or worker works for more than 9 hours in a day or 48 hours in a week, they are entitled to overtime wages at twice their ordinary rate of wages.",
        "topic": "Employment and Labour Rights",
        "act_name": "Factories Act, 1948",
        "section": "Section 59",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 49,
        "question": "When does an employee become entitled to payment of gratuity?",
        "answer": "Under Section 4 of the Payment of Gratuity Act, 1972, gratuity is payable to an employee on termination of employment after rendering continuous service for not less than 5 years (except in cases of death or disablement, where the 5-year requirement is waived).",
        "topic": "Employment and Labour Rights",
        "act_name": "Payment of Gratuity Act, 1972",
        "section": "Section 4",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 50,
        "question": "Can an employer arbitrarily withhold an employee's salary or experience certificate?",
        "answer": "No. Under the Payment of Wages Act, 1936, wages must be paid without unauthorized deductions. Withholding earned wages or service certificates without lawful reason is unlawful, and the employee can approach the Labour Commissioner or file a civil claim.",
        "topic": "Employment and Labour Rights",
        "act_name": "Payment of Wages Act, 1936",
        "section": "Section 7",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 11: Criminal Law
    {
        "id": 51,
        "question": "What is the Bharatiya Nyaya Sanhita (BNS), 2023 and how does it replace the Indian Penal Code (IPC)?",
        "answer": "The Bharatiya Nyaya Sanhita, 2023 (BNS) replaced the Indian Penal Code, 1860 effective July 1, 2024. It modernizes criminal offences, introduces community service as a punishment for minor crimes, updates sexual offence definitions, and reorganizes section numbering across 358 sections.",
        "topic": "Criminal Law",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "Section 1",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 52,
        "question": "What is the punishment for cheating under Section 318 of BNS (formerly Section 420 IPC)?",
        "answer": "Under Section 318 of the Bharatiya Nyaya Sanhita, 2023 (which supersedes Section 420 IPC), cheating and dishonestly inducing delivery of property is punishable with imprisonment for a term which may extend to 7 years, and shall also be liable to fine.",
        "topic": "Criminal Law",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "Section 318 (formerly Section 420 IPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 53,
        "question": "What is the difference between bailable and non-bailable offences?",
        "answer": "Under Section 2(1)(a) of the BNSS, 2023 (formerly Section 2(a) CrPC), in bailable offences, bail is a matter of absolute legal right upon providing surety. In non-bailable offences, bail is not a right; the court exercises judicial discretion based on the severity of the offence and risk of absconding.",
        "topic": "Criminal Law",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 2(1)(a) (formerly Section 2(a) CrPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 54,
        "question": "What constitutes criminal breach of trust under Section 316 of BNS (formerly Section 405 IPC)?",
        "answer": "Under Section 316 of the Bharatiya Nyaya Sanhita, 2023, criminal breach of trust occurs when a person entrusted with property dishonestly misappropriates it or converts it to their own use in violation of any legal contract or direction of law.",
        "topic": "Criminal Law",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "Section 316 (formerly Section 405 IPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 55,
        "question": "What is the offence of defamation under Section 356 of BNS (formerly Section 499/500 IPC)?",
        "answer": "Defamation under Section 356 of BNS, 2023 consists of making or publishing an imputation concerning any person intending to harm their reputation. It is punishable with simple imprisonment up to 2 years, or with fine, or with both, or with community service.",
        "topic": "Criminal Law",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section": "Section 356 (formerly Section 499 IPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 12: Civil Law
    {
        "id": 56,
        "question": "What is a legal notice and is it mandatory before filing a civil suit in India?",
        "answer": "A legal notice is a formal written communication notifying the recipient of a legal grievance and intention to initiate legal proceedings unless demands are met. While not mandatory for private commercial disputes, serving a 2-month prior legal notice is mandatory under Section 80 CPC when suing the Government or a public officer in their official capacity.",
        "topic": "Civil Law",
        "act_name": "Code of Civil Procedure, 1908",
        "section": "Section 80",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 57,
        "question": "What is a temporary injunction and when is it granted under Order 39 of CPC?",
        "answer": "Under Order 39 Rules 1 and 2 of the Code of Civil Procedure, 1908, a court may grant a temporary injunction to preserve the status quo of a property during litigation. The applicant must establish a prima facie case, balance of convenience in their favour, and irreparable injury if the injunction is denied.",
        "topic": "Civil Law",
        "act_name": "Code of Civil Procedure, 1908",
        "section": "Order 39, Rules 1-2",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 58,
        "question": "What is the limitation period for filing a suit for recovery of money?",
        "answer": "Under the Limitation Act, 1963 (Articles 19 to 21 of the Schedule), the limitation period for filing a civil suit for recovery of money or debt is 3 years from the date the cause of action arises or from the date payment became due.",
        "topic": "Civil Law",
        "act_name": "Limitation Act, 1963",
        "section": "Articles 19-21",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 59,
        "question": "What is a Summary Suit under Order 37 of the CPC?",
        "answer": "Order 37 of the CPC provides a fast-track procedure for recovering liquidated debts arising from bills of exchange, hundies, promissory notes, or written contracts. Unlike ordinary suits, the defendant does not have an automatic right to defend and must apply for leave to defend within 10 days.",
        "topic": "Civil Law",
        "act_name": "Code of Civil Procedure, 1908",
        "section": "Order 37",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 60,
        "question": "What is the difference between a General Power of Attorney (GPA) and a Special Power of Attorney (SPA)?",
        "answer": "Under the Powers of Attorney Act, 1882, a General Power of Attorney grants the agent broad authority to handle multiple types of legal, business, and financial transactions on behalf of the principal. A Special Power of Attorney authorizes the agent to perform only a single, specific act or transaction.",
        "topic": "Civil Law",
        "act_name": "Powers of Attorney Act, 1882",
        "section": "Sections 1A, 2",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 13: Traffic Rules and Road Safety
    {
        "id": 61,
        "question": "What is the penalty for driving without a valid driving license in India?",
        "answer": "Under Section 181 of the Motor Vehicles (Amendment) Act, 2019, driving a motor vehicle without a valid driving license is punishable with a fine of up to Rs 5,000, or imprisonment up to 3 months, or both.",
        "topic": "Traffic Rules and Road Safety",
        "act_name": "Motor Vehicles Act, 1988",
        "section": "Section 181",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 62,
        "question": "What is the legal limit for drunk driving and what penalties apply?",
        "answer": "Under Section 185 of the Motor Vehicles Act, driving with blood alcohol content (BAC) exceeding 30 mg per 100 ml of blood is an offence punishable on first conviction with imprisonment up to 6 months or fine up to Rs 10,000, and up to 2 years imprisonment or fine up to Rs 15,000 for repeat offences.",
        "topic": "Traffic Rules and Road Safety",
        "act_name": "Motor Vehicles Act, 1988",
        "section": "Section 185",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 63,
        "question": "What legal protections are provided to a Good Samaritan who helps an accident victim?",
        "answer": "Section 134A of the Motor Vehicles Act protects Good Samaritans from civil and criminal liability for any injury or death of an accident victim resulting from emergency assistance rendered in good faith. Police and hospitals cannot force a Good Samaritan to disclose identity or become a witness.",
        "topic": "Traffic Rules and Road Safety",
        "act_name": "Motor Vehicles Act, 1988",
        "section": "Section 134A",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 64,
        "question": "Are digital vehicle documents stored in DigiLocker or mParivahan legally valid during traffic checks?",
        "answer": "Yes. Under Rule 139 of the Central Motor Vehicles Rules and Ministry of Road Transport and Highways (MoRTH) notifications, digital driving licenses, registration certificates, and insurance documents presented via DigiLocker or mParivahan are legally equivalent to original physical documents.",
        "topic": "Traffic Rules and Road Safety",
        "act_name": "Central Motor Vehicles Rules, 1989",
        "section": "Rule 139",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 65,
        "question": "What is the penalty for riding a two-wheeler without a helmet or driving a car without a seatbelt?",
        "answer": "Under Section 194D of the Motor Vehicles Act, riding without a BIS-standard helmet attracts a fine of Rs 1,000 and disqualification of license for 3 months. Under Section 194B, driving or traveling without wearing a safety seatbelt attracts a fine of Rs 1,000.",
        "topic": "Traffic Rules and Road Safety",
        "act_name": "Motor Vehicles Act, 1988",
        "section": "Sections 194B, 194D",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 14: Right to Information (RTI)
    {
        "id": 66,
        "question": "Who can file an RTI application and which public authorities are covered under the RTI Act?",
        "answer": "Under Section 3 of the Right to Information Act, 2005, any Indian citizen can request information from any 'public authority'. Section 2(h) defines public authorities to include bodies established under the Constitution, Parliament, State Legislatures, and bodies substantially financed directly or indirectly by Government funds.",
        "topic": "Right to Information (RTI)",
        "act_name": "Right to Information Act, 2005",
        "section": "Sections 2(h), 3",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 67,
        "question": "What is the statutory time limit for a Public Information Officer (PIO) to respond to an RTI request?",
        "answer": "Under Section 7(1) of the RTI Act, the PIO must provide the requested information or reject the request within 30 days of receiving the application. If the requested information concerns the life or liberty of a person, it must be provided within 48 hours.",
        "topic": "Right to Information (RTI)",
        "act_name": "Right to Information Act, 2005",
        "section": "Section 7(1)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 68,
        "question": "What categories of information are exempt from disclosure under Section 8 of the RTI Act?",
        "answer": "Section 8(1) lists exemptions including information prejudicing sovereignty, integrity, or security of India; information expressly forbidden by court; trade secrets and intellectual property; commercial confidence; fiduciary relationships; cabinet papers; and personal information with no public interest.",
        "topic": "Right to Information (RTI)",
        "act_name": "Right to Information Act, 2005",
        "section": "Section 8(1)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 69,
        "question": "What is the procedure for filing an appeal under the RTI Act if an application is rejected or ignored?",
        "answer": "Under Section 19(1) of the RTI Act, if no response is received within 30 days or the applicant is aggrieved by the PIO's decision, a First Appeal can be filed within 30 days to the First Appellate Authority. If still dissatisfied, a Second Appeal lies to the Central or State Information Commission under Section 19(3) within 90 days.",
        "topic": "Right to Information (RTI)",
        "act_name": "Right to Information Act, 2005",
        "section": "Section 19",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 70,
        "question": "Can an RTI application be filed online for Central Government ministries?",
        "answer": "Yes, citizens can file RTI applications and First Appeals online for all Central Government ministries, departments, and public sector undertakings through the official portal rtionline.gov.in with a fee of Rs 10 (exempt for BPL applicants).",
        "topic": "Right to Information (RTI)",
        "act_name": "Right to Information Act, 2005",
        "section": "Section 6",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 15: Digital Privacy and Data Protection
    {
        "id": 71,
        "question": "What is the Digital Personal Data Protection Act (DPDPA), 2023 and what is its objective?",
        "answer": "The Digital Personal Data Protection Act, 2023 establishes a statutory framework for processing digital personal data in India. It recognizes both the right of individuals (Data Principals) to protect their personal data and the necessity to process such data for lawful purposes.",
        "topic": "Digital Privacy and Data Protection",
        "act_name": "Digital Personal Data Protection Act, 2023",
        "section": "Sections 1, 4",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 72,
        "question": "What rights do citizens have as 'Data Principals' under the DPDPA, 2023?",
        "answer": "Under Sections 11 to 14 of the DPDPA, Data Principals have the Right to access information about their personal data, the Right to correction and erasure, the Right to grievance redressal, and the Right to nominate a representative in the event of death or incapacity.",
        "topic": "Digital Privacy and Data Protection",
        "act_name": "Digital Personal Data Protection Act, 2023",
        "section": "Sections 11-14",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 73,
        "question": "What are the rules regarding notice and consent before collecting personal data under DPDPA?",
        "answer": "Under Sections 5 and 6, personal data can only be processed with free, specific, informed, unconditional, and unambiguous consent, accompanied by a clear notice detailing the personal data to be collected, the purpose of processing, and instructions on how to exercise privacy rights.",
        "topic": "Digital Privacy and Data Protection",
        "act_name": "Digital Personal Data Protection Act, 2023",
        "section": "Sections 5, 6",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 74,
        "question": "What financial penalties can be imposed on entities for data breaches under the DPDPA?",
        "answer": "Under Section 33 and the Schedule of the DPDPA, the Data Protection Board of India can impose substantial penalties: up to Rs 250 crore for failure to take reasonable security safeguards to prevent a personal data breach, and up to Rs 200 crore for failure to notify the Board and affected users of a breach.",
        "topic": "Digital Privacy and Data Protection",
        "act_name": "Digital Personal Data Protection Act, 2023",
        "section": "Section 33",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 75,
        "question": "Is the Right to Privacy recognized as a Fundamental Right in India?",
        "answer": "Yes. In the historic 9-judge bench decision in Justice K.S. Puttaswamy (Retd.) v. Union of India (2017), the Supreme Court unanimously declared that the Right to Privacy is a Fundamental Right intrinsically protected under Article 21 and Part III of the Constitution.",
        "topic": "Digital Privacy and Data Protection",
        "act_name": "Constitution of India",
        "section": "Article 21",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },

    # Topic 16: Banking and Financial Fraud
    {
        "id": 76,
        "question": "What is the legal process under Section 138 of the Negotiable Instruments Act when a cheque bounces?",
        "answer": "When a cheque bounces due to insufficient funds, the payee must issue a statutory demand notice within 30 days of receiving the memo from the bank. If the drawer fails to make payment within 15 days of receiving the notice, a criminal complaint can be filed within 1 month before a Magistrate under Section 138.",
        "topic": "Banking and Financial Fraud",
        "act_name": "Negotiable Instruments Act, 1881",
        "section": "Section 138",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 77,
        "question": "What is the RBI's zero-liability policy for unauthorized electronic banking transactions?",
        "answer": "Under RBI circulars, a customer has zero liability for unauthorized electronic transactions arising from contributory fraud or third-party breaches where the deficiency lies in the system, or when the customer notifies the bank within 3 working days of receiving the transaction alert.",
        "topic": "Banking and Financial Fraud",
        "act_name": "Banking Regulation Act, 1949 / RBI Directives",
        "section": "",
        "source_title": "National Cyber Crime Reporting Portal",
        "source_url": "https://cybercrime.gov.in/"
    },
    {
        "id": 78,
        "question": "What should a customer do if an ATM fails to dispense cash but money is debited from their account?",
        "answer": "According to RBI guidelines, banks must auto-reversal failed ATM transactions within T+5 days (calendar days). If the bank fails to credit the account within 5 days from the transaction date, the cardholder is entitled to compensation of Rs 100 per day of delay.",
        "topic": "Banking and Financial Fraud",
        "act_name": "Payment and Settlement Systems Act, 2007",
        "section": "",
        "source_title": "National Consumer Helpline",
        "source_url": "https://consumerhelpline.gov.in/"
    },
    {
        "id": 79,
        "question": "How can a customer escalate an unresolved bank grievance to the RBI Ombudsman?",
        "answer": "Under the Reserve Bank - Integrated Ombudsman Scheme, if a bank does not respond within 30 days or rejects a complaint, the customer can file a free complaint online at cms.rbi.org.in or by writing to the Centralised Receipt and Processing Centre (CRPC) of RBI.",
        "topic": "Banking and Financial Fraud",
        "act_name": "Reserve Bank - Integrated Ombudsman Scheme, 2021",
        "section": "",
        "source_title": "National Consumer Helpline",
        "source_url": "https://consumerhelpline.gov.in/"
    },
    {
        "id": 80,
        "question": "What legal protections exist against illegal digital lending apps and recovery agent harassment?",
        "answer": "RBI Fair Practices Code prohibits recovery agents from using abusive language, intimidation, calling before 8:00 AM or after 7:00 PM, or contacting a borrower's relatives or friends. Coercive practices and morphing photographs constitute criminal offences under Section 318 and 356 BNS and Section 66 IT Act.",
        "topic": "Banking and Financial Fraud",
        "act_name": "Reserve Bank of India Guidelines / IT Act, 2000",
        "section": "Section 66D",
        "source_title": "National Cyber Crime Reporting Portal",
        "source_url": "https://cybercrime.gov.in/"
    },

    # Topic 17: Tenant and Rental Rights
    {
        "id": 81,
        "question": "What is the Model Tenancy Act and what does it prescribe regarding security deposits?",
        "answer": "The Model Tenancy Act, 2021 aims to balance the rights of landlords and tenants. It caps the security deposit for residential premises at a maximum of two months' rent, and for non-residential commercial premises at a maximum of six months' rent.",
        "topic": "Tenant and Rental Rights",
        "act_name": "Model Tenancy Act, 2021",
        "section": "Section 10",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 82,
        "question": "Can a landlord forcefully disconnect electricity or water supply to evict a tenant?",
        "answer": "No. Under Section 20 of the Model Tenancy Act, 2021 and State Rent Control Acts, no landlord or property manager can withhold or disconnect essential supplies or services (such as water, electricity, or sewerage) to force an eviction. Such actions are illegal, and tenants can approach the Rent Court.",
        "topic": "Tenant and Rental Rights",
        "act_name": "Model Tenancy Act, 2021",
        "section": "Section 20",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 83,
        "question": "What is the standard notice period required to terminate a lease under the Transfer of Property Act?",
        "answer": "Under Section 106 of the Transfer of Property Act, 1882, in the absence of a contract to the contrary, a monthly residential lease can be terminated by giving 15 days notice in writing, while an agricultural or manufacturing lease requires 6 months notice.",
        "topic": "Tenant and Rental Rights",
        "act_name": "Transfer of Property Act, 1882",
        "section": "Section 106",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 84,
        "question": "Is it mandatory to register a rent agreement for a tenancy exceeding 11 months?",
        "answer": "Yes. Under Section 17(1)(d) of the Registration Act, 1908 and Section 107 of the Transfer of Property Act, any lease of immovable property from year to year, or for any term exceeding one year, or reserving a yearly rent, can be made only by a registered instrument.",
        "topic": "Tenant and Rental Rights",
        "act_name": "Registration Act, 1908",
        "section": "Section 17(1)(d)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 85,
        "question": "Who is legally responsible for structural versus day-to-day repairs in a rented property?",
        "answer": "Under Section 15 of the Model Tenancy Act, 2021, the landlord is responsible for structural repairs, major electrical rewiring, and external painting, while the tenant is responsible for minor routine repairs, changing taps, switchboards, and basic fixtures.",
        "topic": "Tenant and Rental Rights",
        "act_name": "Model Tenancy Act, 2021",
        "section": "Section 15",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 18: Legal Complaint Procedures
    {
        "id": 86,
        "question": "What is the difference between a police complaint and a direct private complaint to a Magistrate?",
        "answer": "A police complaint reports an offence to the station house officer for investigation. A private complaint under Section 223 of the BNSS, 2023 (formerly Section 200 CrPC) is made directly before a Magistrate, who examines the complainant on oath and decides whether to take cognizance or order a police investigation under Section 175(3) BNSS.",
        "topic": "Legal Complaint Procedures",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 223 (formerly Section 200 CrPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 87,
        "question": "What is Lok Adalat and how are disputes settled through it?",
        "answer": "Lok Adalat is an alternative dispute resolution mechanism under the Legal Services Authorities Act, 1987. It handles pending court cases and pre-litigation disputes through compromise and conciliation. Awards passed by a Lok Adalat are deemed civil court decrees, are final and binding on all parties, and cannot be appealed.",
        "topic": "Legal Complaint Procedures",
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "Sections 19, 21",
        "source_title": "National Legal Services Authority",
        "source_url": "https://nalsa.gov.in/"
    },
    {
        "id": 88,
        "question": "What is the National Company Law Tribunal (NCLT) and when can an individual or creditor approach it?",
        "answer": "The NCLT is a quasi-judicial body constituted under Section 408 of the Companies Act, 2013 and the Insolvency and Bankruptcy Code, 2016 (IBC). It resolves corporate insolvency, winding up petitions, oppression and mismanagement, and creditor claims against defaulting companies.",
        "topic": "Legal Complaint Procedures",
        "act_name": "Companies Act, 2013",
        "section": "Section 408",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 89,
        "question": "How can a citizen file a grievance on the Central Government CPGRAMS portal?",
        "answer": "CPGRAMS (Centralised Public Grievance Redress and Monitoring System) at pgportal.gov.in is an online 24x7 portal enabling citizens to submit grievances regarding public services delivered by Central and State Government departments, with assigned tracking numbers and time-bound redressal.",
        "topic": "Legal Complaint Procedures",
        "act_name": "Administrative Reforms and Public Grievances Guidelines",
        "section": "",
        "source_title": "National Portal of India",
        "source_url": "https://www.india.gov.in/"
    },
    {
        "id": 90,
        "question": "What is a Cease and Desist notice and what is its legal purpose?",
        "answer": "A Cease and Desist notice is a formal letter sent to an individual or business demanding that they immediately stop an allegedly illegal activity (such as trademark infringement, defamation, or breach of contract) and refrain from repeating it, warning of litigation if ignored.",
        "topic": "Legal Complaint Procedures",
        "act_name": "Code of Civil Procedure, 1908",
        "section": "",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },

    # Topic 19: Police Complaint and FIR Procedures
    {
        "id": 91,
        "question": "What is a First Information Report (FIR) and under what section is it registered?",
        "answer": "An FIR is information recorded by a police officer relating to the commission of a cognizable offence under Section 173 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (which replaced Section 154 of the CrPC). The informant is legally entitled to receive a copy of the FIR free of cost immediately.",
        "topic": "Police Complaint and FIR Procedures",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 173 (formerly Section 154 CrPC)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 92,
        "question": "What is a 'Zero FIR' and can a police station refuse to register it due to jurisdiction?",
        "answer": "A Zero FIR can be registered at any police station irrespective of territorial jurisdiction where the incident occurred, under Section 173(1) of the BNSS, 2023. The police cannot refuse registration for lack of jurisdiction; they must register it, initiate immediate steps, and transfer it to the competent jurisdictional police station.",
        "topic": "Police Complaint and FIR Procedures",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 173(1) (formerly Section 154 CrPC)",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 93,
        "question": "What is an e-FIR and how does the BNSS allow electronic reporting of offences?",
        "answer": "Section 173(1)(ii) of the BNSS, 2023 statutorily recognizes information given electronically (e-FIR). The electronic record must be taken on record and signed by the complainant within 3 days before the FIR is formally registered in offences punishable with 3 to 7 years imprisonment.",
        "topic": "Police Complaint and FIR Procedures",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 173(1)(ii)",
        "source_title": "India Code - Digital Repository of All Central and State Acts",
        "source_url": "https://www.indiacode.nic.in/"
    },
    {
        "id": 94,
        "question": "What remedies are available if a police officer refuses to register an FIR for a cognizable crime?",
        "answer": "If a police officer refuses to record an FIR, the complainant can send the substance of information by post/digitally to the Superintendent of Police (SP) under Section 173(4) BNSS (formerly Section 154(3) CrPC). If still unredressed, an application can be filed before the Judicial Magistrate under Section 175(3) BNSS (formerly Section 156(3) CrPC).",
        "topic": "Police Complaint and FIR Procedures",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 173(4), 175(3) (formerly Sections 154(3), 156(3) CrPC)",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },
    {
        "id": 95,
        "question": "What are the mandatory rights of an arrested person under the BNSS and D.K. Basu guidelines?",
        "answer": "Under Sections 37, 47, and 48 of the BNSS, 2023 (incorporating D.K. Basu principles), the arrested person has the right to know grounds of arrest, the right to have a friend/relative informed immediately, the right to consult an advocate, and the right to mandatory medical examination upon arrest.",
        "topic": "Police Complaint and FIR Procedures",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Sections 37, 47, 48 (formerly Sections 41B, 50, 50A CrPC)",
        "source_title": "Supreme Court of India Official Portal",
        "source_url": "https://www.sci.gov.in/"
    },

    # Topic 20: Legal Aid and Access to Justice
    {
        "id": 96,
        "question": "Who is eligible for free legal aid in India under Section 12 of the Legal Services Authorities Act?",
        "answer": "Section 12 of the Legal Services Authorities Act, 1987 entitles women, children, members of SC/ST, victims of human trafficking or beggar, persons with disabilities, victims of mass disasters/violence, industrial workmen, persons in custody, and citizens with annual income below prescribed statutory thresholds to free legal aid.",
        "topic": "Legal Aid and Access to Justice",
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "Section 12",
        "source_title": "National Legal Services Authority",
        "source_url": "https://nalsa.gov.in/"
    },
    {
        "id": 97,
        "question": "How can an eligible citizen apply for free legal representation through NALSA or DLSA?",
        "answer": "Eligible citizens can apply online via the NALSA portal (nalsa.gov.in), call the national legal aid helpline 15100, or visit their nearest District Legal Services Authority (DLSA) or Taluk Legal Services Committee located inside court premises. NALSA assigns a panel lawyer free of cost.",
        "topic": "Legal Aid and Access to Justice",
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "Sections 12, 13",
        "source_title": "National Legal Services Authority",
        "source_url": "https://nalsa.gov.in/"
    },
    {
        "id": 98,
        "question": "What is Tele-Law and how does it deliver pre-litigation legal advice in rural areas?",
        "answer": "Tele-Law is a Government of India Department of Justice initiative operating through Common Service Centres (CSCs). Citizens in rural and remote areas can consult panel lawyers via video conferencing and telephone for advice on rights and dispute resolution before taking disputes to court.",
        "topic": "Legal Aid and Access to Justice",
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "",
        "source_title": "National Legal Services Authority",
        "source_url": "https://nalsa.gov.in/"
    },
    {
        "id": 99,
        "question": "What are Permanent Lok Adalats and what types of public utility cases do they handle?",
        "answer": "Established under Section 22B of the Legal Services Authorities Act, Permanent Lok Adalats provide conciliation and adjudication for public utility services including transport, postal, telegraph, telephone, power, light, water, sanitation, and hospital services for disputes up to Rs 1 crore.",
        "topic": "Legal Aid and Access to Justice",
        "act_name": "Legal Services Authorities Act, 1987",
        "section": "Section 22B",
        "source_title": "National Legal Services Authority",
        "source_url": "https://nalsa.gov.in/"
    },
    {
        "id": 100,
        "question": "Does an accused person in criminal custody have a constitutional right to legal aid at state expense?",
        "answer": "Yes. Article 39A of the Constitution guarantees equal justice and free legal aid. The Supreme Court in Khatri (II) v. State of Bihar and Section 341 of BNSS, 2023 (formerly Section 304 CrPC) mandate that if an accused has insufficient means to engage an advocate, the court must assign an advocate at the expense of the State.",
        "topic": "Legal Aid and Access to Justice",
        "act_name": "Constitution of India & BNSS, 2023",
        "section": "Article 39A & Section 341 BNSS (formerly Section 304 CrPC)",
        "source_title": "National Legal Services Authority",
        "source_url": "https://nalsa.gov.in/"
    }
]

def generate_csv():
    """Write the dataset to CSV format."""
    fieldnames = [
        "id", "question", "answer", "topic", "act_name",
        "section", "source_title", "source_url"
    ]
    with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in FAQ_DATA:
            writer.writerow(item)
    print(f"Successfully generated {len(FAQ_DATA)} records at: {CSV_PATH}")

if __name__ == "__main__":
    generate_csv()
