import cloudscraper
import re
import os
import requests
import random
import time

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

# รายชื่อ User-Agent หลากหลายรูปแบบเพื่อลดการถูกบล็อก
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

def update_redis(channel, link):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        print("❌ Redis credentials not found!")
        return
    
    endpoint = f"{UPSTASH_URL}/set/{channel}"
    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
    }
    res = requests.post(endpoint, headers=headers, data=link)
    print(f"Redis Status [{channel}]: {res.status_code}")

def scrape_channel(name, target_url, referer):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": referer,
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1"
    }

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    try:
        # หน่วงเวลาสุ่ม 1-3 วินาที เพื่อลดการถูกมองว่าเป็น Bot ถี่เกินไป
        time.sleep(random.uniform(1.0, 3.0))
        
        response = scraper.get(target_url, headers=headers, timeout=15)

        if response.status_code == 200:
            match = re.search(r'"(https[^"]+\.m3u8[^"]*)"', response.text)
            if match:
                raw_url = match.group(1)
                clean_raw = raw_url.rstrip('\\')
                final_url = clean_raw.encode().decode('unicode_escape')
                final_url = final_url.replace('\\', '').strip()

                update_redis(name, final_url)
                print(f"✅ Success! [{name}] URL saved: {final_url}")
            else:
                print(f"❌ No M3U8 found for {name}.")
        else:
            print(f"❌ Status [{name}]: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Error [{name}]: {e}")

if __name__ == "__main__":
    channels = [
        ("amarin", "https://www.amarintv.com/live", "https://www.amarintv.com/"),
        ("thairath", "https://www.thairath.co.th/tv/live", "https://www.thairath.co.th/"),
        ("true4u", "https://true4u.com/live", "https://true4u.com/"),
        ("ch7", "https://www.ch7.com/live", "https://www.ch7.com/"),
        ("ch3", "https://ch3plus.com/live", "https://ch3plus.com/"),
        ("tv5", "https://thaitv5hd.com/live/", "https://thaitv5hd.com/"),
        ("thaich8", "https://www.thaich8.com/live", "https://www.thaich8.com/"),
        ("one31", "https://oned.net/live-tv/one31", "https://oned.net/"),
        ("gmm25", "https://oned.net/live-tv/gmm25", "https://oned.net/"),
        ("mcot", "https://www.mcot.net/live", "https://www.mcot.net/"),
        ("pptv", "https://www.pptvhd36.com/live", "https://www.pptvhd36.com/"),
        ("thaipbs", "https://www.thaipbs.or.th/live", "https://www.thaipbs.or.th/"),
        ("tpchannel", "https://www.tpchannel.org/broadcasts/tv", "https://www.tpchannel.org/"),
        ("workpoint", "https://workpointtv.com/live-stream-page", "https://workpointtv.com/"),
        ("nationtv", "https://www.nationtv.tv/live", "https://www.nationtv.tv/"),
        ("tnn", "https://www.tnnthailand.com/live/", "https://www.tnnthailand.com/")
    ]

    for name, url, ref in channels:
        scrape_channel(name, url, ref)
