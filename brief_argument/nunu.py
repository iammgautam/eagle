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
        context = await browser.new_context(viewport={'width': 1080, 'height': 1080})

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
        
        div_element = original_page.locator("div[data-is-streaming='false']")
        div_text_content = await div_element.inner_text()
        print("First response:", div_text_content)

        # New interaction: Reply to Claude
        reply_selector = "p[data-placeholder='Reply to Claude...']"
        await original_page.click(reply_selector)
        await original_page.fill(reply_selector, "which is the best")
        await original_page.press(reply_selector, "Enter")
        await asyncio.sleep(60)

        # Retrieve the response
        response_element = original_page.locator("div[data-is-streaming='false']:last-child")  # Assuming the latest message appears last
        response_text_content = await response_element.inner_text()
        print("Second Response:", response_text_content)

        print("Browser will remain open. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
