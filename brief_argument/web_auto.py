from playwright.sync_api import sync_playwright
import imaplib
import email
from email.header import decode_header
import re

def get_otp():
    # Connect to the email server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login("iammgautam@gmail.com", "uzfi oqwy ixwx ffiv")
    mail.select("inbox")

    # Search for all emails in the inbox
    status, messages = mail.search(None, "ALL")
    messages = messages[0].split()

    for msg_num in reversed(messages):
        status, msg_data = mail.fetch(msg_num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header(msg["subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                    print("SUBJECTS::", subject)
                if "Secure link to log in to Claude.ai" in subject:
                    print("WHat is the message::", msg)  # Adjust based on your email subject
                    # if msg.is_multipart():
                    #     for part in msg.walk():
                    #         if part.get_content_type() == "text/plain":
                    #             otp = re.search(r"\b\d{6}\b", part.get_payload(decode=True).decode()).group()
                    #             return otp
                    # else:
                    #     otp = re.search(r"\b\d{6}\b", msg.get_payload(decode=True)).group()
                    #     return otp

    return None


def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://claude.ai")

    # Perform login steps
    page.get_by_placeholder("name@yourcompany.com").fill("iammgautam@gmail.com")
    page.get_by_text("Continue with email").click()
    page.get_by_text("Continue with email").click()
    # page.click("button[type='submit']")

    # Wait for OTP input and retrieve OTP
    otp_input = page.wait_for_selector("input[name='otp']")
    if otp_input:
        otp = get_otp()
        if otp:
            page.fill("input[name='otp']", otp)
            page.click("button[type='submit']")
    
    # Proceed with the rest of your automation script
    # Example:
    page.click("#claudeIcon")  # Example ID selector

    # (rest of your script...)

    # Close the browser
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
