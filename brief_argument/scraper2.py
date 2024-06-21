import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright
from asgiref.sync import sync_to_async
from brief_argument.models import Case, CaseNote, Caseparagraph


@sync_to_async
def get_chatroom(case_info, paragraph_list, case_notes_list):
    # create the case obj first.
    case_obj = Case.objects.create(
        code=case_info["code"],
        court=case_info["court"],
        judges=case_info["judges"],
        petitioner=case_info["petitioner"],
        respondent=case_info["respondent"],
        citations=case_info["citations"],
    )
    # create the passage object first.
    relevant_passage = [
        Caseparagraph(**para_item, case=case_obj) for para_item in paragraph_list
    ]
    para_result = Caseparagraph.objects.bulk_create(relevant_passage)
    for case_note in case_notes_list:
        para_number = list(map(int, case_note["paragraph"]))
        para_number = list(set(para_number))
        para_objs = [
            para
            for para in para_result
            if para.case == case_obj and para.number in para_number
        ]
        del case_note["paragraph"]
        case_note_obj = CaseNote(**case_note, case=case_obj)
        case_note_obj.save()
        case_note_obj.paragraph.add(*para_objs)
    return True


def run(playwright):
    browser = playwright.chromium.launch(
        headless=False
    )  # Set to True for headless mode
    context = browser.new_context()
    page = context.new_page()

    # Step 1: Go to the login page
    page.goto("https://www.aironline.in/login.html")

    # Step 2: Enter user ID
    page.fill("#userName_Id", "jishnu008")

    # Step 3: Enter password
    page.fill("#password_Id", "Jishnu@008")

    # Step 4: Click the submit button
    page.click("#submitButton_Id")

    # Wait for some time to ensure the page loads completely
    page.wait_for_timeout(5000)

    # Step 5: Navigate through the specified elements
    page.click(".tabbed #topic_browse_login")
    page.wait_for_timeout(8000)
    page.click(".data1 #data_2023")
    page.wait_for_timeout(8000)
    page.click(".data2 #data_allindiareporter")
    page.wait_for_timeout(8000)
    page.click(".data3 #data_fullreport")
    page.wait_for_timeout(8000)
    page.click(".data4 #data_supremecourtofindia")
    page.wait_for_timeout(8000)

    # Function to scrape the case details
    def scrape_case(new_page):
        # Scrape case ID
        case_id_element = new_page.query_selector(
            ".fullContentDiv .Publication_Citation_Text .fcCitationJudgementHeading span"
        )
        if case_id_element:
            case_id = case_id_element.text_content().strip()

        # Scrape judges
        judges_element = new_page.query_selector(
            ".Judge_Display_Name .fcCitationJudgeNameHeading"
        )
        if judges_element:
            judges_text = judges_element.text_content().replace("Hon'ble Judge(s):", "")
            judges = [
                judge.strip() for judge in judges_text.split(",") if judge.strip()
            ]

        # Scrape petvres
        petvres_element = new_page.query_selector(".fullcontentData")
        if petvres_element:
            petvres = re.sub(r"\s+", " ", petvres_element.text_content()).strip()
            petitioner, respondent = petvres.split("v.")

        # print("Headnotes:")
        headnote_elements = new_page.query_selector_all(".fullContentBlock .HeadNote")
        headnote_count = 1
        case_notes_list = []
        for headnote_element in headnote_elements:
            if headnote_element.query_selector(".CaseReferenceMainDiv"):
                break

            short_note_para = headnote_element.query_selector(".ShortNotePara")
            long_note_para = headnote_element.query_selector(".LongNotePara")

            short_note_text = ""
            long_note_text = ""
            short_note_para_numbers = []
            long_note_para_numbers = []
            pattern = r"^.*(?=\(Para)"

            if short_note_para:
                judgement_text_paras = short_note_para.query_selector_all(
                    ".Judgement_Text_Para"
                )
                for judgement_text_para in judgement_text_paras:
                    para_text = judgement_text_para.evaluate("el => el.textContent")
                    short_note_text += para_text + " "
                if "(Para" in short_note_text:
                    short_note_text = short_note_text.replace("\n", "")
                    short_note_text = short_note_text.replace("\t", "")
                    # print("SHORT NOTES TEST::", short_note_text)
                    match = re.search(pattern, short_note_text)
                    short_note_text = match.group(0)

                judgement_para_no = short_note_para.query_selector(".JudgementParaNo")
                if judgement_para_no:
                    short_note_text = short_note_text.replace(
                        judgement_para_no.text_content(), ""
                    ).strip()

                para_numbers_element = short_note_para.query_selector(
                    ".ParaNumbersLabel"
                )
                if para_numbers_element:
                    short_note_para_numbers = para_numbers_element.evaluate(
                        'el => Array.from(el.querySelectorAll("a.ParaNumbersLinks")).map(a => a.textContent)'
                    )

            if long_note_para:
                judgement_text_paras = long_note_para.query_selector_all(
                    ".Judgement_Text_Para"
                )
                long_note_para_numbers = []

                for judgement_text_para in judgement_text_paras:
                    para_text = judgement_text_para.evaluate("el => el.textContent")
                    long_note_text += para_text + " "

                    para_numbers_element = judgement_text_para.query_selector(
                        ".ParaNumbersLabel"
                    )
                    if para_numbers_element:
                        para_numbers = para_numbers_element.evaluate(
                            'el => Array.from(el.querySelectorAll("a.ParaNumbersLinks")).map(a => a.textContent)'
                        )
                        long_note_para_numbers.extend(para_numbers)

                judgement_para_no = long_note_para.query_selector(".JudgementParaNo")
                if judgement_para_no:
                    long_note_text = long_note_text.replace(
                        judgement_para_no.text_content(), ""
                    ).strip()
                    long_note_text = long_note_text.replace("\n", "")
                    long_note_text = long_note_text.replace("\t", "")
                    # print("LONG NOTE::", long_note)
                    if "(Para" in long_note_text:
                        match = re.search(pattern, long_note_text)
                        long_note_text = match.group(0)

                if not long_note_para_numbers:
                    long_note_para_numbers = []

            if short_note_text.strip() or long_note_text.strip():
                para_numbers = short_note_para_numbers + long_note_para_numbers
                case_notes_list.append(
                    {
                        "short_text": short_note_text.strip() + long_note_text.strip(),
                        "paragraph": para_numbers,
                    }
                )
                headnote_count += 1

        # print("Cases Referred:")
        case_reference_elements = new_page.query_selector_all(".CaseReferenceMainDiv")
        citation_count = 1
        case_citation_list = []
        for case_reference_element in case_reference_elements:
            citation_div = case_reference_element.query_selector(".CaseReferenceDiv")
            if citation_div:
                citation_texts = []
                direct_citation_text = citation_div.text_content().strip()
                if direct_citation_text:
                    citation_texts.append(direct_citation_text)
                judgement_text_citations = citation_div.query_selector_all(
                    ".judgementTextCitation"
                )
                if judgement_text_citations:
                    citation_texts.extend(
                        [
                            citation_text.evaluate("el => el.textContent")
                            for citation_text in judgement_text_citations
                        ]
                    )
                # print("WHat is the citations HAHAHAHA:::", citation_texts)
                formatted_citation_text = " : ".join(citation_texts)
                if ":" in formatted_citation_text:
                    parts = formatted_citation_text.split(":")
                    variable_1 = parts[0].strip()
                    variable_2 = parts[1].strip()

                para_numbers_container = case_reference_element.query_selector(
                    ".ParaNumbersDivCaseReferred"
                )
                if para_numbers_container:
                    para_numbers = para_numbers_container.evaluate(
                        'el => Array.from(el.querySelectorAll(".ParaNumbersCaseReferred")).map(a => a.textContent)'
                    )
                if variable_1 and variable_2:
                    case_citation_list.append(
                        {
                            "name": variable_1,
                            "paragraph": para_numbers if para_numbers else None,
                        }
                    )
                    case_citation_list.append(
                        {
                            "name": variable_2,
                            "paragraph": para_numbers if para_numbers else None,
                        }
                    )
                else:
                    case_citation_list.append(
                        {
                            "name": formatted_citation_text,
                            "paragraph": para_numbers if para_numbers else None,
                        }
                    )
                citation_count += 1

        # Scrape paragraphs
        paragraph_list = []
        paragraph_elements = new_page.query_selector_all(".Judgement_Text_Div")
        paragraph_count = 1
        current_paragraph = []
        for paragraph_element in paragraph_elements:
            para_number = paragraph_element.query_selector(".JudgementParaNo")
            paragraph_texts = paragraph_element.query_selector_all(
                ".Judgement_Text_Para"
            )

            if para_number and current_paragraph:
                combined_text = " ".join([p.text_content() for p in current_paragraph])
                # print(f"Paragraph {paragraph_count} Text:", combined_text)
                paragraph_list.append(
                    {
                        "number": paragraph_count,
                        "text": combined_text,
                    }
                )
                # print()  # Add a new line between paragraphs
                paragraph_count += 1
                current_paragraph = []

            current_paragraph.extend(paragraph_texts)
        # Print the last paragraph
        if current_paragraph:
            combined_text = " ".join([p.text_content() for p in current_paragraph])
            # print(f"Paragraph {paragraph_count} Text:", combined_text)
            paragraph_list.append(
                {
                    "number": paragraph_count,
                    "text": combined_text,
                }
            )

        unique_names = set()
        case_citation_list = [
            d
            for d in case_citation_list
            if d["name"] not in unique_names and not unique_names.add(d["name"])
        ]

        # print(unique_data)
        case_info = {
            "code": case_id,
            "court": "Supreme Court Of India",
            "judges": judges,
            "petitioner": petitioner,
            "respondent": respondent,
            "citations": case_citation_list,
        }
        return (
            case_info,
            paragraph_list,
            case_notes_list,
        )

    default_node_index = 30  # Set the default node index to start from
    case_name = None
    # Loop for repeating the process
    while True:
        # Get the nodes to iterate over
        nodes = page.query_selector_all("#CitationTree .data .fullContent")

        # Check if the default node index is within the range of available nodes
        if default_node_index < len(nodes):
            # Iterate over the nodes starting from the default node index
            for node_index in range(default_node_index, len(nodes)):
                node = nodes[node_index]
                wait_times = [12000, 30000, 45000, 60000]  # wait times for each attempt

                # try:
                # Wait for some time before clicking the node
                # page.wait_for_timeout(5000)  # Adjust the timeout as needed
                for wait_time in wait_times:
                    try:
                        new_page.wait_for_timeout(wait_time)
                        break
                    except:
                        print(
                            f"Before popup Timeout occurred after {wait_time/1000} seconds, trying again..."
                        )
                # Adjust the timeout as needed

                # Click the node to open a new page
                with page.expect_popup() as popup_info:
                    node.click()
                new_page = popup_info.value

                # Wait for the new page to load
                # new_page.wait_for_timeout(12000)

                for wait_time in wait_times:
                    try:
                        new_page.wait_for_timeout(wait_time)
                        break
                    except:
                        print(
                            f"Timeout occurred after {wait_time/1000} seconds, trying again..."
                        )
                # Adjust the timeout as needed

                # Scrape the case details
                case_info, paragraph_list, case_notes_list = scrape_case(new_page)
                with ThreadPoolExecutor() as executor:
                    executor.submit(
                        asyncio.run,
                        get_chatroom(case_info, paragraph_list, case_notes_list),
                    )

                # Close the second tab
                new_page.close()

                # Increment the default node index after successful scraping
                default_node_index = node_index + 1
                case_name = case_info["code"]
                print(f"CASE No. {default_node_index }---{case_name}")


def run_playwright():
    with sync_playwright() as playwright:
        run(playwright)
