import os
from dotenv import load_dotenv
from playwright.sync_api import Page

DEFAULT_TIMEOUT = 2000


def login(page: Page) -> None:
    """
    Logs into Instagram
    Ensure that the INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables are set inside of a .env file or in the environment
    """
    page.goto("https://www.instagram.com/")
    page.wait_for_timeout(DEFAULT_TIMEOUT)

    page.get_by_label("Phone number, username, or").click()
    page.get_by_label("Phone number, username, or").fill(os.environ["INSTAGRAM_USERNAME"])
    page.wait_for_timeout(DEFAULT_TIMEOUT)

    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(os.environ["INSTAGRAM_PASSWORD"])
    page.get_by_role("button", name="Log in", exact=True).click()
    page.wait_for_timeout(DEFAULT_TIMEOUT)


def unfollow_cycle(page: Page, iterations=10) -> None:
    """
    Unfollows the first person in the "Following" list for the specified number of iterations
    """
    visit_profile(page)
    following_link(page)

    for i in range(iterations):
        # get the first button with the text "Following" and click it
        page.get_by_role("button", name="Following", exact=True).first.click()
        page.wait_for_timeout(DEFAULT_TIMEOUT)

        # click the "Unfollow" button
        page.get_by_role("button", name="Unfollow", exact=True).first.click()
        page.wait_for_timeout(DEFAULT_TIMEOUT * 5)

        # go back to home page
        page.goto("https://www.instagram.com/")
        page.wait_for_timeout(DEFAULT_TIMEOUT)

        # go to the profile
        page.goto(f"https://www.instagram.com/{os.environ['INSTAGRAM_USERNAME']}/")
        page.wait_for_timeout(DEFAULT_TIMEOUT)

        # click the "Following" link
        page.get_by_text("Following").click()
        page.wait_for_timeout(DEFAULT_TIMEOUT)


def following_link(page: Page) -> None:
    # click the "Following" link
    page.get_by_text("Following").click()
    page.wait_for_timeout(DEFAULT_TIMEOUT)


def not_now(page: Page) -> None:
    """
    Clicks the "Not Now" button incase it appears
    """
    if page.query_selector("button:has-text('Not Now')"):
        page.get_by_text("Not Now").click()
        page.wait_for_timeout(DEFAULT_TIMEOUT)


def visit_profile(page: Page) -> None:
    """
    Visits the profile of the user
    """
    page.goto(f"https://www.instagram.com/{os.environ['INSTAGRAM_USERNAME']}/")
    page.wait_for_timeout(DEFAULT_TIMEOUT)


def whoami(page: Page) -> None:
    """
    checks if the user is logged in,
    if not logs in
    """
    if page.query_selector("button:has-text('Log In')"):
        login(page)
    else:
        visit_profile(page)


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    load_dotenv()

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="instagram_unfollower",
            headless=False,
        )
        page = browser.new_page()
        whoami(page)
        not_now(page)
        unfollow_cycle(page, 10)
        browser.close()
