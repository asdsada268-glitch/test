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
  print(f"[{channel}] Status: {res.status_code}")


if __name__ == "__main__":
  # 1. Headers ที่ได้จากการแปลง cURL ในภาพ[cite: 15]
  headers = {
      "accept": "*/*",
      "accept-language": "th-TH,th;q=0.9",
      "origin": "https://www.amarintv.com",
      "priority": "u=1, i",
      "referer": "https://www.amarintv.com/",
      "sec-ch-ua": (
          '"Chromium";v="152", "Not_A_Brand";v="24", "Google Chrome";v="152"'
      ),
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-ch-ua-dest": "empty",
      "sec-ch-ua-mode": "cors",
      "sec-ch-ua-site": "cross-site",
      "user-agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/152.0.0.0 Safari/537.36"
      ),
  }

  # 2. พารามิเตอร์ Token ที่ได้จากการแปลง cURL ในภาพ[cite: 15]
  params = {
      "x_ark_access_id": "fleet-868",
      "x_ark_auth_type": "ark-v2",
      "x_ark_expires": "1789949144",
      "x_ark_path_prefix": "/live/",
      "x_ark_signature": "K3YmEqa1vJiHqJ1vsntGRQ",
  }

  # 3. ยิง Request ไปที่เซิร์ฟเวอร์ ByteArk[cite: 15]
  response = requests.get(
      "https://amarin-ks7jcc.cdn.byteark.com/live/1080p_index.m3u8",
      params=params,
      headers=headers,
  )

  # 4. ดึง URL เต็มๆ ที่รวม params ออกมาอัตโนมัติ
  full_stream_link = response.url
  print(f"Generated Link: {full_stream_link}")

  # 5. บันทึกลง Redis เพื่อให้ Vercel API เรียกใช้งาน
  if response.status_code == 200:
    update_redis("amarin", full_stream_link)
  else:
    print("Failed to fetch stream link from source.")
