import asyncio
import aiohttp
import httpx
import re
from aiohttp_retry import RetryClient, ExponentialRetry
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import argparse
from tqdm.asyncio import tqdm_asyncio

def configure_logging(verbose: bool):
    logging_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Validate URL format
def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'[^ ]+$', re.IGNORECASE
    )
    return re.match(regex, url) is not None

# Check if URL is alive and does NOT contain 'page not found'
async def is_url_alive_and_valid(url, verbose=False):
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            if verbose:
                logging.debug(f"Checking URL: {url}")
            response = await client.get(url)
            if response.status_code == 200:
                content_lower = response.text.lower()
                if "page not found" in content_lower:
                    logging.warning(f"'Page not found' detected in {url}")
                    return False
                return True
            else:
                logging.warning(f"URL returned non-200 status: {url} ({response.status_code})")
    except Exception as e:
        logging.error(f"Error checking URL {url}: {e}")
    return False

# Fetch URL with spoofed headers and retry mechanism
async def fetch_url(session, url, verbose=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        if verbose:
            logging.debug(f"Fetching URL: {url}")
            logging.debug(f"Request Headers: {headers}")

        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if verbose:
                logging.debug(f"Status: {response.status}")
                logging.debug(f"Response Headers: {response.headers}")
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientResponseError as e:
        logging.error(f"Client error for {url}: {e.status}, message='{e.message}', url='{url}'")
    except asyncio.TimeoutError:
        logging.error(f"Timeout while fetching {url}")
    except Exception as e:
        logging.error(f"Unexpected error for {url}: {e}")
    return None

# Parse titles and paragraphs from HTML
async def scrape_data(session, url, verbose=False):
    html = await fetch_url(session, url, verbose)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    try:
        titles = [tag.text.strip() for tag in soup.select("h1, h2, h3")]
        paragraphs = [p.text.strip() for p in soup.find_all("p")]

        if not titles and not paragraphs:
            logging.warning(f"No titles or paragraphs found on {url}")
            return []

        combined_data = []
        max_len = max(len(titles), len(paragraphs))
        for i in range(max_len):
            combined_data.append({
                "url": url,
                "title": titles[i] if i < len(titles) else "",
                "paragraph": paragraphs[i] if i < len(paragraphs) else ""
            })

        return combined_data

    except Exception as e:
        logging.error(f"Parsing error on {url}: {e}")
        return []

# Main coroutine
async def main(urls, filename, verbose=False):
    # Step 1: Validate and filter only alive + valid pages
    valid_urls = []
    logging.info("Checking URLs for validity and page content...")
    for url in urls:
        if is_valid_url(url):
            if await is_url_alive_and_valid(url, verbose):
                valid_urls.append(url)
        else:
            logging.warning(f"Invalid URL skipped: {url}")

    if not valid_urls:
        logging.warning("No valid, alive URLs found. Exiting.")
        return

    retry_options = ExponentialRetry(attempts=3)
    async with RetryClient(raise_for_status=False, retry_options=retry_options) as session:
        tasks = [scrape_data(session, url, verbose) for url in valid_urls]
        all_results = await tqdm_asyncio.gather(*tasks, desc="Scraping Progress")

    flat_data = [item for sublist in all_results if sublist for item in sublist]
    if not flat_data:
        logging.warning("No data scraped from valid URLs.")
        return

    df = pd.DataFrame(flat_data)

    if not filename.endswith(".csv"):
        filename += ".csv"

    try:
        df.to_csv(filename, index=False)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")

# CLI Entry
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async Web Scraper with Page Validation")
    parser.add_argument(
        "-u", "--urls", nargs="+", required=False,
        help="List of URLs to scrape. If not provided, interactive input will be used."
    )
    parser.add_argument(
        "-o", "--output", required=False, default="scraped_data.csv",
        help="Filename to save scraped data (default: scraped_data.csv)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose output for debugging and request inspection"
    )
    args = parser.parse_args()

    configure_logging(args.verbose)

    if args.urls:
        urls = args.urls
    else:
        urls = []
        while True:
            url = input("Enter a URL to scrape (or type 'done' to finish): ").strip()
            if url.lower() == 'done':
                break
            if url.startswith("http"):
                urls.append(url)
            else:
                print("Please enter a valid URL.")

    if not urls:
        print("No URLs provided. Exiting.")
        exit()

    start_time = time.time()
    asyncio.run(main(urls, args.output, args.verbose))
    end_time = time.time()
    logging.info(f"Total scraping time: {end_time - start_time:.2f} seconds")
