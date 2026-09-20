import os
import re
import requests
import html

# ดึงค่าเชื่อมต่อ Redis จาก GitHub Secrets
UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

def update_redis(channel, link):
    """ฟังก์ชันส่งลิงก์สตรีมมิ่งไปเก็บไว้ในฐานข้อมูล Redis"""
    endpoint = f"{UPSTASH_URL}/set/{channel}"
    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
        "Content-Type": "application/json",
    }
    res = requests.post(endpoint, headers=headers, data=link)
    print(f"[{channel}] Redis Status: {res.status_code}")

if __name__ == "__main__":
    print("Starting Automated Scraper for Amarin TV (1080p)...")
    
    target_url = "https://www.amarintv.com/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.amarintv.com/"
    }

    try:
        print(f"Fetching target web: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=15)

        if response.status_code == 200:
            # ค้นหาเฉพาะลิงก์ 1080p_index.m3u8 ที่มี Token สดๆ จากหน้าเว็บ
            pattern = r'(https://[^\s\'"]+?1080p_index\.m3u8\?[^\s\'"]*)'
            matches = re.findall(pattern, response.text)

            if matches:
                raw_link = matches[0]
                # ทำความสะอาดลิงก์แปลงรหัสตัวอักษรพิเศษ
                clean_link = html.unescape(raw_link).replace(r"\u0026", "&")
                
                print(f"Successfully fetched fresh live link: {clean_link}")
                
                # ส่งเข้า Redis ทันที
                update_redis("amarin", clean_link)
            else:
                print("Error: 1080p live link not found in HTML content.")
        else:
            print(f"Failed to fetch website, status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error while scraping: {e}")
