from playwright.sync_api import sync_playwright
import requests
import sys


def perplexity_scrape(link):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Go to the URL
        page.goto(link)
        # Wait for the necessary elements to be loaded
        page.wait_for_selector("span.rounded-md.duration-150", timeout=60000)
        page.wait_for_selector("div.prose", timeout=60000)

        # Scrape all the required text for the first structure
        titles = page.query_selector_all("span.rounded-md.duration-150")
        prose_elements = page.query_selector_all("div.prose")

        # Scrape the required text
        title_list = []
        for index, title in enumerate(titles):
            title_list.append({index: title.inner_text()})

        # Extract and print the text for div prose spans (first structure)
        combined_texts = []
        for index, prose in enumerate(prose_elements):
            combined_text = ""
            paragraphs = prose.query_selector_all("span")
            for paragraph in paragraphs:
                paragraph_text = paragraph.inner_text().strip()
                combined_text += paragraph_text + "\n"

            # Check if the list items exist inside the current div.prose
            if prose.query_selector("ul.list-disc li span"):
                # Extract the text from each li span inside ul.list-disc
                list_items = prose.query_selector_all("ul.list-disc li span")
                list_texts = [
                    f"{index}. {item.inner_text()}"
                    for index, item in enumerate(list_items, start=1)
                ]

                # Append the list texts to the combined_text variable
                combined_text += "\n" + "\n".join(list_texts)

            # Add the combined text to the list
            combined_texts.append({index: combined_text})

        merged_list = []

        # Iterate through the first list
        for title in title_list:
            key = list(title.values())[0]
            value = list(combined_texts[list(title.keys())[0]].values())[0]
            merged_dict = {key: value}
            merged_list.append(merged_dict)

        # Close browser
        browser.close()
    return merged_list


# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python perplexity_scraper.py <url> <case_id>")
#         sys.exit(1)

#     url = sys.argv[1]
#     case_id = sys.argv[2]
#     result = perplexity_scrape(url)

#     output = {"id": case_id, "scrape_link": url, "citations": result}

#     api_url = f"http://13.200.242.60:8000/api/cocounsel/{case_id}/"

#     try:
#         response = requests.put(api_url, json=output)
#         response.raise_for_status()  # Raises an HTTPError for bad responses
#         print(f"Successfully updated API for case ID: {case_id}")
#         print(f"API Response: {response.json()}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error updating API: {e}")


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
from selenium.webdriver.common.action_chains import ActionChains
import shutil
import pyautogui  # You'll need to install this: pip install pyautogui
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)


# Path to your original Chrome user data
# ORIGINAL_PROFILE = r"C:\Users\rithi\AppData\Local\Google\Chrome\User Data"

# Path where you want to save the copy
# COPY_PROFILE = r"C:\Users\rithi\chromeprofile"

# Path to your original Chrome user data on macOS
ORIGINAL_PROFILE = os.path.expanduser(
    "'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)

# Path where you want to save the copy
COPY_PROFILE = os.path.expanduser("~/ChromeProfile")


def click_element(driver, element):
    try:
        # Try to click normally first
        element.click()
    except ElementClickInterceptedException:
        # If normal click fails, try JavaScript click
        driver.execute_script("arguments[0].click();", element)

def input_section(driver, section_name):
    # Wait for the input field to be present and interactable
    input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="What is this section about?"]')
        )
    )

    # Enter text into the input field and press Enter
    input_element.send_keys(section_name)
    input_element.send_keys(Keys.RETURN)

    # Wait for a moment to ensure everything has loaded after scrolling
    time.sleep(10)




def automated_login_with_profile(memo, step_1_input, step_1_folder_path):
    options = Options()
    options.add_argument(f"user-data-dir={COPY_PROFILE}")
    options.add_argument("profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    try:
        # Open Perplexity.ai
        driver.get("https://www.perplexity.ai")
        print("Opened Perplexity.ai")

        # Wait for manual login
        time.sleep(2)

        # Wait for the search box to be present and interactable
        search_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div/main/div/div/div[2]/div/div/div/div[1]/div[2]/div/div/div[2]/span/div/div/div[1]/textarea",
                )
            )
        )

        # Enter text in the search box
        search_box.clear()
        # search_box.send_keys(Keys.TAB)

        #  Find and click the attach button
        # attach_button = WebDriverWait(driver, 20).until(
        #     EC.element_to_be_clickable(
        #         (
        #             By.XPATH,
        #             "/html/body/div/main/div/div/div[2]/div/div/div/div[1]/div[2]/div/div/div[2]/span/div/div/div[2]/div[2]/button/div",
        #         )
        #     )
        # )
        # driver.execute_script("arguments[0].click();", attach_button)
        # print("Clic ked attach button")

        # Navigate to the directory
        # pyautogui.write(step_1_folder_path)
        # pyautogui.press("enter")
        # time.sleep(1)  # Wait for directory to open

        # # Type the file name
        # pyautogui.write(step_1_folder_path)
        # time.sleep(1)

        # # Press Enter to select the file
        # pyautogui.press("enter")

        # # print("File selected for follow-up")

        # # Wait for the file to be processed
        # time.sleep(10)

        # # Wait for the file dialog to appear
        # time.sleep(2)

        search_box.send_keys("""Whether the gro.""")
        # time.sleep(10)
        search_box.send_keys(Keys.TAB)
        # search_box.send_keys(Keys.RETURN)
        print("Entered search text")

        #
        # print("File selected")

        # Wait for a few seconds to allow the file to be processed
        # time.sleep(10)

        # Click the go button
        go_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit']"))
        )
        driver.execute_script("arguments[0].click();", go_button)
        print("Clicked go button")

        # Wait for the answer to generate (adjust time as needed)
        time.sleep(50)

        # Attempt to scrape the first answer
        try:
            # Wait for the main div to be present
            main_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.prose.dark\\:prose-invert")
                )
            )
            # Extract the main text
            all_text = main_div.text

            print("Scraped first answer:")
            print(all_text)
        except Exception as e:
            print(f"Couldn't scrape first answer: {e}")

        # Wait a bit longer before interacting with follow-up box
        time.sleep(10)

        # Follow-up query
        # max_attempts = 3
        # for attempt in range(max_attempts):
            # try:
        follow_up_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div/div/div/span/div/div/div[1]/textarea",
                )
            )
        )

        # Scroll the element into view
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", follow_up_box
        )
        time.sleep(2)  # Wait for any animations to complete

        # Try to interact using different methods
        # try:
        follow_up_box.clear()
        follow_up_box.send_keys("Brief Fact + Legal Issue")
            # except ElementNotInteractableException:
            #     ActionChains(driver).move_to_element(
            #         follow_up_box
            #     ).click().send_keys("Brief Fact + Legal Issue").perform()
            # except Exception:
            #     driver.execute_script(
            #         "arguments[0].value = arguments[1];",
            #         follow_up_box,
            #         "Brief Fact + Legal Issue",
            #     )

        print("Entered follow-up query")
        # break
            # except (
            #     StaleElementReferenceException,
            #     ElementNotInteractableException,
            # ) as e:
            #     if attempt == max_attempts - 1:
            #         print(
            #             f"Failed to interact with follow-up box after {max_attempts} attempts: {e}"
            #         )
            #     else:
            #         print(f"Attempt {attempt + 1} failed, retrying...")
            #         time.sleep(2)

        # Find and click the attach button for follow-up
        try:
            attach_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div/div/div/span/div/div/div[2]/div/button/div",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", attach_button)
            print("Clicked attach button for follow-up")
        except Exception as e:
            print(f"Failed to click attach button: {e}")

        # Wait for the file dialog to appear
        time.sleep(2)

        # File path and name (same as before)
        # file_path = r"C:\Users\rithi\Desktop"
        # file_name = "iea_1872.pdf"

        
        # Click the go button for follow-up
        go_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit']"))
        )
        driver.execute_script("arguments[0].click();", go_button)
        print("Clicked go button for follow-up")

        # Wait for the second answer to generate
        time.sleep(45)

        # Attempt to scrape the second answer
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.prose.dark\\:prose-invert")
                )
            )

            # Find all elements with the class
            divs = driver.find_elements(
                By.CSS_SELECTOR, "div.prose.dark\\:prose-invert"
            )

            # Select the last one
            if divs:
                main_div = divs[-1]
                # Extract all text from the main div
                raw_text = main_div.text

                # Remove any extra whitespace and normalize line breaks
                # raw_text = ' '.join(raw_text.split())

                print(raw_text)
                # return raw_text
            else:
                print("No elements found with the specified class")
                # return ""

            # Remove any extra whitespace and normalize line breaks
            # raw_text = ' '.join(raw_text.split())
            print("Scraped second answer:")
        except Exception as e:
            print(f"Couldn't scrape second answer: {e}")

        # Click on "Convert to Page" button
        try:
            convert_to_page_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div/main/div/div/div[2]/div/div/div[1]/div/div[4]/div[1]/button/div/div",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", convert_to_page_button)
            print("Clicked 'Convert to Page' button")
        except Exception as e:
            print(f"Failed to click 'Convert to Page' button: {e}")

        # Wait for the page to load (400 seconds as requested)
        print("Waiting for page to load...")
        time.sleep(40)

        # Scroll to the bottom of the page
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # print("Scrolled to the bottom of the page")

        # Wait for a moment to ensure everything has loaded after scrolling
        # time.sleep(5)

        # Take a screenshot
        # screenshot_path = os.path.join(os.getcwd(), "page_at_draft_box.png")
        # driver.save_screenshot(screenshot_path)
        # print(f"Screenshot saved at: {screenshot_path}")

        # Print page source
        print("Page source:")

        # List of sections to input
        sections = [
            "Draft Question Presented",
            "Draft Brief Answer",
            "Draft Statement of Facts",
            "Draft Conclusion"
        ]

        # Input each section
        for section in sections:
            input_section(driver, section)


        # Wait for the input field to be present and interactable
        # input_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, 'input[placeholder="What is this section about?"]')
        #     )
        # )

        # Enter text into the input field
        # input_element.send_keys("Draft Question Presented")

        # Press the Enter key
        # input_element.send_keys(Keys.RETURN)

        # Wait for a moment to ensure everything has loaded after scrolling
        # time.sleep(10)

        # Wait for the input field to be present and interactable
        # input_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, 'input[placeholder="What is this section about?"]')
        #     )
        # )

        # Enter text into the input field
        # input_element.send_keys("Draft Statement of Facts")

        # Press the Enter key
        # input_element.send_keys(Keys.RETURN)

        # Wait for a moment to ensure everything has loaded after scrolling
        # time.sleep(10)

        # Wait for the input field to be present and interactable
        # input_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, 'input[placeholder="What is this section about?"]')
        #     )
        # )

        # Enter text into the input field
        # input_element.send_keys("Draft Discussion")

        # Press the Enter key
        # input_element.send_keys(Keys.RETURN)

        # Wait for a moment to ensure everything has loaded after scrolling
        # time.sleep(10)

        # Wait for the input field to be present and interactable
        # input_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, 'input[placeholder="What is this section about?"]')
        #     )
        # )

        # Enter text into the input field
        # input_element.send_keys("Draft Conclusion")

        # Press the Enter key
        # input_element.send_keys(Keys.RETURN)

        # Wait for a moment to ensure everything has loaded after scrolling
        # time.sleep(10)

        # Wait for the page to load
        # wait = WebDriverWait(driver, 10)

        # try:
        #     # Find all main div elements
        #     main_divs = WebDriverWait(driver, 10).until(
        #         EC.presence_of_all_elements_located(
        #             (
        #                 By.XPATH,
        #                 "//div[contains(@class, 'flex flex-col grid-cols-12 gap-md md:gap-xl max-w-threadWidth w-full md:grid')]",
        #             )
        #         )
        #     )

        # Iterate through each main div
        # for main_div in main_divs:
        #     try:
        #         # 1. Find and click the 'Edit' button within this main div
        #         edit_button = main_div.find_element(
        #             By.XPATH, ".//button[.//div[contains(text(), 'Edit')]]"
        #         )
        #         click_element(driver, edit_button)

        #         # Wait for 2 seconds
        #         time.sleep(2)

        #         # 2. Find and click the 'Concise' button within this main div
        #         concise_button = WebDriverWait(driver, 10).until(
        #             EC.element_to_be_clickable(
        #                 (By.XPATH, ".//button[.//div[contains(text(), 'Concise')]]")
        #             )
        #         )
        #         # concise_button.click()
        #         click_element(driver, concise_button)

        #         # 3. Wait for the dropdown to appear
        #         dropdown = WebDriverWait(driver, 10).until(
        #             EC.visibility_of_element_located(
        #                 (
        #                     By.XPATH,
        #                     "//div[contains(@class, 'animate-in fade-in zoom-in-95')]",
        #                 )
        #             )
        #         )

        #         # 4. Find and click the 'Detailed' option within the dropdown
        #         detailed_option = dropdown.find_element(
        #             By.XPATH,
        #             ".//div[contains(@class, 'relative cursor-pointer select-none rounded')]//span[text()='Detailed']/ancestor::div[contains(@class, 'relative cursor-pointer select-none rounded')]",
        #         )

        #         # Scroll the element into view
        #         driver.execute_script(
        #             "arguments[0].scrollIntoView(true);", detailed_option
        #         )

        #         # Move to the element and click
        #         ActionChains(driver).move_to_element(
        #             detailed_option
        #         ).click().perform()

        #         # Find the div containing the button
        #         button_container = WebDriverWait(main_div, 10).until(
        #             EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'flex w-full items-end justify-between gap-sm')]"))
        #         )

        #         # Find and click the arrow button within this container
        #         arrow_button_xpath = ".//button[contains(@class, 'bg-super') and contains(@class, 'dark:bg-superDark') and .//svg[contains(@class, 'fa-arrow-right')]]"

        #         arrow_button = WebDriverWait(button_container, 10).until(
        #             EC.element_to_be_clickable((By.XPATH, arrow_button_xpath))
        #         )
        #         print("Arrow button found")

        #         try:
        #             # Find the div containing the button
        #             button_container = WebDriverWait(main_div, 10).until(
        #                 EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'flex w-full items-end justify-between gap-sm')]"))
        #             )

        #             # Find and click the arrow button within this container
        #             arrow_button_xpath = ".//button[contains(@class, 'bg-super') and contains(@class, 'dark:bg-superDark') and .//svg[contains(@class, 'fa-arrow-right')]]"

        #             arrow_button = WebDriverWait(button_container, 10).until(
        #                 EC.element_to_be_clickable((By.XPATH, arrow_button_xpath))
        #             )
        #             print("Arrow button found")

        #             # Scroll the button into view
        #             driver.execute_script("arguments[0].scrollIntoView(true);", arrow_button)

        #             # Try multiple click methods
        #             try:
        #                 click_element(driver, arrow_button)
        #                 print("Clicked arrow button successfully")
        #             except Exception as e:
        #                 print(f"Error clicking arrow button: {e}")
        #                 print("Attempting to click with ActionChains...")
        #                 ActionChains(driver).move_to_element(arrow_button).click().perform()

        #             # Wait for 10 seconds
        #             time.sleep(10)
        #             print("Completed 10-second wait after clicking arrow button")

        #         except TimeoutException:
        #             print(f"Could not find or click the arrow button in div")

        #         print(
        #             f"Successfully completed actions for div {main_divs.index(main_div) + 1}"
        #         )

        #     except TimeoutException:
        #         print(
        #             f"Timed out waiting for element in div {main_divs.index(main_div) + 1}"
        #         )
        #     except Exception as e:
        #         print(
        #             f"An error occurred in div {main_divs.index(main_div) + 1}: {e}"
        #         )

        # except TimeoutException:
        #     print("Timed out waiting for main div elements")
        # except Exception as e:
        #     print(f"An error occurred: {e}")

        # Attempt to scrape the content of the converted page
        try:
            page_content = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div/main/div/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]",
                    )
                )
            )
            content_text = page_content.text
            # Wait for the necessary elements to be loaded
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.rounded-md.duration-150")
                )
            )
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.prose"))
            )

            # Scrape all the required text for the first structure
            titles = driver.find_elements(
                By.CSS_SELECTOR, "span.rounded-md.duration-150"
            )
            prose_elements = driver.find_elements(By.CSS_SELECTOR, "div.prose")

            # Scrape the required text
            title_list = []
            for index, title in enumerate(titles):
                title_list.append({index: title.text})

            # Extract and print the text for div prose spans (first structure)
            combined_texts = []
            for index, prose in enumerate(prose_elements):
                combined_text = ""
                paragraphs = prose.find_elements(By.CSS_SELECTOR, "span")
                for paragraph in paragraphs:
                    paragraph_text = paragraph.text.strip()
                    combined_text += paragraph_text + "\n"

                # Check if the list items exist inside the current div.prose
                list_items = prose.find_elements(
                    By.CSS_SELECTOR, "ul.list-disc li span"
                )
                if list_items:
                    # Extract the text from each li span inside ul.list-disc
                    list_texts = [
                        f"{idx}. {item.text}"
                        for idx, item in enumerate(list_items, start=1)
                    ]

                    # Append the list texts to the combined_text variable
                    combined_text += "\n" + "\n".join(list_texts)

                # Add the combined text to the list
                combined_texts.append({index: combined_text})

            merged_list = []

            # Iterate through the first list
            for title in title_list:
                key = list(title.values())[0]
                value = list(combined_texts[list(title.keys())[0]].values())[0]
                merged_dict = {key: value}
                merged_list.append(merged_dict)
            print("Scraped content from converted page:")
            for i in merged_list:
                print(i)
                print()

            memo_url = f"http://localhost:8000/api/cocounsel/{memo["id"]}/"
            memo['citations'] = merged_list

            # Prepare the headers for the request
            headers = {
                'Content-Type': 'application/json',
                # Add any other necessary headers, like authorization tokens
            }
            # Make the PUT request
            try:
                response = requests.put(memo_url, json=data, headers=headers)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                print("Successfully updated memo citations")
            except requests.exceptions.RequestException as e:
                print(f"Error updating memo citations: {e}")
        except Exception as e:
            print(f"Couldn't scrape content from converted page: {e}")

        # Keep the browser open for manual inspection
        input("Press Enter to close the browser...")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()


# Function to create a file
def write_to_file(filename, text):
    try:
        with open(filename, "w") as file:
            file.write(text)
        print(f"Text successfully written to {filename}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")


def create_folder(folder_path):
    """Create a folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")


# First, copy the profile (only needs to be done once)
# copy_chrome_profile()

# Then use the copied profile for automation

if __name__ == "__main__":

    get_case = f"http://localhost:8000/api/cocounsel/get_cocounse_value/"
    response = requests.get(get_case)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # print("Data::", data)
    elif response.status_code == 404:
        print("::::No Cocounsel Yet:::::")

    data = {
        "id": "9da21853-e316-4aa7-92a8-e72230f3deca",
        "legal_issue": "legal",
        "brief_facts": "brief",
        "case_facts": "case",
        "legal_research": "legal-research",
        "research_analysis": "",
        "search_query": "",
        "is_completed": False,
        "citations": {},
        "scrape_link": None,
        "case_ids_list": "",
        "created_date": "2024-07-20T11:55:13.601597Z",
        "modified_date": "2024-07-20T11:55:13.601616Z",
    }

    step_1_input = f"{data['brief_facts']} {data['legal_issue']}"

    base_path = "/Users/mithilesh/law/step_1_files"
    step_1_folder_path = os.path.join(base_path, data["id"])

    # Create folder
    create_folder(step_1_folder_path)
    print("PARENT FOLDER::", step_1_folder_path)
    # Write files
    write_to_file(
        os.path.join(step_1_folder_path, "case_facts.txt"), data["case_facts"]
    )
    write_to_file(
        os.path.join(step_1_folder_path, "legal_research.txt"), data["legal_research"]
    )

    automated_login_with_profile(data, step_1_input, step_1_folder_path)

    # try:
    #     response.raise_for_status()  # Raises an HTTPError for bad responses
    #     # print(f"Successfully updated API for case ID: {case_id}")
    #     print(f"API Response: {response.json()}")
    # except requests.exceptions.RequestException as e:
    #     print(f"Error updating API: {e}")
