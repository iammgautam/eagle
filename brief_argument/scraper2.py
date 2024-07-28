import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from asgiref.sync import sync_to_async
import random
import time
import logging
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)
from brief_argument.models import Case, CaseNote, Caseparagraph

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

credentials_list = [
    {"username": "rith005", "password": "Rith@005"},
    {"username": "jishnu008", "password": "Jishnu@008"},
    {"username": "paul008", "password": "Jishnu@008"},
    {"username": "nunu008", "password": "Nunu@008"},
    {"username": "gautam008", "password": "Gautam@008"},
    {"username": "mithilesh008", "password": "Mithilesh@008"},
]


@sync_to_async
def save_in_db(case_info, paragraph_list, case_notes_list):
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


def get_random_credentials():
    return random.choice(credentials_list)


def logout_modal_popup(page, password):
    # Wait for and locate the specific logout dialog
    logout_dialog_selector = 'div[role="dialog"]:has-text("Please Logout from devices")'
    logout_dialog = page.locator(logout_dialog_selector)

    # Wait for the dialog to be visible
    logout_dialog.wait_for(state="visible", timeout=5000)

    if logout_dialog.is_visible():
        print("Logout dialog found. Proceeding with logout process.")

        # Select the "Select All" checkbox
        select_all = logout_dialog.locator(
            'input[type="checkbox"]:right-of(:text("Select All"))'
        )
        if select_all.is_visible():
            select_all.check()
            print("Selected 'Select All' checkbox.")
        else:
            print("Warning: 'Select All' checkbox not found or not visible.")

        # Click the "LOGOUT" button
        logout_button = logout_dialog.locator('button:has-text("LOGOUT")')
        if logout_button.is_visible():
            logout_button.click()
            print("Clicked the LOGOUT button.")

            # Wait for the password confirmation dialog
            password_dialog_selector = (
                'div[role="dialog"]:has(#password):has-text("Confirm Password")'
            )
            password_dialog = page.locator(password_dialog_selector)
            expect(password_dialog).to_be_visible(timeout=5000)

            # try:
            password_dialog.wait_for(state="visible", timeout=5000)
            if password_dialog.is_visible():
                print("Password confirmation dialog found.")

                # Enter the password
                password_input = password_dialog.locator("#password")
                if password_input.is_visible():
                    password_input.fill(password)
                    print("Entered the password.")
                else:
                    print("Warning: Password input field not found or not visible.")

                # Click the final "Logout" button
                final_logout_button = password_dialog.locator(
                    'button:has-text("Logout")'
                )
                if final_logout_button.is_visible():
                    final_logout_button.click()
                    print("Clicked the final Logout button.")
                    return True
    else:
        return False


def login(page, credentials, max_retries=3):
    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt {attempt + 1}/{max_retries}")
            page.goto("https://www.aironline.in/login.html", timeout=30000)
            page.fill("#userName_Id", credentials["username"])
            page.fill("#password_Id", credentials["password"])
            page.click("#submitButton_Id")

            # Wait for navigation to complete
            page.wait_for_load_state("networkidle", timeout=0)
            # time.sleep(5)
            # Check for logout modal
            try:
                if logout_modal_popup(page, credentials["password"]):
                    logging.info("Logout process completed. Retrying login.")
                    continue  # Retry login after logout
            except Exception as e:
                logging.info("Extra Login Popup not Found.")

            try:
                if page.url == "https://www.aironline.in/AuthenticateUser.html":
                    logging.info("AuthenticateUser page detected. Going to login page.")
                    credentials = get_random_credentials()
                    login(page, credentials)
            except Exception as e:
                logging.info("Another Opps! Error not found.")

            # Check if login was successful
            if page.url != "https://www.aironline.in/login.html":
                logging.info(f"Login successful with {credentials['username']}")
                return True
            else:
                logging.warning("Login unsuccessful. URL did not change as expected.")

        except Exception as e:
            logging.error(f"Error during login attempt: {str(e)}")

        if attempt < max_retries - 1:
            logging.info("Retrying login...")
        else:
            logging.error("Max login attempts reached. Login failed.")

    return False


def navigate_to_cases(page, year, max_retries=3):
    steps = [
        (".tabbed #topic_browse_login", 8000),
        (f".data1 #data_{year}", 8000),
        (".data2 #data_allindiareporter", 8000),
        (".data3 #data_fullreport", 8000),
        (".data4 #data_supremecourtofindia", 8000),
    ]

    for selector, wait_time in steps:
        for attempt in range(max_retries):
            try:
                page.click(selector)
                logging.info(f"Selected {selector} going for next selector")
                page.wait_for_load_state("networkidle", timeout=0)
                break
            except PlaywrightTimeoutError:
                if attempt == max_retries - 1:
                    logging.error(f"Navigation failed at step {selector}")
                    return False
                logging.warning(
                    f"Navigation attempt {attempt + 1} failed for {selector}. Retrying..."
                )

    logging.info("Navigation to cases successful")
    return True


def scrape_case(new_page):
    # Function to scrape the case details
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
        judges = [judge.strip() for judge in judges_text.split(",") if judge.strip()]

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

            para_numbers_element = short_note_para.query_selector(".ParaNumbersLabel")
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
    # Initialize variables
    variable_1 = None
    variable_2 = None
    para_numbers = None

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
        paragraph_texts = paragraph_element.query_selector_all(".Judgement_Text_Para")

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


def check_for_max_usage_error(page):
    try:
        error_message = page.locator("p.couponErrorMessage")
        # expect(error_message).to_contain_text("You Exceed Maximum Usage", timeout=0)
        if error_message.is_visible():
            # If the error message is found, attempt to click the logout button
            logout_button = page.locator("#userLogoutBtn_Id")
            if logout_button.is_visible():
                logout_button.click()
                page.wait_for_load_state("networkidle", timeout=0)
                logging.info(
                    "Clicked logout button after detecting maximum usage error."
                )
                return True
            else:
                logging.warning(
                    "Logout button not found after detecting maximum usage error."
                )
                return False

    except Exception as e:
        logging.debug(f"No maximum usage error detected: {str(e)}")
        return False
    except:
        return False


def run(playwright, start_index=1, max_restarts=10, start_year=2006, end_year=1950):
    current_year = start_year
    while current_year >= end_year:
        restart_count = 0
        while restart_count < max_restarts:
            try:
                browser = playwright.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                credentials = get_random_credentials()
                if not login(page, credentials):
                    raise Exception("Login failed")

                if not navigate_to_cases(page, current_year):
                    raise Exception("Navigation failed")
                time.sleep(10)
                nodes = page.query_selector_all("#CitationTree .data .fullContent")

                # Adjust the starting index to be 0-based
                adjusted_start_index = start_index - 1 if start_index > 0 else 0

                for node_index in range(adjusted_start_index, len(nodes)):
                    node = nodes[node_index]

                    with page.expect_popup() as popup_info:
                        node.click()
                    new_page = popup_info.value

                    new_page.wait_for_load_state("networkidle", timeout=0)

                    if check_for_max_usage_error(new_page):
                        new_page.close()
                        if "browser" in locals():
                            browser.close()

                    try:
                        case_info, paragraph_list, case_notes_list = scrape_case(
                            new_page
                        )
                    except Exception as e:
                        # time.sleep(30)
                        new_page.close()
                        start_index = node_index + 1
                        case_name = case_info["code"]
                        logging.info(f"SKIPPING CASE No. {start_index}---{case_name}")

                    if case_info is None:
                        logging.warning(
                            f"Failed to scrape case at index {node_index}. Skipping..."
                        )
                        continue

                    # with ThreadPoolExecutor() as executor:
                    #     executor.submit(
                    #         asyncio.run,
                    #         save_in_db(case_info, paragraph_list, case_notes_list),
                    #     )

                    new_page.close()
                    start_index = node_index + 1
                    case_name = case_info["code"]
                    logging.info(f"CASE No. {start_index}---{case_name}")

                # If we've successfully processed all cases for the current year, move to the next year
                logging.info(
                    f"All cases processed successfully for year {current_year}"
                )
                if start_index == len(nodes):
                    current_year -= 1
                    start_index = 1  # Reset start_index for the new year
                    break  # Break out of the restart loop

            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                restart_count += 1
                logging.info(
                    f"Restarting the process for year {current_year} from index {start_index}. Restart count: {restart_count}"
                )
                if "browser" in locals():
                    browser.close()
                time.sleep(5)  # Wait for 5 seconds before restarting

        if restart_count == max_restarts:
            logging.error(
                f"Maximum restarts ({max_restarts}) reached for year {current_year}. Moving to next year..."
            )
            current_year -= 1
            start_index = 1  # Reset start_index for the new year

    logging.info(f"Finished scraping all years from {start_year} to {end_year}")


def run_playwright():
    with sync_playwright() as playwright:
        run(playwright)


if __name__ == "__main__":
    run_playwright()
