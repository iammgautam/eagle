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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python perplexity_scraper.py <url> <case_id>")
        sys.exit(1)
    
    url = sys.argv[1]
    case_id = sys.argv[2]
    result = perplexity_scrape(url)

    output = {
        "id": case_id,
        "scrape_link": url,
        "citations": result
    }

    api_url = f"http://13.200.242.60:8000/api/cocounsel/{case_id}/"
    
    try:
        response = requests.put(api_url, json=output)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print(f"Successfully updated API for case ID: {case_id}")
        print(f"API Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating API: {e}")
