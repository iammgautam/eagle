import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pyautogui  # You'll need to install this: pip install pyautogui

ORIGINAL_PROFILE = os.path.expanduser(
    "'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)

# Path where you want to save the copy
COPY_PROFILE = os.path.expanduser("~/ChromeProfile")


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

    # try:
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
    search_box.clear()
    search_box.send_keys(Keys.TAB)

    attach_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/div/main/div/div/div[2]/div/div/div/div[1]/div[2]/div/div/div[2]/span/div/div/div[2]/div[2]/button/div",
            )
        )
    )
    driver.execute_script("arguments[0].click();", attach_button)
    print("Clicked attach button")

    # Wait for the file dialog to appear
    time.sleep(2)

    # File path and name
    file_path = step_1_folder_path
    file_name = '"case_facts.txt" "legal_research.txt"'

    # Navigate to the directory
    pyautogui.write(file_path)
    pyautogui.press("enter")
    time.sleep(1)  # Wait for directory to open

    # Type the file name
    pyautogui.write(file_name)
    time.sleep(1)

    # Press Enter to select the file
    pyautogui.press("enter")

    print("File selected")

    # Enter text in the search box
    search_box.clear()
    search_box.send_keys(step_1_input)
    search_box.send_keys(Keys.TAB)
    print("Entered search text")
    # search_box.send_keys(Keys.ESCAPE)

    # Wait for a few seconds to allow the file to be processed
    time.sleep(1)

    # Click the go button
    go_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit']"))
    )
    driver.execute_script("arguments[0].click();", go_button)
    print("Clicked go button")

    # Wait for the answer to generate (adjust time as needed)
    time.sleep(20)

    # Attempt to scrape the first answer
    # Wait for the main div to be present
    main_div = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.prose.dark\\:prose-invert")
        )
    )
    # Extract the main text
    all_text = main_div.text

    memo_url = f"http://13.200.242.60:8000/api/cocounsel/{memo['id']}/get_case_ids/"

    data_to_send = {
        "step_1_op": all_text,
    }
    # Prepare the headers for the request
    headers = {
        'Content-Type': 'application/json',
    }
    # Make the PUT request
    response = requests.put(memo_url, json=data_to_send, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    print("DATA INCOMINING:::", response.json())
    print("Successfully updated step1 output")
    
    time.sleep(5)

    # Follow-up query
    follow_up_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/div/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div/div/div/span/div/div/div[1]/textarea",
            )
        )
    )

    time.sleep(2)

    driver.execute_script("arguments[0].scrollIntoView(true);", follow_up_box)
    time.sleep(2)

    follow_up_box.clear()
    follow_up_box.send_keys("Brief Fact + Legal Issue")

    # Find and click the attach button for follow-up
    # try:
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
    # except Exception as e:
    #     print(f"Failed to click attach button: {e}")

    # Wait for the file dialog to appear
    time.sleep(1)

    # File path and name (same as before)
    file_path = r"C:\Users\rithi\Desktop"
    file_name = response.json()

    # Navigate to the directory
    pyautogui.write(file_path)
    pyautogui.press("enter")
    time.sleep(1)  # Wait for directory to open

    # Type the file name
    pyautogui.write(file_name)
    time.sleep(1)

    # Press Enter to select the file
    pyautogui.press("enter")

    print("File selected for follow-up")

    # Wait for the file to be processed
    time.sleep(10)

    # Click the go button for follow-up
    go_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Submit']"))
    )
    driver.execute_script("arguments[0].click();", go_button)
    print("Clicked go button for follow-up")

    # Wait for the second answer to generate
    time.sleep(20)

    # Click on "Convert to Page" button
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

    # Wait for the page to load (400 seconds as requested)
    print("Waiting for page to load...")
    time.sleep(35)

    # List of sections to input
    sections = [
        "Draft Question Presented",
        "Draft Brief Answer",
        "Draft Statement of Facts",
        "Draft Conclusion",
    ]

    # Input each section
    for section in sections:
        input_section(driver, section)

    # Attempt to scrape the content of the converted page
    # try:
    # page_content = WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located(
    #         (
    #             By.XPATH,
    #             "/html/body/div/main/div/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]",
    #         )
    #     )
    # )
    # content_text = page_content.text
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

    # List of sections to input
    sections = [
        "Question Presented",
        "Brief Answer",
        "Statement of Facts",
        "Conclusion",
    ]
    # Step 1: Extract the first 5 dictionaries into "discussion"
    discussion = merged_list[:5]

    remaining = merged_list[5:]
    print("WHat is the ::", remaining)
    for i, section in enumerate(sections):
        if i < len(remaining):
            old_key = list(remaining[i].keys())[0]
            remaining[i] = {section: remaining[i][old_key]}

    # Step 3: Insert the "discussion" list back into the original list at index 3
    remaining.insert(2, {"Discussion": discussion})

    for i in remaining:
        print(i)
        print()

    memo_url = f"http://13.200.242.60:8000/api/cocounsel/{memo["id"]}/"
    memo['citations'] = remaining
    memo['is_completed'] = True
    # Prepare the headers for the request
    headers = {
        'Content-Type': 'application/json',
        # Add any other necessary headers, like authorization tokens
    }
    # Make the PUT request
    # try:
    response = requests.put(memo_url, json=memo, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    print("Successfully updated memo citations")

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


if __name__ == "__main__":
    get_case_url = "http://13.200.242.60:8000/api/cocounsel/get_cocounse_value/"

    while True:
        response = requests.get(get_case_url)
        
        if response.status_code == 200:
            data = response.json()
            step_1_input = f"{data['brief_facts']} {data['legal_issue']}"

            base_path = "/Users/mithilesh/law/step_1_files"
            step_1_folder_path = os.path.join(base_path, data["id"])

            # Create folder
            create_folder(step_1_folder_path)

            # Write files
            write_to_file(
                os.path.join(step_1_folder_path, "case_facts.txt"), data["case_facts"]
            )
            write_to_file(
                os.path.join(step_1_folder_path, "legal_research.txt"), data["legal_research"]
            )

            automated_login_with_profile(data, step_1_input, step_1_folder_path)
            
            print("Processing complete. Immediately polling API again.")
            # The loop will continue immediately to the next iteration
        else:
            print(f"API call failed with status code {response.status_code}. Retrying in 60 seconds.")
            time.sleep(60)  # Wait for 60 seconds before the next attempt