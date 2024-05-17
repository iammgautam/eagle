import asyncio
from playwright.async_api import async_playwright
import random
import re

async def extract_6_digit_code(new_page):
    try:
        await new_page.wait_for_selector('#MailList .Cz7T5 .FiPRo .EeHm8 .jGG6V.gDC9O', state='visible')
        email_element = await new_page.query_selector('#MailList .Cz7T5 .FiPRo .EeHm8 .jGG6V.gDC9O')
        if email_element:
            aria_label = await email_element.get_attribute('aria-label')
            if aria_label:
                match = re.search(r'\b\d{6}\b', aria_label)
                return match.group() if match else None
    except Exception as e:
        print(f"Error extracting code: {e}")
    return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1080, 'height': 3080})

        # Open the original tab
        original_page = await context.new_page()
        await original_page.goto("https://claude.ai/chats", timeout=120000, wait_until="networkidle")
        await original_page.click("#email")
        await original_page.fill("#email", "jishnu.shopping@outlook.com")
        await original_page.click("[type='submit']")

        # Open new tab and handle email login and code retrieval
        new_page = await context.new_page()
        await new_page.goto('https://www.microsoft.com/en-us/microsoft-365/outlook/log-in')
        await new_page.click('.btn.btn-outline-primary-white')

        # Switch to the new tab
        new_page = await context.wait_for_event('page')
        
        # Enter email
        await new_page.fill('#i0116', 'jishnu.shopping@outlook.com')
        await new_page.click('#idSIButton9')

        # Wait for 10 seconds
        await new_page.wait_for_timeout(10000)

        await new_page.fill('#i0118', '%u23!pU59bvR#')
        await new_page.click('#idSIButton9')
        await new_page.click('#acceptButton')

        # Extract 6 digit code from the email
        code = await extract_6_digit_code(new_page)
        if code:
            print(code)
        else:
            print("Unable to extract 6 digit code from the email.")

        # Close the new tab
        await new_page.close()

        # Switch back to the original page
        await original_page.bring_to_front()  # Make sure the original page is active

        # Use the code in the original context
        if code:
            await original_page.fill('#code', code)
            await original_page.click('[data-testid="continue"][type="submit"]')

        # Continue with original page interactions
        await original_page.fill("[contenteditable='true']", "what is browser automation? List down the best browser automation tools")
        await original_page.press("[contenteditable='true']", "Enter")
        await asyncio.sleep(60)

        # Scroll down in case the response is not visible
        await original_page.evaluate("window.scrollBy(0, 1000);")

        # Handle responses from chat more dynamically and robustly
        responses_locator = original_page.locator("div[data-is-streaming='false']")
        responses_count = await responses_locator.count()
        
        for i in range(responses_count):
            response_text = await responses_locator.nth(i).inner_text()
            print(f"Response {i+1}: {response_text}")

       # New interaction: Reply to Claude
        await original_page.click("[contenteditable='true']")
        await original_page.fill("[contenteditable='true']", "which is the best")
        send_button = original_page.locator('button[aria-label="Send Message"]')
        await send_button.click()
        await asyncio.sleep(60)

        # Retrieve the response
        await original_page.evaluate("window.scrollBy(0, 2000);")  # Scroll again if necessary
        response_element = original_page.locator("div[data-is-streaming='false']").last  # Assuming the latest message appears last
        response_text_content = await response_element.inner_text()
        print("Second Response:", response_text_content)


        # New interaction: 3
        # New interaction
        await original_page.click("[contenteditable='true']")
        await original_page.fill("[contenteditable='true']", "which is suitable for chat interface?")
        await asyncio.sleep(1)  # Let the page settle if needed

        send_button = original_page.locator('button[aria-label="Send Message"]')
        await send_button.wait_for(state="visible")
        try:
            await send_button.click()
        except Exception as e:
            print("Normal click failed, attempting JavaScript click")
            await original_page.evaluate("element => element.click()", send_button)

        await asyncio.sleep(60)  # Wait for the response to be fully loaded

        # Scroll if needed and retrieve the response
        await original_page.evaluate("window.scrollBy(0, 1000);")
        response_element = original_page.locator("div[data-is-streaming='false']").last  # Use 'last' to get the latest message
        response_text_content = await response_element.inner_text()
        print("Response:", response_text_content)

        
        # New interaction: 4
        await original_page.click("[contenteditable='true']")
        await original_page.fill("[contenteditable='true']", "which one would you choose?")
        send_button = original_page.locator('button[aria-label="Send Message"]')
        await send_button.click()
        await asyncio.sleep(60)

        # Retrieve the response 4
        await original_page.evaluate("window.scrollBy(0, 2000);")  # Scroll again if necessary
        response_element = original_page.locator("div[data-is-streaming='false']").last  # Assuming the latest message appears last
        response_text_content = await response_element.inner_text()
        print("Fourth Response:", response_text_content)

        print("Browser will remain open. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
