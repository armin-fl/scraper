# Configuration
SERPAPI_KEY = ""  # Replace with your SerpApi key
import asyncio
import json
import csv
from playwright.async_api import async_playwright
import requests

SERPAPI_KEY = "0747b5546ece61f28e29ebb85039c1971810f9496823729177414d18e5d58221"  # Replace with your SerpApi key

async def extract_headings(url, playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    try:
        await page.goto(url, timeout=30000, wait_until="load")
        headings = await page.evaluate("""
        () => {
            const hs = document.querySelectorAll('h1, h2, h3');
            return Array.from(hs).map(h => ({ tag: h.tagName, text: h.innerText.trim() }));
        }
        """)
        return headings
    except Exception as e:
        print(f"Error extracting headings from {url}: {e}")
        return []
    finally:
        await context.close()
        await browser.close()

def fetch_serp_results(query, hl, gl, num=20):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": query,
        "hl": hl,
        "gl": gl,
        "google_domain": "google.com",  # Use a supported domain
        "num": num,
        "api_key": SERPAPI_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    results = data.get("organic_results", [])
    urls = [res["link"] for res in results if "link" in res]

    return urls[:num]

async def main():
    query = input("Enter your keyword: ")
    hl = input("Enter language code (e.g. 'en'): ")
    gl = input("Enter region code (e.g. 'us'): ")

    urls = fetch_serp_results(query, hl, gl, num=20)

    async with async_playwright() as p:
        all_data = []
        for url in urls:
            print(f"Extracting headings from: {url}")
            headings = await extract_headings(url, p)
            all_data.append({
                "url": url,
                "headings": headings
            })

    # Sort the results by URL alphabetically
    all_data.sort(key=lambda x: x['url'])

    # Write to CSV
    # CSV format: url, tag, heading_text
    output_filename = "headings_results.csv"
    with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["url", "tag", "heading_text"])

        for item in all_data:
            url = item["url"]
            headings = item["headings"]
            for h in headings:
                writer.writerow([url, h["tag"], h["text"]])

    print(f"Saved headings to {output_filename}")

if __name__ == "__main__":
    asyncio.run(main())
