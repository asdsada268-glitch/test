import os
import requests
from playwright.sync_api import sync_playwright

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

def scrape_channel(playwright, name, target_url):
    # เปิดเบราว์เซอร์จำลองแบบไร้หน้าจอ (Headless)
    browser = playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
    
    found_url = None

    # ดักจับ Network Request ทั้งหมดที่วิ่งผ่านหน้าเว็บเพื่อหาไฟล์ .m3u8
    def handle_request(request):
        nonlocal found_url
        if ".m3u8" in request.url and not found_url:
            found_url = request.url

    page.on("request", handle_request)

    try:
        print(f"🔍 Loading [{name}] -> {target_url}")
        # เข้าเว็บไซต์และรอให้โหลดสตรีมมิ่งเสร็จสิ้น
        page.goto(target_url, timeout=40000, wait_until="networkidle")
        # หน่วงเวลาเผื่อให้เครื่องเล่นวิดีโอ (Player) เริ่มเล่นและยิง Request สตรีม
        page.wait_for_timeout(6000)
    except Exception as e:
        print(f"⚠️ Error loading [{name}]: {e}")

    browser.close()

    if found_url:
        update_redis(name, found_url)
        print(f"✅ Success! [{name}] URL saved: {found_url}")
    else:
        print(f"❌ No M3U8 found for {name}.")

if __name__ == "__main__":
    channels = [
        ("amarin", "https://www.amarintv.com/live"),
        ("thairath", "https://www.thairath.co.th/tv/live"),
        ("true4u", "https://true4u.com/live"),
        ("ch7", "https://www.ch7.com/live"),
        ("ch3", "https://ch3plus.com/live"),
        ("tv5", "https://thaitv5hd.com/live/"),
        ("thaich8", "https://www.thaich8.com/live"),
        ("one31", "https://oned.net/live-tv/one31"),
        ("gmm25", "https://oned.net/live-tv/gmm25"),
        ("mcot", "https://www.mcot.net/live"),
        ("pptv", "https://www.pptvhd36.com/live"),
        ("thaipbs", "https://www.thaipbs.or.th/live"),
        ("tpchannel", "https://www.tpchannel.org/broadcasts/tv"),
        ("workpoint", "https://workpointtv.com/live-stream-page"),
        ("nationtv", "https://www.nationtv.tv/live"),
        ("tnn", "https://www.tnnthailand.com/live/")
    ]

    with sync_playwright() as p:
        for name, url in channels:
            scrape_channel(p, name, url)
