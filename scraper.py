import os, requests

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
HEADERS = {"Authorization": f"Bearer {UPSTASH_TOKEN}", "Content-Type": "application/json"}

def update_channel(channel, link):
    res = requests.post(f"{UPSTASH_URL}/set/{channel}", headers=HEADERS, data=link)
    print(f"[{channel}] Status: {res.status_code}")

if __name__ == "__main__":
    # จำลองการดึงลิงก์ (แทนที่ด้วยโค้ดดึงข้อมูลจริงของคุณ)
    m3u8_link = "https://true4u-p41jv2.cdn.byteark.com/live/.../index.m3u8?token=123"
    update_channel("true4u", m3u8_link)
