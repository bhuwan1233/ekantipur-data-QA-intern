from playwright.sync_api import sync_playwright
import json

BASE_URL = "https://ekantipur.com"
ENTERTAINMENT_URL = f"{BASE_URL}/entertainment"
CARTOON_URL = f"{BASE_URL}/cartoon"
# extract only 5 entwertainment articles
ARTICLE_LIMIT = 5   
OUTPUT_FILE = "output.json"


def safe_text(element):
    """Get inner text from element or None if missing."""
    if element:
        try:
            return element.inner_text().strip()
        except Exception:
            return None
    return None


def safe_attr(element, attr):
    """Get attribute from element or None if missing."""
    if element:
        try:
            return element.get_attribute(attr)
        except Exception:
            return None
    return None


def scrape_entertainment(page):
    """Scrape entertainment news articles."""
    page.goto(ENTERTAINMENT_URL, wait_until="domcontentloaded")
    articles = page.query_selector_all("article.normal")[:ARTICLE_LIMIT]
    results = []

    for article in articles:
        # locate elements relative to each articles card
        title_el = article.query_selector("h2")
        author_el = article.query_selector(".author")
        img_el = article.query_selector(".image img")

        title = safe_text(title_el)
        author = safe_text(author_el)
        image_url = safe_attr(img_el, "src")

        results.append({
            "title": title,
            "image_url": image_url,
            "category": "मनोरञ्जन",
            "author": author,
        })

    return results


def scrape_cartoon(page):
    """Scrape cartoon of the day."""
    page.goto(CARTOON_URL, wait_until="domcontentloaded")
    # wait up to 30 seconds for cartoon image
    page.wait_for_selector(
        "section.cartoon-wrapper figure.popup-image img",
        timeout=30000,
    )

    wrapper = page.query_selector("section.cartoon-wrapper")
    if not wrapper:
        return None

    img_el = wrapper.query_selector("figure.popup-image img")
    thumbnail_url = safe_attr(img_el, "src")
    title = safe_attr(img_el, "alt")

    # Convert thumbnail URL -> direct image URL if needed
    image_url = thumbnail_url
    if thumbnail_url and "src=" in thumbnail_url:
        image_url = thumbnail_url.split("src=")[1].split("&")[0]

    author_el = wrapper.query_selector(".cartoon-author")
    author = safe_text(author_el)

    return {
        "title": title,
        "image_url": image_url,
        "author": author,
    }


def main(headless=False):
    data = {"entertainment_news": [], "cartoon_of_the_day": None}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            data["entertainment_news"] = scrape_entertainment(page)
            data["cartoon_of_the_day"] = scrape_cartoon(page)
        finally:
            browser.close()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(data['entertainment_news'])} articles and cartoon to {OUTPUT_FILE}")


if __name__ == "__main__":
    main(headless=False)
