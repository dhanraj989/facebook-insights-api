import sys
import json
from playwright.sync_api import sync_playwright

def run_scraper(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.facebook.com/{username}", timeout=60000)

        # Wait for full page load
        page.wait_for_load_state("networkidle")

        # Extract profile pic
        profile_pic = None
        try:
            page.wait_for_selector("g image", timeout=10000)
            profile_pic = page.locator("g image").get_attribute("xlink:href")
        except:
            pass

        if not profile_pic:
            try:
                profile_pic = page.locator("meta[property='og:image']").get_attribute("content")
            except:
                pass

        if not profile_pic:
            try:
                profile_pic = page.locator("img[alt*='profile']").get_attribute("src")
            except:
                pass

        if not profile_pic:
            profile_pic = "Profile pic not found"

        page_name = page.title()
        browser.close()

        print(json.dumps({
            "username": username,
            "page_name": page_name,
            "profile_pic": profile_pic
        }))

if __name__ == "__main__":
    username = sys.argv[1]
    run_scraper(username)