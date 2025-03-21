```markdown
# 🔎 Async Web Scraper with URL Validation & Page Filtering

This project is a **robust, asynchronous web scraping tool** built in Python. It verifies URLs, checks if the content is alive and valid (excluding pages with `"Page not found"`), and scrapes headlines and paragraphs from structured websites.

The scraper uses:
- `asyncio` + `aiohttp` for non-blocking scraping
- `httpx` for fast URL health checks
- `BeautifulSoup` for HTML parsing
- `tqdm` for async progress bars
- `pandas` for saving structured data as CSV

---

## 🚀 Features

- ✅ Asynchronous scraping (fast and efficient)
- ✅ URL format validation using regex
- ✅ Alive URL check using `httpx`
- ✅ Skips pages containing "page not found"
- ✅ Scrapes `<h1>`, `<h2>`, `<h3>`, and `<p>` tags
- ✅ Saves clean and structured data to CSV
- ✅ Verbose debug mode (`--verbose`)

---

## 📦 Requirements

Install all required Python packages:

```bash
pip install aiohttp aiohttp_retry httpx beautifulsoup4 lxml pandas tqdm
```

---

## 🛠 Usage

### 💡 Basic CLI Command:

```bash
python3 scrapper.py -u <url1> <url2> ... -o <output_filename.csv>
```

### 🐾 Example:

```bash
python3 scrapper.py -u https://example.com -o output.csv
```

### 🐛 With Verbose Debug Logs:

```bash
python3 scrapper.py -u https://exampl.com -o output.csv --verbose
```

---

## ✨ Features Explained

| Feature                    | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `--urls` or `-u`          | One or more URLs to scrape                                                  |
| `--output` or `-o`        | Output CSV filename (default: `scraped_data.csv`)                           |
| `--verbose` or `-v`       | Enable verbose output with detailed logs and header info                    |
| URL Validation            | Regex-based filtering for `http`/`https` formatted URLs                     |
| Live Page Check           | Uses `httpx` to send a GET request and skips any with "page not found" text |
| Async Scraping            | Uses `aiohttp` with retry and `tqdm` async progress bar                     |

---

## 📁 Output Format (CSV)

| url                          | title               | paragraph                                |
|-----------------------------|---------------------|-------------------------------------------|
| https://example.com/page1   | page1 News Headline | The European Union announced...           |
| https://example.com/page1   |                     | Lorem ipsum dolor sit amet...             |

Each row includes:
- URL of the source
- Title (if available)
- Corresponding paragraph (if available)

---

## 🧠 How It Works

1. Takes a list of URLs via CLI or interactive input.
2. Validates URL structure using regex.
3. Sends `GET` requests using `httpx` to check if:
   - Page is alive (200 OK)
   - Content doesn't include "page not found"
4. Only valid pages are scraped asynchronously.
5. Extracted `<h1>`, `<h2>`, `<h3>`, and `<p>` tags.
6. Results are flattened and saved to CSV using `pandas`.

---

