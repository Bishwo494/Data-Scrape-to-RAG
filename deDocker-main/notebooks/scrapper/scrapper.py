import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from io import BytesIO
from botocore.exceptions import ClientError


INDEX_URL = "https://www.gutenberg.org/ebooks/search/?sort_order=downloads"
BASE_URL = "https://www.gutenberg.org"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_books():  
    def get_all_book_links(pages_to_scan=50):
        book_links = set()
        for page in range(1, pages_to_scan + 1):
            print(f"Fetching index page {page}...")
            try:
                resp = requests.get(f"{INDEX_URL}&start_index={(page - 1) * 25 + 1}", headers=headers, timeout=10)
                if resp.status_code != 200:
                    print(f"Failed to fetch index page {page}")
                    continue

                soup = BeautifulSoup(resp.content, 'html.parser')
                for link in soup.select('.booklink a.link'):
                    href = link.get('href')
                    if href and href.startswith("/ebooks/"):
                        book_links.add(urljoin(BASE_URL, href))
            except Exception as e:
                print(f"Error on index page {page}: {e}")
            time.sleep(0.3)  # Small polite delay

        print(f" Collected {len(book_links)} book links from {pages_to_scan} pages.\n")
        return list(book_links)

    def scrape_book_metadata(book_url):
        try:
            print(f"Scraping {book_url}")
            response = requests.get(book_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch {book_url}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            title_element = soup.find('h1')
            title = title_element.get_text(strip=True) if title_element else "Unknown"

            about_ebook = {}
            table = soup.find('table', class_='bibrec')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    key = row.find('th')
                    value = row.find('td')
                    if key and value:
                        key_text = key.get_text(strip=True).replace(':', '')
                        value_text = value.get_text(strip=True)
                        about_ebook[key_text] = value_text

            downloads = {}
            for link in soup.select('a.link'):
                file_type = link.get('type')
                if file_type and 'text' in file_type:
                    href = link.get('href')
                    if href:
                        downloads[file_type] = urljoin(book_url, href)

            return {
                "url": book_url,
                "title": title,
                "about_ebook": about_ebook,
                "download_links": downloads
            }

        except Exception as e:
            print(f"Error while scraping {book_url}: {e}")
            return None

    # Step 1: Get all book links from 50 pages
    book_urls = get_all_book_links(pages_to_scan=2)

    # Step 2: Scrape metadata concurrently
    ebooks_metadata = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_book_metadata, url): url for url in book_urls}
        for future in as_completed(future_to_url):
            data = future.result()
            if data:
                ebooks_metadata.append(data)

    # # Step 3: Save to JSON
    # output_file = "random_ebooks_metadata.json"
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(ebooks_metadata, f, indent=4, ensure_ascii=False)

    # print(f"\n Scraped metadata for {len(ebooks_metadata)} books.")
    # print(f"Saved to {output_file}")


    minio_endpoint = "http://minio:9000"  # or your MinIO host
    access_key = "admin"
    secret_key = "password"
    bucket_name = "ebooks"
    object_key = "random_ebooks_metadata.json"

    s3_client = boto3.client(
    's3',
    endpoint_url=minio_endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
    )

    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)

    
    # Convert your metadata to JSON and encode it
    json_bytes = json.dumps(ebooks_metadata, indent=4, ensure_ascii=False).encode('utf-8')
    json_buffer = BytesIO(json_bytes)

    # Upload to MinIO
    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=json_buffer, ContentType='application/json')

    print(f"\n Uploaded metadata for {len(ebooks_metadata)} books to MinIO bucket '{bucket_name}' as '{object_key}'")

scrape_books()