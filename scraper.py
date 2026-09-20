import os
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

if __name__ == "__main__":
    print("Starting Scraper for Amarin TV (1080p)...")

    # พารามิเตอร์ Token ชุดที่เปิดดูผ่านเว็บได้จริง
    params = {
        "x_ark_access_id": "fleet-868",
        "x_ark_auth_type": "ark-v2",
        "x_ark_expires": "1789949144",
        "x_ark_path_prefix": "/live/",
        "x_ark_signature": "K3YmEqa1vJiHqJ1vsntGRQ",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.amarintv.com/"
    }

    # เจาะจงดึงไฟล์ความละเอียด 1080p โดยตรงเพื่อให้เล่นบนเว็บได้ทันที
    response = requests.get(
        "https://amarin-ks7jcc.cdn.byteark.com/live/1080p_index.m3u8",
        params=params,
        headers=headers
    )

    if response.status_code == 200:
        full_stream_link = response.url
        print(f"Generated Link: {full_stream_link}")
        update_redis("amarin", full_stream_link)
    else:
        print(f"Failed to fetch stream, status code: {response.status_code}")
