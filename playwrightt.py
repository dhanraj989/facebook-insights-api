from playwright.sync_api import sync_playwright

def test_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Use False to debug visually
        page = browser.new_page()
        page.goto("https://www.facebook.com/boat.lifestyle", timeout=60000)

        # Wait for the entire page to load
        page.wait_for_load_state("networkidle")

        # Try multiple selectors to get profile pic
        profile_pic = None

        try:
            # First, check the SVG <image> tag
            page.wait_for_selector("g image", timeout=10000)
            profile_pic = page.locator("g image").get_attribute("xlink:href")
        except:
            pass

        if not profile_pic:
            try:
                # Try extracting image from meta tag (if available)
                profile_pic = page.locator("meta[property='og:image']").get_attribute("content")
            except:
                pass

        if not profile_pic:
            try:
                # Try another selector
                profile_pic = page.locator("img[alt*='profile']").get_attribute("src")
            except:
                pass

        if not profile_pic:
            profile_pic = "Profile pic not found"

        page_name = page.title()

        browser.close()

        print("Page Name:", page_name)
        print("Profile Pic:", profile_pic)

test_scraper()