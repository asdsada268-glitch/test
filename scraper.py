import cloudscraper
import re
import os
import requests

# ดึงค่าเชื่อมต่อ Redis จาก GitHub Secrets
UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

def update_redis(link):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        print("❌ Redis credentials not found!")
        return
    
    endpoint = f"{UPSTASH_URL}/set/amarin"
    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
    }
    
    # ส่งลิงก์ตรงเข้า Upstash Redis
    res = requests.post(endpoint, headers=headers, data=link)
    print(f"Redis Status: {res.status_code} - {res.text}")

def get_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.amarintv.com/",
    }

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    try:
        response = scraper.get("https://www.amarintv.com/live", headers=headers)

        if response.status_code == 200:
            match = re.search(r'"(https[^"]+\.m3u8[^"]*)"', response.text)
            if match:
                raw_url = match.group(1)

                # ทำความสะอาดลิงก์
                clean_raw = raw_url.rstrip('\\')
                final_url = clean_raw.encode().decode('unicode_escape')
                final_url = final_url.replace('\\', '')
                final_url = final_url.strip()

                # บันทึกลง Redis แทนการเขียนไฟล์
                update_redis(final_url)
                print(f"✅ Success! URL saved to Redis: {final_url}")
            else:
                print("❌ No M3U8 found.")
        else:
            print(f"❌ Status: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    get_data()
