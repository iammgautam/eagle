import re
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.urls import reverse
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import viewsets
from .models import Argument, BriefArgument
from case_history.models import CaseHistory
from .serializers import ArgumentSerializer, BriefArgumentSerializer
from case_history.models import LawTopics
from legal_gpt import settings


INPUT_TOPICS = """1 Constitutional Law:
    1.1 Constitution and Constitutionalism Size:14102,
    1.2 Nature of Indian Constitution and Concept of Federalism Size:20192,
    1.3 The Union and its Territories Size:11768,
    1.4 Union and State Executive Size:40215,
    1.5 LEGISLATIVE POWER OF THE EXECUTIVE (ORDINANCES) Size:11263,
    1.6 Parliament and State Legislatures Size:16698,
    1.7 The Union and State Judiciary Size:54864,
    1.8 Distribution of Powers between Centre and States (Articles 245-254) Size:24678,
    1.9 Freedom of Trade, Commerce and Intercourse Size:12408,
    1.10 Emergency Provisions Size:13891,
    2 CPC:
    2.1 Jurisdiction of Civil Courts (Sections 3, 6 and 9) Size:16642,
    2.2 Res Sub Judice : Stay of Suit (Section 10) Size:5877,
    2.3 Foreign Judgment [Section 2(5) & (6), 13, 14 & 44A] Size:8936,
    2.4 Res Judicata: Bar of Suit (Section 11) Size:31199,
    2.5 An Introduction to the Civil Procedure Code (Sections 1, 4 & 5, 7 & 8) Size:9428,
    2.6 Definitions: Section 2 (Judgment, Decree, Order, Legal Representative, Mesne Profits) Size:12530,
    2.7 Place of Suing (Sections 15, 16 to 20, 21-21A) Size:14789,
    2.8 Power of Transfer Suits (Sections 22, 23, 24 and 25) Size:8205,
    2.9 Attachment of Property (Sections 60 to 64 ; Order 21, Rules 41 to 57) Size:8417,
    2.10 Commission (Sections 75 to 78 ; Order 26) Size:4956,
    2.11 Suits by or against Government (Sections 79 to 82 ; Order 27) Size:5354,
    2.12 Appeals in General (Sections 96 to 112 ; Orders 41 to 45) Size:15738,
    2.13 Production of Additional Evidence in Appellate Court [Section 107(1)(d) and Order 41] Size:8211,
    2.14 Second Appeal (Appeals from Appellate Decrees) (Sections 100 to 103 and Order 42) Size:13176,
    2.15 Reference, Review and Revision (Sections 113, 114, 115 and Orders 46, 47) Size:18238,
    2.16 Inherent Powers of a Court (Sections 148 to 153A) Size:12022,
    2.17 Parties to Suits (Order 1, Rules 1 to 13) Size:11074,
    2.18 Institution of Suits (Order 4 and Section 26) Size:3507,
    2.19 Pleadings: Meaning, Object, General Rules (Order 6, Rules 1 to 16) Size:7785,
    2.20 Amendment of Pleadings (Order 6, Rules 17 & 18) Size:14183,
    2.21 Plaint (Order 7, Rules 1 to 18) Size:9799,
    2.22 Written Statement, Set-off & Counter Claim (Order 8, Rules 1 to 10) Size:9186,
    2.23 Appearance of Parties and Consequences of Non-appearance (Order 9, Rules 1 to 14) Size:19490,
    2.24 Suits / Appeals by Indigent Persons (Orders 33 and 44) Size:4226,
    2.25 Interpleader Suits (Order 335 and Section 88) Size:1689,
    2.26 Summary Procedure (Order 37, Rules 1 to 7) Size:9500,
    2.27 Temporary Injunction and Interlocutory Orders (Order 39, Rules 1 to 10) Size:17400,
    2.28 Receiver [Order 40, Section 94(d)] Size:3605,
    2.29 Affidavits, Restitution, Caveat [Order 19 ; Section 114 ; Section 148A] Size:4022,
    3 Law of Evidence:
    3.1 An Introduction to the Law of Evidence and Interpretation Clause (Sections 3 and 4) Size:17435,
    3.2 Relevancy of Facts [Sections 5 to 16 ((CONSPIRACY: ALIBI; DAMAGES; RIGHT / CUSTOM; PSYCHOLOGICAL FACTS; SIMILAR OCCURRENCES; COURSE OF BUSINESS))] Size:39312,
    3.3 Admissions (Sections 17 to 23 and 31) Size:15392,
    3.4 Confession (Section 24 to 30) (Stated Type Relevant Facts) Size:26754,
    3.5 Dying Declarations (DD) [Sections 32(1)] Size:15675,
    3.6 Expert Evidence (Opinion of Experts) (Relevancy of Opinion of third persons) Size:14879,
    3.7 Relevancy of Character (Sections 52, 53, 53A, 54 & 55) Size:4989,
    3.8 Facts which need not be Proved (Sections 56, 57 & 58) Size:2421,
    3.9 Means / Modes of Proof : Oral Evidence (Sections 59 and 60) Size:6293,
    3.10 Means / Modes of Proof : Documentary Evidence (Sections 61 to 78) Size:12332,
    3.11 Exclusion of Oral Evidence by Documentary Evidence (Sections 91 to 100) Size:14256,
    3.12 Burden of Proof [who has the burden of bringing / adducing facts before the court] (Sections 3, 101 to 111) Size:13350,
    3.13 Presumptions (Rules limiting Judicial freedom of drawing inference) [Sections 4, 41, 79-90A, 111A to 114] Size:25536,
    3.14 Doctrine of Estoppel (Sections 115, 116, and 117) [Facts which the parties are Prohibited from Proving] Size:21275,
    3.15 Privileged Communications (Sections 121 to 132) Size:17409,
    3.16 Accomplice / Approver Evidence [Sections 133 and 114(b)] Size:15591,
    3.17 Competency and Sufficiency of Witnesses (Sections 118, 119, 120 & 134) Size:8462,
    3.18 Examination of Witnesses (Sections 135 to 140 & 154, 155) Size:15934,
    4 Competition Law:
    4.1 Introduction of Competition Law Size:5960,
    4.2 History and Development of Competition Law Size:24229,
    4.3 Anti-Competitive Agreements [Section 3] Size:35946,
    4.4 Regulation of Abuse of Dominant Position (Section 4) Size:29980,
    4.5 Regulation of Combinations (Section 5 & 6) Size:15706,
    4.6 Enforcement Mechanisms Size:27795,
    4.7 Competition Advocacy and Leniency Programme Size:6864,
    4.8 Emerging Trends In Competition Law (National and International) Size:10600,
    5 Taxation Laws:
    5.1 Preliminary and Previous Year Size:26193,
    5.2 Residential Status and Tax Incidence Size:13101,
    5.3 Agricultural Income Size:12504,
    5.4 Heads of Income-Salaries Size:15972,
    5.5 Income from House Property Size:14364,
    5.6 Profits and Gains of Business or Profession Size:37920,
    5.7 Capital Gains Size:25493,
    5.8 Income from Other Sources Size:5958,
    5.9 Income of Other Persons Included in Assessee's Total Income Size:7492,
    5.10 Set-off and Carry Forward of Losses Size:6208,
    5.11 Assessment Size:29042,
    5.12 GST-Overview Size:2228,
    6 Property Law:
    6.1 Movable and Immovable Property Size:8755,
    6.2 Attestation Size:8946,
    6.3 Doctrine of Notice Size:15700,
    6.4 Transfer of Property (Section 5) Size:16728,
    6.5 Transferable Property [Section 6(a) and 43] Size:16372,
    6.6 Conditional Transfers (Conditions Repugnant to Interest Created) (Sections 10, 11, 12, & 40) Size:18412,
    6.7 Rule against perpetuities (Transfer for the benefit of Unborn Person) (Sections 13 to 18, 20 & 22) Size:16609,
    6.8 Vested and Contingent Interest (Sections 19 and 21) Size:9470,
    6.9 Transfer During Pendency of Litigation (Rule/Doctrine of Lis Pendens) (Section 52) Size:16481,
    6.10 Mortgages (Chapter 4: Sections 58 to 104) Size:26588,
    6.11 Lease and License (Sections 105 & 106, TPA; Sections 52, Indian Easement Act, 1882) Size:19005,
    6.12 GIFT (Sections 122-129) Size:20312,
    7 Family Law - 1:
    7.1 Nature of Hindu Law Size:3111,
    7.2 Sources and Schools of Hindu Law Size:5746,
    7.3 Hindu Law of Marriage Size:44543,
    7.4 Restitution of Conjugal Rights Size:16755,
    7.5 Judicial Separation Size:4152,
    7.6 Divorce: A Matrimonial Relief Size:45928,
    7.7 Hindu Law of Maintenance Size:18637,
    7.8 Hindu Law of Adoption Size:15187,
    7.9 Legitimacy of Children of Void and Voidable Marriage Size:3522,
    7.10 Minority, Guardianship and Custody Size:9154,
    7.11 Sources and Schools of Muslim Law Size:7312,
    7.12 Muslim Law of Marriage (Nikah) Size:24844,
    7.13 Muslim Law of Divorce Size:29595,
    7.14 Muslim Law of Maintenance Size:14223,
    7.15 Acknowledgement of Paternity and Legitimacy Size:4417,
    7.16 Wakfs and Endowments Size:7784,
    8 Intellectual Property Law:
    8.1 Introduction to Intellectual Property Rights, and International Agreements in the Field of Copyright and Patents Size:18994,
    8.2 Copyright Size:14083,
    8.3 Classes of Works in which Copyright Subsists or The Subject Matter of Copyright Size:21271,
    8.4 Rights Conferred by Copyright Size:13294,
    8.5 Ownership of Copyright Size:8752,
    8.6 Assignment and Licenses of Copyright Size:12622,
    8.7 Collective Management of Copyright by Copyright Societies [Sections 32-35] Size:3281,
    8.8 Infringement of Copyright Size:5798,
    8.9 International Copyright Order, 1999 Size:2739,
    8.10 Permitted Uses/Fair Dealing Size:12841,
    8.11 Origin of Patent Size:11231,
    8.12 Procedure for Filling Patent Applications Size:6852,
    8.13 Grounds of Opposition and Revocation Size:7656,
    8.14 Rights of Patentee Size:1716,
    8.15 Revocation of Patent [Sections 64] Size:2063,
    8.16 Infringement of Patents Size:4302,
    8.17 Compulsory Licensing and Parallel Importing Size:3529,
    8.18 Law of Plant Varieties and Farmer's Rights Size:11558,
    8.19 Trade Secret/Confidential Information Size:2765,
    8.20 Traditional Knowledge Size:4362,
    8.21 Semiconductor Integrated Circuits Layout Design Act 200 Size:2349,
    8.22 Introduction to the Intellectual Property Size:5802,
    8.23 Abuse of Intellectual Property-Concept, Redress under Article 40 of TRIPS and Competition Law Size:5572,
    8.24 International Legal Instruments Relating to IPR Size:12374,
    8.25 Fundamentals of Trademark Size:4045,
    8.26 Statutory Definition of Trade Mark [Section 2(1)(zb)] Size:7148,
    8.27 Protecting Domain Names as Trade Marks Size:3930,
    8.28 Trade Marks for Services Size:4945,
    8.29 Registration of Trade Marks for Goods/Services Size:1962,
    8.30 Requisites for Registration and Grounds of Refusal of Registration Size:45308,
    8.31 Infringement and Passing off of Trademarks and Transborder Reputation Size:26182,
    8.32 Trade Dress and Colour Combination, Disparagement, Comparative Advertising, Dilution or Tarnishment of Trademark and Exhaustion of Intellectual Property Rights Size:6799,
    8.33 Licensing of Trademarks [Sections 48 to 56] Size:2110,
    8.34 Geographical Indications of Goods (Registration and Protection Act, 1999) Size:8701,
    8.35 Industrial Designs Law Size:12721,
    9 Law of Crimes - 3:
    9.1 An Introduction to Socio-Economic Offences and White Collar Crimes Size:13566,
    9.2 The Immoral Traffic (Prevention) Act, 1956 Size:23822,
    9.3 The Narcotic Drugs and Psychotropic Substances Act, 1985 Size:39957,
    9.4 The Food Safety and Standards Act, 2006 Size:20212,
    9.5 The prevention of Corruption Act, 1988 Size:18432,
    9.6 The Prevention of Money Laundering Act, 2002 Size:8413,
    9.7 Special Courts (Sections 43 to 47) Size:8755,
    10 Labour Law:
    10.1 The Trade Unions Act, 1926 Size:32124,
    10.2 Industry Size:32694,
    10.3 Industrial Dispute Size:10468,
    10.4 Workman Size:29382,
    10.5 Strikes and Lock-nuts Size:24825,
    10.6 Lay-off, Retrenchment and Closure Size:34420,
    10.7 Dispute Settlement under the Industrial Disputes Act Size:13334,
    10.8 Awards and Settlements Size:8610,
    10.9 The Industrial Employment (Standing Orders) Act, 1946 Size:5010,"""


def get_step_1_input(topics, facts, legal_issue):
    return f"""You are a legal researcher tasked with finding the most relevant and applicable law topics for a particular legal case. To assist you, I will provide three key pieces of information: <allLawTopics> {topics}</allLawTopics> <facts>{facts} </facts><legalIssue>{legal_issue}</legalIssue>Please follow these steps carefully:1. Read the facts of the case and the legal issue thoroughly to fully understand the details and context of the case.2. Review the provided list of law topics, paying close attention to how they are segmented and described. Make sure you have a clear grasp of what each topic entails.3. Select the law topics that are most relevant and applicable to the case at hand, based on your analysis of the facts and the legal issue that needs to be addressed.4. Check the cumulative size of your selected law topics. If the total size exceeds 125000, carefully deselect the least relevant and applicable topics from your list until the cumulative size is reduced to 125000 or below.5. Provide your final curated list of the most relevant and applicable law topics for this case inside <selected_law_topics> tags, formatted as follows:<selected_law_topics>[list the relevant and applicable law topics here]</selected_law_topics>Remember, your goal is to identify the law topics that are most pertinent and useful for addressing the legal issue, given the specific facts of the case. Carefully consider the relevance and applicability of each topic before making your final selections.  Strictly give response as per the given sample response format Sample Response Format:            <selected_law_topics>            1.2: "Topic_1.2_name"-"topic_1.2_size"            1.4: "Topic_1.4_name"-"topic_1.4_size"            9.3: "Topic_9.3_name"-"topic_9.3_size"             Total size: topic_1.2_size + topic_1.4_size + topic_9.3_size            </selected_law_topics>"""


def get_step_2_input(relevent_topics, fact, legal_issue):
    return f"""
       You are a legal researcher tasked with drafting a legal memorandum for a particular case. To complete this task, please follow these steps: 

        1. Carefully read and understand the statement of law provided: 

        <statement_of_law> 
        {relevent_topics} 
        </statement_of_law> 

        2. Study the facts of the case: 

        <facts_of_the_case> 
        {fact} 
        </facts_of_the_case> 

        3. Consider the legal question to be addressed: 

        <legal_question> 
        {legal_issue} 
        </legal_question> 

        4. Before proceeding, take time to thoroughly understand the statement of law, facts of the case, and the legal question. 

        5. Structure your legal memorandum as follows: 

        !%!Question Presented!%! 
        - Formulate a specific and impartial question that captures the core legal issue without assuming a legal conclusion. 

        !%!Statement of Facts!%!   
        - Provide a concise, impartial summary of the key facts relevant to the legal matter, approximately 200 words in length. 
        - Include current and past legal proceedings related to the issue. 
        - Present the facts chronologically or grouped thematically, whichever format offers the clearest understanding. 

        !%!Analysis!% ! 
        - Provide a well-reasoned legal analysis that discusses the application of the relevant law to the facts of the case. Be sure to incorporate the applicable legal principles (statutes and case laws) from the statement of law. 
        - Divide the analysis into subsections, each addressing a specific legal topic relevant to the case in at least 500 words in length. 
        - For each topic, clearly state the applicable law and relevant facts in an active voice and present your analysis in a logical manner. 
        - The total length of the Analysis section should be approximately 2000 words. 
        - Subsection titles must be enclosed in |$| tags as in |$|subsection_title|$|. 

        !%!Conclusion!% ! 
        - In approximately 300 words, predict how the court will likely apply the law based on your analysis. 
        - Before providing your prediction, express your level of confidence in the prediction based on the available information. 
        - Using an impartial advisory tone, identify next steps and propose a legal strategy to proceed. 

        6. Provide your complete legal memorandum inside <legal_memorandum> tags. 

        Remember to provide a thorough and well-reasoned legal analysis, incorporating the relevant legal principles from the statement of law, facts of the case, and application of law to the facts. Your memorandum should demonstrate a clear understanding of the legal issues at hand and provide valuable insights for the reader.

        Strictly follow the instructions and structure the legal memorandum as per the given format.
    """


class ArgumentViewSet(viewsets.ModelViewSet):
    queryset = Argument.objects.all()
    serializer_class = ArgumentSerializer


class BriefArgumentViewSet(viewsets.ModelViewSet):
    queryset = BriefArgument.objects.all()
    serializer_class = BriefArgumentSerializer

    def create(self, request, *args, **kwargs):
        research_output = request.data.get("research_output")
        input_relevant_topic = self.relevent_topics_input_generator(research_output)
        brief_argument_data = {
            "relevant_topics": input_relevant_topic,
        }
        serializer = self.get_serializer(data=brief_argument_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        case_history = CaseHistory.objects.get(id=request.data.get("case_id"))
        case_history.brief_argument_id = serializer.data["id"]
        case_history.save()
        self.get_success_headers(serializer.data)
        return HttpResponseRedirect(
            reverse(
                "brief_argument:step_2",
                kwargs={"brief_id": serializer.data["id"]},
            )
        )

    def update(self, request, *args, **kwargs):
        string = self.counsel_formatter(request.data.get("counsel_output"))
        html_content = render_to_string(
            "email/example.html",
            context={
                "string": string,
            },
        )
        brief_argument_obj = self.get_object()
        subject = f"{brief_argument_obj.case_history.petitioner_name} v. {brief_argument_obj.case_history.respondent_name} in {brief_argument_obj.case_history.high_court}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ["rithikchaudhary150500@gmail.com", "jishnusai99@gmail.com", "iammgautam@gmail.com"]
        message = EmailMultiAlternatives(
            subject, body="", from_email=from_email, to=recipient_list
        )
        message.attach_alternative(html_content, "text/html")
        message.send()
        brief_argument_obj.case_history.is_completed = True
        brief_argument_obj.case_history.save()
        return HttpResponseRedirect(
            reverse(
                "brief_argument:admin_home_page",
            )
        )

    def counsel_formatter(self, string):
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
            string = string.replace(
                "!%!Analysis!%!", "<h2><b>Analysis</b></h2>"
            ).replace("Analysis", "<h2><b>Analysis</b></h2>")

        if "!%!Conclusion!%!" in string or "Conclusion" in string:
            string = string.replace(
                "!%!Conclusion!%!", "<h2><b>Conclusion</b></h2>"
            ).replace("Conclusion", "<h2><b>Conclusion</b></h2>")
        pattern = r"\|\$\|(.*?)\|\$\|"
        matches = re.findall(pattern, string)
        for title in matches:
            string = string.replace(f"|$|{title}|$|", f"<b>{title}<b>")
        string = re.search(
            r"&lt;legal_memorandum&gt;(.*?)&lt;\/legal_memorandum&gt;",
            string,
            re.DOTALL,
        ).group(1)
        return string

    def relevent_topics_input_generator(self, topics):
        pattern = r"\d+\.\d+:\s*(.*?)-\d+"
        matches = re.findall(pattern, topics)
        output = [match for match in matches]
        topics = LawTopics.objects.filter(name__in=output)
        topics_input_value = ""
        for topic in topics:
            topics_input_value += f"<{topic.name}>{topic.content}</{topic.name}>"
        return topics_input_value

    # def send_brief_email(self, brief_id, _relevant_topics):
    #     brief_argument_obj = BriefArgument.objects.get(id=brief_id)
    #     relevent_topics = LawTopics.objects.filter(name__in=_relevant_topics)
    #     html_content = render_to_string(
    #         "email/brief_argument.html",
    #         context={
    #             "brief_argument": brief_argument_obj,
    #             "relevent_topics": relevent_topics,
    #         },
    #     )
    #     subject = f"{brief_argument_obj.case_history.petitioner_name} v. {brief_argument_obj.case_history.respondent_name} in {brief_argument_obj.case_history.high_court}"
    #     from_email = settings.EMAIL_HOST_USER
    #     recipient_list = ["mithileshtheledgend@gmail.com"]
    #     message = EmailMultiAlternatives(
    #         subject, body="", from_email=from_email, to=recipient_list
    #     )
    #     message.attach_alternative(html_content, "text/html")
    #     message.send()
    #     brief_argument_obj.case_history.is_completed = True
    #     brief_argument_obj.case_history.save()


def main_page(request):
    csrf_token = get_token(request)
    return render(request, "brief_argument/main_page.html", {"csrf_token": csrf_token})


def step_1(request, case_id):
    csrf_token = get_token(request)
    case_history = CaseHistory.objects.get(id=case_id)
    system_instruction = get_step_1_input(
        INPUT_TOPICS, case_history.fact_case, case_history.legal_issue
    )
    context = {
        "research_input": system_instruction,
        "csrf_token": csrf_token,
    }
    return render(request, "brief_argument/step_1.html", context)


def law_topics_format_generator():
    parent_objs = LawTopics.objects.filter(parent__isnull=True)
    input_law_topics = ""
    for i, parent_obj in enumerate(parent_objs, start=1):
        input_law_topics += f"{i} {parent_obj.name}:\n"
        for y, child_obj in enumerate(parent_obj.lawtopics_set.all(), start=1):
            input_law_topics += f" {i}.{y} {child_obj.name} Size:{child_obj.token_value},\n"
    return input_law_topics


def step_2(request, brief_id):
    brief_argument = BriefArgument.objects.get(id=brief_id)
    csrf_token = get_token(request)
    system_instruction = get_step_2_input(
        brief_argument.relevant_topics,
        brief_argument.case_history.fact_case,
        brief_argument.case_history.legal_issue,
    )
    context = {
        "csrf_token": csrf_token,
        "input_1": system_instruction,
    }
    return render(request, "brief_argument/step_2.html", context)


def admin_home_page(request):
    print(law_topics_format_generator())
    case_history = CaseHistory.objects.filter(is_completed=False).order_by(
        "created_date"
    )
    count = case_history.count()
    case_history_obj = case_history.first()
    context = {
        "case_history": case_history_obj,
        "count": count,
    }
    return render(request, "brief_argument/admin_home_page.html", context)
