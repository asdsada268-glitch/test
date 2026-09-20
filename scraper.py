import os
import re
import requests

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


def get_amarin_live_link():
    """ฟังก์ชันดึงลิงก์สดของ Amarin TV แบบไดนามิกจากหน้าเว็บหลัก"""
    target_url = "https://www.amarintv.com/live"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.amarintv.com/",
    }

    try:
        print(f"Fetching target web: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=15)

        if response.status_code == 200:
            # ใช้ Regular Expression ค้นหาลิงก์ .m3u8 ที่มีพารามิเตอร์ token ของ ByteArk จากหน้าเว็บ
            pattern = r'(https://[^\s\'"]+?\.m3u8\?[^\s\'"]*)'
            matches = re.findall(pattern, response.text)

            if matches:
                # กรองเอาลิงก์สตรีมตัวแรกที่พบ
                live_link = matches[0]
                print(f"Found dynamic live link: {live_link}")
                return live_link
            else:
                print("No m3u8 link found in HTML content.")
        else:
            print(f"Failed to fetch website, status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error while scraping: {e}")

    return None


if __name__ == "__main__":
    print("Starting Dynamic Scraper for Amarin TV...")

    # 1. ดึงลิงก์สดแบบไดนามิกจากหน้าเว็บ
    stream_link = get_amarin_live_link()

    # 2. บันทึกลง Redis ถ้าพบลิงก์ที่ถูกต้อง
    if stream_link:
        update_redis("amarin", stream_link)
    else:
        print("Could not retrieve a valid live stream link.")
