import re
import docx
import ast
import os
from brief_argument.models import default_embeddings
import openai
from openai import OpenAI
import google.generativeai as genai
import lxml.etree
from django.template.loader import render_to_string
from django.db.models import Q, Prefetch
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from brief_argument.scraper2 import run_playwright
from legal_gpt import settings
from case_history.models import LawTopics
from brief_argument.models import (
    HulsburyLawBooks,
    Case,
    CaseNote,
    Caseparagraph,
)
from legal_gpt import settings
INPUT_TOPICS = """Law 1 Constitutional Law:
    Topic 1.01 Constitution and Constitutionalism Size:14102,
    Topic 1.02 Nature of Indian Constitution and Concept of Federalism Size:20192,
    Topic 1.03 The Union and its Territories Size:11768,
    Topic 1.04 Union and State Executive Size:40215,
    Topic 1.05 LEGISLATIVE POWER OF THE EXECUTIVE (ORDINANCES) Size:11263,
    Topic 1.06 Parliament and State Legislatures Size:16698,
    Topic 1.07 The Union and State Judiciary Size:54864,
    Topic 1.08 Distribution of Powers between Centre and States (Articles 245-254) Size:24678,
    Topic 1.09 Freedom of Trade, Commerce and Intercourse Size:12408,
    Topic 1.10 Emergency Provisions Size:13891,
    Topic 1.11 CIVIL SERVANTS (Articles 308-323) Size:4152,
    Topic 1.12 THE AMENDMENT OF THE CONSTITUTION (Article 368) Size:21918,
    Topic 1.13 DIRECTIVE PRINCIPLES OF STATE POLICY (Articles 36-51) Size:4557,
    Topic 1.14 FUNDAMENTAL DUTIES (Article 51A) Size:1980,
    Topic 1.15 RIGHT TO CONSTITUTIONAL REMEDIES (Article 32) Size:7717,
    Topic 1.16 CULTURAL AND EDUCATIONAL RIGHTS (Articles 29-30) Size:10760,
    Topic 1.17 RIGHT TO FREEDOM OF RELIGION (Articles 25-28) Size:9622,
    Topic 1.18 RIGHT AGAINST EXPLOITATION (Articles 23-24) Size:1515,
    Topic 1.19 Right to Freedom (Articles 19-22) Size:54975,
    Topic 1.20 RIGHT TO EQUALITY (Articles 14-18) Size:49262,
    Topic 1.21 FUNDAMENTAL RIGHTS: MEANING OF STATE AND LAW (Articles 12-13) Size:29406,
    Law 2 CPC:
    Topic 2.01 Definitions: Section 2 (Judgment, Decree, Order, Legal Representative, Mesne Profits) Size:12530,
    Topic 2.02 Power of Transfer Suits (Sections 22, 23, 24 and 25) Size:8205,
    Topic 2.03 Attachment of Property (Sections 60 to 64 ; Order 21, Rules 41 to 57) Size:8417,
    Topic 2.04 Commission (Sections 75 to 78 ; Order 26) Size:4956,
    Topic 2.05 Suits by or against Government (Sections 79 to 82 ; Order 27) Size:5354,
    Topic 2.06 Appeals in General (Sections 96 to 112 ; Orders 41 to 45) Size:15738,
    Topic 2.07 Production of Additional Evidence in Appellate Court [Section 107(1)(d) and Order 41] Size:8211,
    Topic 2.08 Second Appeal (Appeals from Appellate Decrees) (Sections 100 to 103 and Order 42) Size:13176,
    Topic 2.09 Reference, Review and Revision (Sections 113, 114, 115 and Orders 46, 47) Size:18238,
    Topic 2.10 Inherent Powers of a Court (Sections 148 to 153A) Size:12022,
    Topic 2.11 Parties to Suits (Order 1, Rules 1 to 13) Size:11074,
    Topic 2.12 Institution of Suits (Order 4 and Section 26) Size:3507,
    Topic 2.13 Pleadings: Meaning, Object, General Rules (Order 6, Rules 1 to 16) Size:7785,
    Topic 2.14 Amendment of Pleadings (Order 6, Rules 17 & 18) Size:14183,
    Topic 2.15 Plaint (Order 7, Rules 1 to 18) Size:9799,
    Topic 2.16 Written Statement, Set-off & Counter Claim (Order 8, Rules 1 to 10) Size:9186,
    Topic 2.17 Appearance of Parties and Consequences of Non-appearance (Order 9, Rules 1 to 14) Size:19490,
    Topic 2.18 Suits / Appeals by Indigent Persons (Orders 33 and 44) Size:4226,
    Topic 2.19 Interpleader Suits (Order 335 and Section 88) Size:1689,
    Topic 2.20 Summary Procedure (Order 37, Rules 1 to 7) Size:9500,
    Topic 2.21 Temporary Injunction and Interlocutory Orders (Order 39, Rules 1 to 10) Size:17400,
    Topic 2.22 Receiver [Order 40, Section 94(d)] Size:3605,
    Topic 2.23 Affidavits, Restitution, Caveat [Order 19 ; Section 114 ; Section 148A] Size:4022,
    Topic 2.24 Jurisdiction of Civil Courts (Sections 3, 6 and 9) Size:16642,
    Topic 2.25 Res Sub Judice : Stay of Suit (Section 10) Size:5877,
    Topic 2.26 Foreign Judgment [Section 2(5) & (6), 13, 14 & 44A] Size:8936,
    Topic 2.27 Res Judicata: Bar of Suit (Section 11) Size:31199,
    Topic 2.28 An Introduction to the Civil Procedure Code (Sections 1, 4 & 5, 7 & 8) Size:9428,
    Topic 2.29 Place of Suing (Sections 15, 16 to 20, 21-21A) Size:14789,
    Law 3 Law of Evidence:
    Topic 3.01 An Introduction to the Law of Evidence and Interpretation Clause (Sections 3 and 4) Size:17435,
    Topic 3.02 Relevancy of Facts [Sections 5 to 16 ((CONSPIRACY: ALIBI; DAMAGES; RIGHT / CUSTOM; PSYCHOLOGICAL FACTS; SIMILAR OCCURRENCES; COURSE OF BUSINESS))] Size:39312,
    Topic 3.03 Admissions (Sections 17 to 23 and 31) Size:15392,
    Topic 3.04 Confession (Section 24 to 30) (Stated Type Relevant Facts) Size:26754,
    Topic 3.05 Dying Declarations (DD) [Sections 32(1)] Size:15675,
    Topic 3.06 Expert Evidence (Opinion of Experts) (Relevancy of Opinion of third persons) Size:14879,
    Topic 3.07 Relevancy of Character (Sections 52, 53, 53A, 54 & 55) Size:4989,
    Topic 3.08 Facts which need not be Proved (Sections 56, 57 & 58) Size:2421,
    Topic 3.09 Means / Modes of Proof : Oral Evidence (Sections 59 and 60) Size:6293,
    Topic 3.10 Means / Modes of Proof : Documentary Evidence (Sections 61 to 78) Size:12332,
    Topic 3.11 Exclusion of Oral Evidence by Documentary Evidence (Sections 91 to 100) Size:14256,
    Topic 3.12 Burden of Proof [who has the burden of bringing / adducing facts before the court] (Sections 3, 101 to 111) Size:13350,
    Topic 3.13 Presumptions (Rules limiting Judicial freedom of drawing inference) [Sections 4, 41, 79-90A, 111A to 114] Size:25536,
    Topic 3.14 Doctrine of Estoppel (Sections 115, 116, and 117) [Facts which the parties are Prohibited from Proving] Size:21275,
    Topic 3.15 Privileged Communications (Sections 121 to 132) Size:17409,
    Topic 3.16 Accomplice / Approver Evidence [Sections 133 and 114(b)] Size:15591,
    Topic 3.17 Competency and Sufficiency of Witnesses (Sections 118, 119, 120 & 134) Size:8462,
    Topic 3.18 Examination of Witnesses (Sections 135 to 140 & 154, 155) Size:15934,
    Law 4 Competition Law:
    Topic 4.01 Introduction of Competition Law Size:5960,
    Topic 4.02 History and Development of Competition Law Size:24229,
    Topic 4.03 Anti-Competitive Agreements [Section 3] Size:35946,
    Topic 4.04 Regulation of Abuse of Dominant Position (Section 4) Size:29980,
    Topic 4.05 Regulation of Combinations (Section 5 & 6) Size:15706,
    Topic 4.06 Enforcement Mechanisms Size:27795,
    Topic 4.07 Competition Advocacy and Leniency Programme Size:6864,
    Topic 4.08 Emerging Trends In Competition Law (National and International) Size:10600,
    Law 5 Taxation Laws:
    Topic 5.01 Preliminary and Previous Year Size:26193,
    Topic 5.02 Residential Status and Tax Incidence Size:13101,
    Topic 5.03 Agricultural Income Size:12504,
    Topic 5.04 Heads of Income-Salaries Size:15972,
    Topic 5.05 Income from House Property Size:14364,
    Topic 5.06 Profits and Gains of Business or Profession Size:37920,
    Topic 5.07 Capital Gains Size:25493,
    Topic 5.08 Income from Other Sources Size:5958,
    Topic 5.09 Income of Other Persons Included in Assessee's Total Income Size:7492,
    Topic 5.10 Set-off and Carry Forward of Losses Size:6208,
    Topic 5.11 Assessment Size:29042,
    Topic 5.12 GST-Overview Size:2228,
    Law 6 Property Law:
    Topic 6.01 Movable and Immovable Property Size:8755,
    Topic 6.02 Attestation Size:8946,
    Topic 6.03 Doctrine of Notice Size:15700,
    Topic 6.04 Transfer of Property (Section 5) Size:16728,
    Topic 6.05 Transferable Property [Section 6(a) and 43] Size:16372,
    Topic 6.06 Conditional Transfers (Conditions Repugnant to Interest Created) (Sections 10, 11, 12, & 40) Size:18412,
    Topic 6.07 Rule against perpetuities (Transfer for the benefit of Unborn Person) (Sections 13 to 18, 20 & 22) Size:16609,
    Topic 6.08 Vested and Contingent Interest (Sections 19 and 21) Size:9470,
    Topic 6.09 Transfer During Pendency of Litigation (Rule/Doctrine of Lis Pendens) (Section 52) Size:16481,
    Topic 6.10 Mortgages (Chapter 4: Sections 58 to 104) Size:26588,
    Topic 6.11 Lease and License (Sections 105 & 106, TPA; Sections 52, Indian Easement Act, 1882) Size:19005,
    Topic 6.12 GIFT (Sections 122-129) Size:20312,
    Law 7 Family Law - 1:
    Topic 7.01 Nature of Hindu Law Size:3111,
    Topic 7.02 Sources and Schools of Hindu Law Size:5746,
    Topic 7.03 Hindu Law of Marriage Size:44543,
    Topic 7.04 Restitution of Conjugal Rights Size:16755,
    Topic 7.05 Judicial Separation Size:4152,
    Topic 7.06 Divorce: A Matrimonial Relief Size:45928,
    Topic 7.07 Hindu Law of Maintenance Size:18637,
    Topic 7.08 Hindu Law of Adoption Size:15187,
    Topic 7.09 Legitimacy of Children of Void and Voidable Marriage Size:3522,
    Topic 7.10 Minority, Guardianship and Custody Size:9154,
    Topic 7.11 Sources and Schools of Muslim Law Size:7312,
    Topic 7.12 Muslim Law of Marriage (Nikah) Size:24844,
    Topic 7.13 Muslim Law of Divorce Size:29595,
    Topic 7.14 Muslim Law of Maintenance Size:14223,
    Topic 7.15 Acknowledgement of Paternity and Legitimacy Size:4417,
    Topic 7.16 Wakfs and Endowments Size:7784,
    Law 8 Intellectual Property Law:
    Topic 8.01 Assignment and Licenses of Copyright Size:12622,
    Topic 8.02 Introduction to Intellectual Property Rights, and International Agreements in the Field of Copyright and Patents Size:18994,
    Topic 8.03 Copyright Size:14083,
    Topic 8.04 Classes of Works in which Copyright Subsists or The Subject Matter of Copyright Size:21271,
    Topic 8.05 Rights Conferred by Copyright Size:13294,
    Topic 8.06 Ownership of Copyright Size:8752,
    Topic 8.07 Collective Management of Copyright by Copyright Societies [Sections 32-35] Size:3281,
    Topic 8.08 Infringement of Copyright Size:5798,
    Topic 8.09 International Copyright Order, 1999 Size:2739,
    Topic 8.10 Permitted Uses/Fair Dealing Size:12841,
    Topic 8.11 Origin of Patent Size:11231,
    Topic 8.12 Procedure for Filling Patent Applications Size:6852,
    Topic 8.13 Grounds of Opposition and Revocation Size:7656,
    Topic 8.14 Rights of Patentee Size:1716,
    Topic 8.15 Revocation of Patent [Sections 64] Size:2063,
    Topic 8.16 Infringement of Patents Size:4302,
    Topic 8.17 Compulsory Licensing and Parallel Importing Size:3529,
    Topic 8.18 Law of Plant Varieties and Farmer's Rights Size:11558,
    Topic 8.19 Trade Secret/Confidential Information Size:2765,
    Topic 8.20 Traditional Knowledge Size:4362,
    Topic 8.21 Semiconductor Integrated Circuits Layout Design Act 200 Size:2349,
    Topic 8.22 Introduction to the Intellectual Property Size:5802,
    Topic 8.23 Abuse of Intellectual Property-Concept, Redress under Article 40 of TRIPS and Competition Law Size:5572,
    Topic 8.24 International Legal Instruments Relating to IPR Size:12374,
    Topic 8.25 Fundamentals of Trademark Size:4045,
    Topic 8.26 Statutory Definition of Trade Mark [Section 2(1)(zb)] Size:7148,
    Topic 8.27 Protecting Domain Names as Trade Marks Size:3930,
    Topic 8.28 Trade Marks for Services Size:4945,
    Topic 8.29 Registration of Trade Marks for Goods/Services Size:1962,
    Topic 8.30 Requisites for Registration and Grounds of Refusal of Registration Size:45308,
    Topic 8.31 Infringement and Passing off of Trademarks and Transborder Reputation Size:26182,
    Topic 8.32 Trade Dress and Colour Combination, Disparagement, Comparative Advertising, Dilution or Tarnishment of Trademark and Exhaustion of Intellectual Property Rights Size:6799,
    Topic 8.33 Licensing of Trademarks [Sections 48 to 56] Size:2110,
    Topic 8.34 Geographical Indications of Goods (Registration and Protection Act, 1999) Size:8701,
    Topic 8.35 Industrial Designs Law Size:12721,
    Law 9 Law of Crimes - 3:
    Topic 9.01 An Introduction to Socio-Economic Offences and White Collar Crimes Size:13566,
    Topic 9.02 The Immoral Traffic (Prevention) Act, 1956 Size:23822,
    Topic 9.03 The Narcotic Drugs and Psychotropic Substances Act, 1985 Size:39957,
    Topic 9.04 The Food Safety and Standards Act, 2006 Size:20212,
    Topic 9.05 The prevention of Corruption Act, 1988 Size:18432,
    Topic 9.06 The Prevention of Money Laundering Act, 2002 Size:8413,
    Topic 9.07 Special Courts (Sections 43 to 47) Size:8755,
    Law 10 Labour Law:
    Topic 10.01 The Trade Unions Act, 1926 Size:32124,
    Topic 10.02 Industry Size:32694,
    Topic 10.03 Industrial Dispute Size:10468,
    Topic 10.04 Workman Size:29382,
    Topic 10.05 Strikes and Lock-nuts Size:24825,
    Topic 10.06 Lay-off, Retrenchment and Closure Size:34420,
    Topic 10.07 Dispute Settlement under the Industrial Disputes Act Size:13334,
    Topic 10.08 Awards and Settlements Size:8610,
    Topic 10.09 The Industrial Employment (Standing Orders) Act, 1946 Size:5010,
    Topic 10.10 DISPUTE SETTLEMENT UNDER THE INDUSTRIAL DISPUTES ACT Size:17326,
    Topic 10.11 REFERENCE OF THE INDUSTRIAL DISPUTE Size:20080,
    Topic 10.12 AWARDS AND SETTLEMENTS Size:19830,
    Topic 10.13 MANAGERIAL PREROGATIVE AND DISCIPLINARY ACTION Size:11404,
    Topic 10.14 RESTRAINTS ON MANAGERIAL PREROGATIVES Size:2895,
    Topic 10.15 POWERS OF THE ADJUDICATORY AUTHORITIES Size:6289,
    Topic 10.16 CONCEPT OF WAGE, KINDS OF WAGES AND THE MINIMUM WAGES ACT, 1948 Size:11595,
    Topic 10.17 THE PAYMENT OF WAGES ACT, 1936 Size:6530,
    Topic 10.18 EQUAL REMUNERATION ACT, 1976 Size:5750,
    Topic 10.19 EMPLOYEES' COMPENSATION ACT, 1923 Size:39791,
    Topic 10.20 THE EMPLOYEES' STATE INSURANCE ACT, 1948 Size:8042,
    Topic 10.21 THE PAYMENT OF BONUS ACT, 1965 Size:20672,
    Topic 10.22 THE PAYMENT OF GRATUITY ACT, 1972 Size:11650,
    Topic 10.23 MATERNITY BENEFIT ACT, 1961 Size:12049,
    Topic 10.24 THE FACTORIES ACT, 1948 Size:15701,
    Law 11 Contract Law:
    Topic 11.01 REMEDIES FOR BREACH OF CONTRACT Size:21398,
    Topic 11.02 QUASI CONTRACTS OR CERTAIN RELATIONS RESEMBLING THOSE CREATED BY CONTRACT Size:8516,
    Topic 11.03 E-CONTRACT Size:6028,
    Topic 11.04 NATURE AND KINDS OF CONTRACTS Size:9605,
    Topic 11.05 OFFER AND ACCEPTANCE Size:33912,
    Topic 11.06 CONSIDERATION AND PRIVITY OF CONTRACT CONSIDERATION Size:14353,
    Topic 11.07 CAPACITY OF PARTIES Size:11779,
    Topic 11.08 FREE CONSENT Size:30975,
    Topic 11.09 LEGALITY OF OBJECT AND CONSIDERATION Size:9777,
    Topic 11.10 AGREEMENTS EXPRESSLY DECLARED VOID Size:11106,
    Topic 11.11 CONTINGENT CONTRACTS Size:2195,
    Topic 11.12 PERFORMANCE OF CONTRACTS Size:8129,
    Topic 11.13 DISCHARGE OF CONTRACTS Size:16074,"""


def get_step_1_input(topics, facts, legal_issue):
    return f"""You are a legal researcher tasked with finding the most relevant and applicable law topics for a particular legal case. To assist you, I will provide three key pieces of information: <allLawTopics> {topics}</allLawTopics> <facts>{facts} </facts><legalIssue>{legal_issue}</legalIssue>Please follow these steps carefully:1. Read the facts of the case and the legal issue thoroughly to fully understand the details and context of the case.2. Review the provided list of law topics, paying close attention to how they are segmented and described. Make sure you have a clear grasp of what each topic entails.3. Select the law topics that are most relevant and applicable to the case at hand, based on your analysis of the facts and the legal issue that needs to be addressed.4. Check the cumulative size of your selected law topics. If the total size exceeds 100000, carefully deselect the least relevant and applicable topics from your list until the cumulative size is reduced to 125000 or below.5. Provide your final curated list of the most relevant and applicable law topics for this case inside <selected_law_topics> tags, formatted as follows:<selected_law_topics>[list the relevant and applicable law topics here]</selected_law_topics>Remember, your goal is to identify the law topics that are most pertinent and useful for addressing the legal issue, given the specific facts of the case. Carefully consider the relevance and applicability of each topic before making your final selections.  Strictly give response as per the given sample response format Sample Response Format:            <selected_law_topics>            Topic 1.02: "Topic_1.02_name"-"topic_1.02_size"           Topic 1.04: "Topic_1.04_name"-"topic_1.04_size"           Topic 9.03: "Topic_9.03_name"-"topic_9.03_size"             Total size: topic_1.02_size + topic_1.04_size + topic_9.03_size            </selected_law_topics>"""


def get_step_2_input_with_lr(relevent_topics, facts, legal, research):
    return f"""You are a legal researcher tasked with drafting a legal memorandum for a particular case. To
        complete this task, please follow these steps:

        1. Carefully read and understand the statement of law provided:

        <statement_of_law>
        {relevent_topics}
        </statement_of_law>

        2. Carefully read and understand the legal research material provided:

        <legal_research>
        {research}
        </legal_research>

        3. Study the facts of the case:

        <facts_of_the_case>
        {facts}
        </facts_of_the_case>

        4. Consider the legal question to be addressed:

        <legal_question>
        {legal}
        </legal_question>

        5. Before proceeding, take time to thoroughly understand the statement of law, legal research
        material, facts of the case, and the legal question.

        6. Structure your legal memorandum as follows:

        !%!Question Presented!%!  
        - Formulate a specific and impartial question that captures the core legal issue without assuming a
        legal conclusion.

        !%!Statement of Facts!%!  
        - Provide a concise, impartial summary of the key facts relevant to the legal matter, approximately
        200 words in length.
        - Include current and past legal proceedings related to the issue.
        - Present the facts chronologically or grouped thematically, whichever format offers the clearest
        understanding.

        !%!Analysis!%!  
        - Provide a well-reasoned legal analysis that discusses the application of the relevant law to the
        facts of the case. Be sure to incorporate the applicable legal principles (statutes and case laws)
        from the statement of law and legal research material.
        - Divide the analysis into subsections, each addressing a specific legal topic relevant to the case.
        - For each topic, clearly state the applicable law and relevant facts in an active voice and present
        your analysis in a logical manner.
        - The total length of the Analysis section should be approximately 2000 words.
        - Subsection titles must be enclosed in |$| tags as in |$|subsection_title|$|.

        !%!Conclusion!%!  
        - In approximately 300 words, predict how the court will likely apply the law based on your
        analysis.
        - Before providing your prediction, express your level of confidence in the prediction based on the
        available information.
        - Using an impartial advisory tone, identify next steps and propose a legal strategy to proceed.

        7. Provide your complete legal memorandum inside <legal_memorandum> tags.

        Remember, the key is providing a thorough and well-reasoned legal analysis that ties together the
        relevant law, the facts of this case, and your application of that law to those facts to address the
        stated legal question. Your memorandum should demonstrate a clear understanding of the legal issues
        at hand and provide valuable insights for the reader.

        Strictly follow the instructions and structure the legal memorandum as per the given format.
"""


def get_step_2_input_without_lr(relevent_topics, facts, legal):
    return f"""
        You are a legal researcher tasked with drafting a legal memorandum for a particular case. To
        complete this task, please follow these steps:

        1. Carefully read and understand the statement of law provided:

        <statement_of_law>
        {relevent_topics}
        </statement_of_law>

        2. Study the facts of the case:

        <facts_of_the_case>
        {facts}
        </facts_of_the_case>

        3. Consider the legal question to be addressed:

        <legal_question>
        {legal}
        </legal_question>

        4. Before proceeding, take time to thoroughly understand the statement of law, facts of the case, and the legal question.

        5. Structure your legal memorandum as follows:

        !%!Question Presented!%!  
        - Formulate a specific and impartial question that captures the core legal issue without assuming a
        legal conclusion.

        !%!Statement of Facts!%!  
        - Provide a concise, impartial summary of the key facts relevant to the legal matter, approximately
        200 words in length.
        - Include current and past legal proceedings related to the issue.
        - Present the facts chronologically or grouped thematically, whichever format offers the clearest
        understanding.

        !%!Analysis!%!  
        - Provide a well-reasoned legal analysis that discusses the application of the relevant law to the
        facts of the case. Be sure to incorporate the applicable legal principles (statutes and case laws)
        from the statement of law.
        - Divide the analysis into subsections, each addressing a specific legal topic relevant to the case.
        - For each topic, clearly state the applicable law and relevant facts in an active voice and present
        your analysis in a logical manner.
        - The total length of the Analysis section should be approximately 2000 words.
        - Subsection titles must be enclosed in |$| tags as in |$|subsection_title|$|.

        !%!Conclusion!%!  
        - In approximately 300 words, predict how the court will likely apply the law based on your
        analysis.
        - Before providing your prediction, express your level of confidence in the prediction based on the
        available information.
        - Using an impartial advisory tone, identify next steps and propose a legal strategy to proceed.

        7. Provide your complete legal memorandum inside <legal_memorandum> tags.

        Remember, the key is providing a thorough and well-reasoned legal analysis that ties together the
        relevant law, the facts of this case, and your application of that law to those facts to address the
        stated legal question. Your memorandum should demonstrate a clear understanding of the legal issues
        at hand and provide valuable insights for the reader.

        Strictly follow the instructions and structure the legal memorandum as per the given format.
    """


def get_step_3_input_with_lr(
    legal_memo, selected_laws, facts, legal, title, content, research
):
    legal_memo = legal_memo.replace("<p>", "")
    legal_memo = legal_memo.replace("</p>", "")
    legal_memo = legal_memo.replace("<br>!%!", "")
    legal_memo = legal_memo.replace("<!%!<br>", "")
    legal_memo = legal_memo.replace("|$|<br>", "")
    legal_memo = legal_memo.replace("<br>|$|", "")
    legal_memo = legal_memo.replace("<br>-", " ")
    legal_memo = legal_memo.replace("<br>", " ")
    content = content.replace("<p>", "")
    content = content.replace("</p>", "")
    return f"""You will be drafting the expanded {title} part of the Analysis section of a legal memorandum. This should be a detailed legal analysis discussing the application of the relevant law to the facts of the case, backed by sound legal reasoning. First, carefully read through the full legal memorandum provided: <legal_memorandum> {legal_memo} </legal_memorandum> Next, review the key statement of law that applies to this case: <statement_of_law> {selected_laws} </statement_of_law>review the legal research material that applies to this case: <legal_research> {research} </legal_research>   Now read through the important facts of the case: <facts_of_the_case> {facts} </facts_of_the_case> Keep in mind that your analysis should address this core legal question: <legal_question> {legal} </legal_question> Re-read the current version of the {title} subsection: {title} {content} Before drafting your expanded subsection, take time in a <scratchpad> to thoroughly analyze how the statement of law, and the legal research material applies to the facts of this case. Consider what legal principles are most relevant from the statement of law and the legal research material and which specific facts are most pertinent. Write out your thought process and reasoning here. Now, please draft the expanded {title} subsection of the legal memorandum in detail: - Provide a well-reasoned legal analysis that discusses the application of the relevant law to the facts of the case. Be sure to incorporate the applicable legal principles (statutes and case laws) from the statement of law and the legal research material. - Divide the analysis into subsections, each addressing a specific legal topic relevant to the case. - For each topic, clearly state the applicable law and relevant facts in an active voice and present your analysis in a logical manner. Provide your complete draft inside <subsection> tags. Remember, the key is providing a thorough and well-reasoned legal analysis that ties together the relevant law, the facts of this case, and your application of that law to those facts to address the stated legal question. Incorporate your scratchpad notes and reasoning into a polished final subsection draft."""


def get_step_3_input_without_lr(
    legal_memo, selected_laws, facts, legal, title, content
):
    legal_memo = legal_memo.replace("<p>", "")
    legal_memo = legal_memo.replace("</p>", "")
    legal_memo = legal_memo.replace("<br>!%!", "")
    legal_memo = legal_memo.replace("<!%!<br>", "")
    legal_memo = legal_memo.replace("|$|<br>", "")
    legal_memo = legal_memo.replace("<br>|$|", "")
    legal_memo = legal_memo.replace("<br>-", " ")
    legal_memo = legal_memo.replace("<br>", " ")
    content = content.replace("<p>", "")
    content = content.replace("</p>", "")
    return f"""
        You will be drafting the expanded {title} part of the Analysis section of a legal memorandum. This should be a detailed legal analysis discussing the application of the relevant law to the facts of the case, backed by sound legal reasoning. First, carefully read through the full legal memorandum provided: <legal_memorandum> {legal_memo} </legal_memorandum> Next, review the key statement of law that applies to this case: <statement_of_law> {selected_laws} </statement_of_law> Now read through the important facts of the case: <facts_of_the_case> {facts} </facts_of_the_case> Keep in mind that your analysis should address this core legal question: <legal_question> {legal} </legal_question> Re-read the current version of the {title} subsection: {title} {content} Before drafting your expanded subsection, take time in a <scratchpad> to thoroughly analyze how the statement of law applies to the facts of this case. Consider what legal principles are most relevant from the statement of law and which specific facts are most pertinent. Write out your thought process and reasoning here. Now, please draft the expanded {title} subsection of the legal memorandum in detail: - Provide a well-reasoned legal analysis that discusses the application of the relevant law to the facts of the case. Be sure to incorporate the applicable legal principles (statutes and case laws) from the statement of law. - Divide the analysis into subsections, each addressing a specific legal topic relevant to the case. - For each topic, clearly state the applicable law and relevant facts in an active voice and present your analysis in a logical manner. Provide your complete draft inside <subsection> tags. Remember, the key is providing a thorough and well-reasoned legal analysis that ties together the relevant law, the facts of this case, and your application of that law to those facts to address the stated legal question. Incorporate your scratchpad notes and reasoning into a polished final subsection draft.

        """


def get_step_3_input(legal_memo, selected_laws, facts, legal, title, content):
    legal_memo = legal_memo.replace("<p>", "")
    legal_memo = legal_memo.replace("</p>", "")
    legal_memo = legal_memo.replace("<br>!%!", " !%!")
    legal_memo = legal_memo.replace("<!%!<br>", "!%! ")
    legal_memo = legal_memo.replace("|$|<br>", " <br>")
    legal_memo = legal_memo.replace("<br>|$|", " |$|")
    legal_memo = legal_memo.replace("<br>-", " ")
    legal_memo = legal_memo.replace("<br>", " ")
    content = content.replace("<p>", "")
    content = content.replace("</p>", "")
    return f"""
        You are tasked with drafting the {title} part of the Analysis section of a legal
        memorandum. Here is the full legal memorandum for context:

        <legal_memorandum>
        {legal_memo}
        </legal_memorandum>

        Please carefully read and understand the following statement of law:

        <statement_of_law>
        {selected_laws}
        </statement_of_law>

        Here are the relevant facts of the case:

        <facts_of_the_case>
        {facts}
        </facts_of_the_case>

        The legal question to be addressed is:

        <legal_question>
        {legal}
        </legal_question>

        Please re-read the legal memorandum, paying close attention to this subsection:

        {title}
        {content}

        Before drafting your subsection, take time in a <scratchpad> to thoroughly analyze how the statement
        of law applies to the facts of this case. Consider what legal principles are most relevant from the
        statement of law and which specific facts are most pertinent. Write out your thought process.

        <scratchpad>
        </scratchpad>

        Now, please draft the {title} subsection of the legal memorandum. Provide a
        well-reasoned legal analysis that discusses the application of the relevant law to the facts of the
        case. Be sure to incorporate the applicable legal principles (statutes and case laws) from the
        statement of law. Clearly state the law and facts in an active voice and present your analysis in a
        logical flow.

        Provide your complete draft inside <subsection> tags.

        <subsection>
        </subsection>

        Remember, the key is providing a thorough and well-reasoned legal analysis that ties together the
        relevant law, the facts of this case, and your application of that law to those facts to address the
        stated legal question. Incorporate your scratchpad notes into a polished final subsection draft.
        """


def send_legal_memo_detail(legal_memo, *args, **kwargs):
    legal = legal_memo.legal
    facts = legal_memo.facts
    detailed_analyis = legal_memo.analysis.all()
    conclusion = legal_memo.conclusion
    html_content = render_to_string(
        "email/legal_memo_detailed.html",
        context={
            "legal": legal,
            "facts": facts,
            "analysis": detailed_analyis,
            "conclusion": conclusion,
            "id": legal_memo.id,
            "domain_name": settings.ALLOWED_HOSTS[0],
        },
    )
    subject = "Legal Memorandum Detailed"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [
        # "rithikchaudhary150500@gmail.com",
        # "jishnusai99@gmail.com",
        "iammgautam@gmail.com",
    ]
    message = EmailMultiAlternatives(
        subject, body="", from_email=from_email, to=recipient_list
    )
    message.attach_alternative(html_content, "text/html")
    try:
        message.send()
        return True
    except EmailBackend.RecipientRefused:
        return False


def aib_exam__step_1_input(question, option_a, option_b, option_c, option_d):
    return f"""You are a legal researcher tasked with finding the most relevant and applicable law topics to answer
        a multiple choice question.

        First, carefully read the full list of available law topics, paying close attention to how they are
        segmented and described:

        <allLawTopics>
        {INPUT_TOPICS}
        </allLawTopics>

        Next, read the question text thoroughly to fully understand what is being asked:

        <question>
        {question}
        </question>

        Now read through each of the answer options carefully:

        <option_a>
        {option_a}
        </option_a>

        <option_b>
        {option_b}
        </option_b>

        <option_c>
        {option_c}
        </option_c>

        <option_d>
        {option_d}
        </option_d>

        Based on your analysis of the question and the answer options, select the law topics from the full
        list that you believe are most relevant and applicable to determining the correct answer.

        After making your initial selection, check the cumulative character count of the topics you've
        chosen. If the total size exceeds 125000 characters, carefully review your selections and deselect
        the least relevant topics until you have reduced the total size to 125000 characters or less.

        Finally, provide your curated list of the most relevant and applicable law topics for answering this
        question inside <selected_law_topics> tags, like this:

        <selected_law_topics>
        [list the relevant and applicable law topics here, separated by newlines]
        </selected_law_topics>

        Remember, your goal is to identify the subset of law topics that will be most useful for determining
        the correct answer to the question, given the answer options provided. Carefully consider the
        pertinence of each topic before settling on your final curated list.

        Strictly give response as per the given sample response format Sample Response Format:             <selected_law_topics>            Topic 1.02: "Topic_1.02_name"-"topic_1.02_size"           Topic 1.04: "Topic_1.04_name"-"topic_1.04_size"           Topic 9.03: "Topic_9.03_name"-"topic_9.03_size"             Total size: topic_1.02_size + topic_1.04_size + topic_9.03_size            </selected_law_topics>
    """


def aib_exam_step_2_input(
    law_content, question, option_a, option_b, option_c, option_d
):
    return f"""
        Here is the statement of law to consider:

        <statement_of_law>
        {law_content}
        </statement_of_law>

        Here is the question to answer:

        <question>
        {question}
        </question>

        Here are the answer options:

        <option_a>
        {option_a}
        </option_a>

        <option_b>
        {option_b}
        </option_b>

        <option_c>
        {option_c}
        </option_c>

        <option_d>
        {option_d}
        </option_d>

        Before proceeding, take the time to carefully read and fully understand the provided statement of
        law, the question being asked, and the four answer options. Do not move forward until you have a
        thorough grasp of these materials.

        Now, carefully review the statement of law again and extract the specific portions that are relevant
        to answering the question at hand. Provide these relevant extracts inside <relevant_law> tags.

        Next, think through your strategy and approach for answering this question based on the provided
        statement of law. Summarize your strategic approach inside <strategy> tags.

        Then, go through each of the four answer options (A, B, C, D) and provide your reasoning for why you
        would or would not select that option based on the relevant law. Provide your reasoning for each
        option inside <option_reasoning> tags, with a separate set of tags for each option.

        Finally, select the single best answer option based on your analysis above. Provide only the letter
        (A, B, C, or D) corresponding to your answer inside <answer> tags.
    """


def relevent_topics_input_generator(topics, aib=False):
    # matches_1 = re.findall(r"Topic \d+\.\d+:\s*(.*?)\s+(Size:\d+)", topics)
    # matches_2 = re.findall(r"Topic \d+\.\d+:\s*(.*?)\s+-\s+(\d+)", topics)
    # matches_3 = re.findall(r'Topic \d+\.\d+:\s*(.*?)-(\d+)', topics)
    # matches_4 = re.findall(r"Topic \d+\.\d+\s*(.*?)\s+(Size:\d+)", topics)
    # matches_5 = re.findall(r"Topic \d+\.\d+\s*(.*?)-(\d+)", topics)
    # total_matches = matches_1 + matches_2 + matches_3 + matches_4 + matches_5
    pattern = r"Topic\s+(\d+\.\d+)"
    matches = re.findall(pattern, topics)
    matches = list(map(float, matches))
    print("OUTPUT::", matches)
    output = []
    for match in matches:
        # if match[0].startswith('"') or match[0].endswith('"'):
        #     output.append(match.strip('"'))
        # else:
        output.append(match)
    topics = LawTopics.objects.filter(topic_id__in=matches)
    print("TOPICS::", topics)
    topics_input_value = ""
    for topic in topics:
        topics_input_value += f"<{topic.name}>{topic.content}</{topic.name}>"
    return topics_input_value


def send_aib_mail(aib_answer, *args, **kwargs):
    html_content = render_to_string(
        "email/aib_email.html",
        context={
            "string": aib_answer,
        },
    )
    subject = "AIB Question-Answer by Syndicus"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [
        # "rithikchaudhary150500@gmail.com",
        # "jishnusai99@gmail.com",
        "iammgautam@gmail.com",
    ]
    message = EmailMultiAlternatives(
        subject, body="", from_email=from_email, to=recipient_list
    )
    message.attach_alternative(html_content, "text/html")
    try:
        message.send()
        return True
    except EmailBackend.RecipientRefused:
        return False


def law_topics_format_generator():
    parent_objs = LawTopics.objects.filter(parent__isnull=True).prefetch_related(
        "lawtopics_set"
    )
    input_law_topics = ""
    child_objs_to_update = []
    for i, parent_obj in enumerate(parent_objs, start=1):
        input_law_topics += f"Law {i} {parent_obj.name}:\n"
        for y, child_obj in enumerate(parent_obj.lawtopics_set.all(), start=1):
            y_str = str(y).zfill(2)
            input_law_topics += (
                f"Topic {i}.{y_str} {child_obj.name} Size:{child_obj.token_value},\n"
            )
            child_obj.topic_id = f"{i}.{y_str}"
            child_objs_to_update.append(child_obj)
    LawTopics.objects.bulk_update(child_objs_to_update, ["topic_id"])
    return input_law_topics


def step_2_output_formatter(string):
    string = string.replace("&amp;", "&")
    full_legal_memo_original = re.search(
        r"&lt;legal_memorandum&gt;(.*?)&lt;\/legal_memorandum&gt;",
        string,
        re.DOTALL,
    ).group(1)
    string = string.replace("<br>", "")
    if "!%!Question Presented!%!" in string or "Question Presented" in string:
        string = string.replace(
            "!%!Question Presented!%!", "<h2><b>Question Presented</b></h2>"
        ).replace("Question Presented", "<h2><b>Question Presented</b></h2>")

    if "!%!Statement of Facts!%!" in string or "Statement of Facts" in string:
        string = string.replace(
            "!%!Statement of Facts!%!", "<h2><b>Statement of Facts</b></h2>"
        ).replace("Statement of Facts", "<h2><b>Statement of Facts</b></h2>")

    if "!%!Analysis!%!" in string or "Analysis" in string:
        string = string.replace("!%!Analysis!%!", "<h2><b>Analysis</b></h2>").replace(
            "Analysis", "<h2><b>Analysis</b></h2>"
        )

    if "!%!Conclusion!%!" in string or "Conclusion" in string:
        string = string.replace(
            "!%!Conclusion!%!", "<h2><b>Conclusion</b></h2>"
        ).replace("Conclusion", "<h2><b>Conclusion</b></h2>")
    full_legal_memo_html = re.search(
        r"&lt;legal_memorandum&gt;(.*?)&lt;\/legal_memorandum&gt;",
        string,
        re.DOTALL,
    ).group(1)
    pattern = r"\|\$\|(.*?)\|\$\|"
    matches = re.findall(pattern, full_legal_memo_html)
    for title in matches:
        full_legal_memo_html = full_legal_memo_html.replace(
            f"|$|{title}|$|", f"<b>{title}<b>"
        )
    legal = re.search(
        r"!%!Question Presented!%!(.*?)!%!Statement of Facts!%!",
        full_legal_memo_original,
        re.DOTALL,
    ).group(1)

    facts = re.search(
        r"!%!Statement of Facts!%!(.*?)!%!Analysis!%!",
        full_legal_memo_original,
        re.DOTALL,
    ).group(1)

    pattern = r"\|\$\|(.*?)\|\$\|"
    matches = re.findall(pattern, full_legal_memo_original)
    analysis = []
    for title in matches:
        pattern = rf"\|\$\|{title}\|\$\|(.*?)\|\$\|"
        if title == matches[-1]:
            print("TITLE:::", title)
            pattern = rf"\|\$\|{title}\|\$\|(.*?)!%!Conclusion!%!"
        content_match = re.search(pattern, full_legal_memo_original, re.DOTALL).group(1)
        title = title.replace("<h2>", "")
        title = title.replace("</h2>", "")
        title = title.replace("<b>", "")
        title = title.replace("</b>", "")
        content_match = content_match.replace("<h2>", "")
        content_match = content_match.replace("</h2>", "")
        content_match = content_match.replace("<b>", "")
        content_match = content_match.replace("<b>", "")
        analysis.append({"title": title, "content": content_match})

    conclusion = re.search(
        r"!%!Conclusion!%!(.*)",
        full_legal_memo_original,
        re.DOTALL,
    ).group(1)

    return (
        full_legal_memo_original,
        full_legal_memo_html,
        legal,
        facts,
        analysis,
        conclusion,
    )


def read_word_doc(tag, directory):
    file_contents = []
    for filename in os.listdir(directory):
        if filename.endswith(".docx"):
            file_contents.append(filename)
    data = []
    for file_name in file_contents:
        # print("FILE NAME::", file_name)
        file_path = os.path.join(directory, file_name)
        doc = docx.Document(file_path)
        regex = r"\[(\d+\.\d+)\]\s*(.+)(?=\.docx)"
        match = re.search(regex, file_name)
        book_id = match.group(1)
        name = match.group(2)
        file_name_pattern = r"^(.+)(?=\.docx$)"
        file_name_value = re.search(file_name_pattern, file_name).group(1)
        # print("NAME::", file_name_value)
        each_statement = []
        statement = []
        citations_list = []
        v_line_start = None
        v_line_middle = None
        v_line_end = None
        # for statement value
        for para in doc.paragraphs:
            if tag in para._p.xml:
                paragraph_xml = lxml.etree.fromstring(para._p.xml)
                v_line = paragraph_xml.xpath(
                    "//v:line", namespaces={"v": "urn:schemas-microsoft-com:vml"}
                )
                v_line_attribute = v_line[0].attrib
                # print("ATTRIB::", v_line_attribute)
                # if (
                #     v_line_attribute is not None
                #     and v_line_attribute.get("strokecolor") == "#009ddb"
                #     and v_line_attribute.get("strokeweight") == "2pt"
                # ):
                #     # print("1st stroke")
                #     v_line_start = v_line
                if (
                    v_line_attribute is not None
                    and v_line_attribute.get("strokecolor") == "#bcbeb0"
                    and (
                        v_line_attribute.get("strokeweight") == ".5pt"
                        or v_line_attribute.get("strokeweight") == "0.5pt"
                    )
                ):
                    # print("2nd stroke")
                    v_line_middle = v_line
                    # break
                if (
                    v_line_attribute is not None
                    and v_line_attribute.get("strokecolor") == "black"
                    and v_line_attribute.get("strokeweight") == "1pt"
                ):
                    # print("VLINE END::", v_line_attribute)
                    v_line_end = v_line

            para_text = ""
            if not v_line_middle:
                for run in para.runs:
                    if not run.font.superscript:
                        para_text += run.text
                each_statement.append(para_text)

            citations_text = ""
            if v_line_middle and not v_line_end:
                citations_text += para.text
            citations_list.append(citations_text)
        citations_list = [
            re.search(r"(\t.*)", item).group(1) if "\t" in item else item
            for item in citations_list
            if item and item.strip()
        ]
        statement.append("".join(each_statement))
        pattern = rf"\[{book_id}\](.*)\s{name}"
        match = re.search(pattern, statement[0])
        if match:
            start_pos = match.start() + len(book_id) + len(name) + 3
            filtered_text = statement[0][start_pos:]
        data.append(
            {
                "book_id": book_id,
                "name": f"[{book_id}] {name}",
                "statement": filtered_text,
                "citation_list": citations_list,
            }
        )
    hulsbury_law = [HulsburyLawBooks(**data_item) for data_item in data]
    data = HulsburyLawBooks.objects.bulk_create(hulsbury_law)
    return data


def update_the_citation():
    law_obj = HulsburyLawBooks.objects.get(id=530)

    genai.configure(api_key="AIzaSyCvsOGdpu4Ke0E-m90nCSUV2M5LGv5GEwA")
    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 0,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    print("Available base models:", [m.name for m in genai.list_models()])

    model = genai.GenerativeModel(
        model_name="tunedModels/w2ndfinetuneprompt-ydb1zhmc9pmn",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )
    # for law_single_obj in law_obj.first():
    # legal_text = ''.join(law_obj.citation_list)
    # print("Citations::", legal_text, type(legal_text))
    response = model.generate_content(law_obj.citation_list)

    print(response.text)
    # response = model.generate_content([
    # "input: 1 the Assam Rhinoceros Protection Act 1954 s 2. Every rhinoceros captured and the horn or carcass or any\npart of every rhinoceros killed in contravention of the Act will be the property of the state government: Assam\nRhinoceros Protection Act 1954 s 3.\n\n2 The\nWild Life (Protection) Act 1972 has six schedules. Schedules 1, 2, 3, 4 contain a list of endangered\nfauna, mammals, amphibians, reptiles, birds, crustaceans and insects, Sch 5 contains a list of vermin and Sch 6\ncontains a list of endangered flora.\n\n3\nWild Life (Protection) Act 1972 ss 40, 41, 42. Every person who, at the commencement of the Act, was\nin possession of any uncured trophy derived from a Sch 1 or Sch 2 Pt I wild animal, or salted or dried skin of such\nanimal, or the musk of a musk deer, or the horn of a rhinoceros, was required to declare the same to the Chief Wild Life\nWarden within 30 days:\nWild Life (Protection) Act 1972 s 40 (1). The Chief Wild Life Warden would make enquiries, and if\nsatisfied, affix on the article, trophy or uncured trophy, identification marks and issue a certificate of ownership:\nWild Life (Protection) Act 1972 s 41 (1) (b), (c).\n\n4\nWild Life (Protection) Act 1972 s 40 (3).\n\n5\nWild Life (Protection) Act 1972 s 43 (2).\n\nPage 2 of\n\n[15.009] Property in wild animals under the Wild Life (Protection) Act 1972\n\n6\nWild Life (Protection) Act 1972 s 43 (1), (3), (4). Prior to the granting of permission, the Chief Wild Life\nWarden has to ascertain that the animal referred to in the certificate of ownership has been lawfully acquired:\nWild Life (Protection) Act 1972 s 43 (4).",
    # "output: ",
    # ])

    # print(response.text)

    # gemini code
    # output = {
    #     "statutes": {
    #         # "Assam Rhinoceros Protection Act 1954 s 2",
    #         # "Assam Rhinoceros Protection Act 1954 s 3",
    #         "Wild Life (Protection) Act 1972",
    #         # "Wild Life (Protection) Act 1972 s 42",
    #         # "Wild Life (Protection) Act 1972 s 41",
    #         # "Wild Life (Protection) Act 1972 s 40",
    #         # "Wild Life (Protection) Act 1972 s 43",
    #     },
    #     "case laws": {},
    #     "files": {},
    # }
    # statutes = list(output["statutes"])
    # case_laws = list(output["case laws"])
    # files = list(output["files"])

    # return final_function(case_laws, statutes, law_obj.book_id, law_obj)


def import_air():

    # Set your OpenAI API key
    openai.api_key = os.getenv("OPEN_AI")

    # paras = Caseparagraph.objects.all()
    # for para in paras:
    #     embedding = openai.embeddings.create(input=[para.text], model="text-embedding-3-large")
    #     para.embeddings = embedding.data[0].embedding
    #     para.save()
    index = 1
    notes = CaseNote.objects.all()
    for note in notes:
        embedding = openai.embeddings.create(
            input=[note.short_text], model="text-embedding-3-large"
        )
        note.embeddings = embedding.data[0].embedding
        note.save()
        print("Index::", index + 1)
        index = index + 1

    return True


def open_ai_keyword_api(input_text):
    client = OpenAI(
        api_key=os.getenv("OPEN_AI"),
    )
    # openai.api_key = os.getenv("OPEN_AI")
    model = "gpt-4o"
    prompt = f"""
        You are a legal researcher tasked with suggesting individual searchable key phrases to perform legal research for a particular legal issue. Your goal is to analyze the given legal text and extract relevant key phrases that must be useful for further legal research.
        Here is the legal text you need to analyze:
        <legal_text>
        {input_text}
        </legal_text>
        Follow these steps to generate a list of searchable key phrases:

        Read the entire text carefully to understand the general topic and context.
        Determine the primary subject matter.
        Identify and highlight terms and phrases that stand out as particularly relevant or important.
        Look for specific legal terminology relevant to the topic.
        Note words and phrases that are repeated throughout the text.
        Consider the jurisdiction, as legal terms and relevance can vary by location.

        When selecting keywords, keep the following guidelines in mind:

        Ensure the key phrases are directly relevant to the specific legal issue or question.
        Begin with broad terms and then narrow down to more specific terms as needed.
        Include a mix of general legal concepts and case-specific terms.
        Consider including names of relevant laws, statutes, or regulations.
        Do not include names of parties or entities involved.

        Your output must be a list of individual searchable keywords in JSON format. The JSON should contain an array of strings, where each string is a key phrase.
        Aim to provide between 2 and 10 key phrases, depending on the complexity and length of the given text. Make sure each key phrase is relevant and useful for further legal research on the topic."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a legal researcher tasked with suggesting individual searchable key phrases to perform legal research for a particular legal issue.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0,
        top_p=1.0,
        n=1,
        stop=None,
    )
    result = response.choices[0].message.content.replace("\n", "")
    result = result.replace("```", "")
    result = result.replace("json", "")
    try:
        terms = ast.literal_eval(result)
    except:
        return None
    return terms


def para_embedd():

    openai.api_key = os.getenv("OPEN_AI")
    cases = Case.objects.all().prefetch_related(
        Prefetch(
            "case_note",
            queryset=CaseNote.objects.prefetch_related("paragraph"),
            to_attr="case_notes_query",
        )
    )
    case_value = 0
    for case in cases:
        case_value = case_value + 1
        case_note_para = set()
        citation_paragraphs = set()
        for case_note in case.case_notes_query:
            for para in case_note.paragraph.all():
                case_note_para.add(para.para_count)
        for item in case.citations:
            if item["paragraph"] is not None:
                citation_paragraphs.update(item["paragraph"])
        combined_set = list(case_note_para.union(citation_paragraphs))
        para_obj = Caseparagraph.objects.filter(
            para_count__in=combined_set, case=case, embeddings=default_embeddings
        )
        index = 0
        for para in para_obj:
            try:
                embedding = openai.embeddings.create(
                    input=[para.text], model="text-embedding-3-large"
                )
                para.embeddings = embedding.data[0].embedding
                para.save()
                index = index +1
            except Exception as e:
                truncate_text = get_first_4000_words(para.text)
                print(para.id)
                print(truncate_text)
                print()
                embedding = openai.embeddings.create(
                    input=[truncate_text], model="text-embedding-3-large"
                )
                para.embeddings = embedding.data[0].embedding
                para.save()
                index = index +1
    return True


def keyword_and_embedding():
    openai.api_key = os.getenv("OPEN_AI")
    index = 0
    case_notes = CaseNote.objects.exclude(~Q(embeddings=default_embeddings))
    # print(case_notes.count())
    for case_note in case_notes:
        embedding = openai.embeddings.create(
            input=[case_note.short_text], model="text-embedding-3-large"
        )
        case_note.embeddings = embedding.data[0].embedding
        case_note.save()
        index += 1
        print("Case Notes::", index)
        # keyword_create_list = []
        # keyword = open_ai_keyword_api(case_note.short_text)
        # if keyword is not None:
        #     for key in keyword:
        #         co = cohere.Client("<<apiKey>>")

        #         response = co.embed(
        #             texts=[case_note.short], model="embed-english-v3.0", input_type="classification"
        #         )
        #         embedding = openai.embeddings.create(
        #             input=[key], model="text-embedding-3-large"
        #         )
        #         keyword_create_list.append(
        #             {
        #                 "keyword": key,
        #                 "embedding": embedding.data[0].embedding,
        #             }
        #         )
        #     relevant_passage = [
        #         caseNotesKeyword(**key_item, case_note=case_note) for key_item in keyword_create_list
        #     ]
        #     caseNotesKeyword.objects.bulk_create(relevant_passage)
        #     index += 1
        #     print("CASE DONE:::",index)


def del_duplicates():
    # case = Case.objects.values('code').annotate(count=Count('code')).filter(count__gt=1)
    # print(case)
    # case_name = set()
    # for c in case:
    #     case_name.add(c["code"])
    # case_name = list(case_name)
    # for case in case_name:
    #     case_obj = Case.objects.filter(code=case)
    #     print(case_obj, case_obj.count())
    #     first_case = case_obj.first()
    #     print(first_case)
    #     first_case.delete()
    para = Caseparagraph.objects.all()
    index = 0
    for p in para:
        # have_space = p.para_count.strip()
        # if p.para_count != have_space:
        p.para_count = p.para_count.strip()
        p.save()
        index += 1
        print("index:", index)


def get_first_4000_words(text):
    words = text.split()
    first_4000 = words[:4000]
    result = ' '.join(first_4000)
    return result
