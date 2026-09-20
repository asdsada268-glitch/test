import cloudscraper
import re
import os
import requests

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": referer,
    }

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    try:
        response = scraper.get(target_url, headers=headers)

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
    # ดึงข้อมูลทั้งหมดรวมถึง TNN แบบอัตโนมัติ
    scrape_channel("amarin", "https://www.amarintv.com/live", "https://www.amarintv.com/")
    scrape_channel("thairath", "https://www.thairath.co.th/tv/live", "https://www.thairath.co.th/")
    scrape_channel("true4u", "https://true4u.com/live", "https://true4u.com/")
    scrape_channel("ch7", "https://www.ch7.com/live", "https://www.ch7.com/")
    scrape_channel("ch3", "https://ch3plus.com/live", "https://ch3plus.com/")
    scrape_channel("tv5", "https://thaitv5hd.com/live/", "https://thaitv5hd.com/")
    scrape_channel("thaich8", "https://www.thaich8.com/live", "https://www.thaich8.com/")
    scrape_channel("one31", "https://oned.net/live-tv/one31", "https://oned.net/")
    scrape_channel("gmm25", "https://oned.net/live-tv/gmm25", "https://oned.net/")
    scrape_channel("mcot", "https://www.mcot.net/live", "https://www.mcot.net/")
    scrape_channel("pptv", "https://www.pptvhd36.com/live", "https://www.pptvhd36.com/")
    scrape_channel("thaipbs", "https://www.thaipbs.or.th/live", "https://www.thaipbs.or.th/")
    scrape_channel("tpchannel", "https://www.tpchannel.org/broadcasts/tv", "https://www.tpchannel.org/")
    scrape_channel("workpoint", "https://workpointtv.com/live-stream-page", "https://workpointtv.com/")
    scrape_channel("nationtv", "https://www.nationtv.tv/live", "https://www.nationtv.tv/")
    scrape_channel("tnn", "https://www.tnnthailand.com/live/", "https://www.tnnthailand.com/")
