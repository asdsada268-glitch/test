import os
import re
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
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox", 
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--autoplay-policy=no-user-gesture-required",
            "--mute-audio",
            "--disable-web-security" # [NEW] ปิดระบบความปลอดภัยเพื่อเจาะทะลุ Iframe ข้ามโดเมน
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
    
    # [FIX] เอา "media" ออกจากการบล็อก เพื่อให้ช่อง 7 กลับมาดึงข้อมูลได้ปกติ
    page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "font"] else route.continue_())

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)
    
    found_url = None

    # [NEW] ระบบดักจับขั้นสุดยอด: คุ้ยหาลิงก์ m3u8 จากเนื้อหา API (JSON/Text) ที่เว็บโหลดมา
    def handle_response(response):
        nonlocal found_url
        if found_url: return
        
        # 1. เช็คจาก URL ตรงๆ ก่อน
        if ".m3u8" in response.url:
            found_url = response.url
            return
            
        # 2. เช็คเนื้อหาใน API Requests (พวก Fetch/XHR) ว่ามีลิงก์ซ่อนมาในรูปแบบ JSON ไหม
        try:
            if response.request.resource_type in ["fetch", "xhr"]:
                text = response.text()
                match = re.search(r'(https?:\/\/[^"\'<>\s]+\.m3u8[^"\'<>\s]*)', text)
                if match:
                    found_url = match.group(1).replace('\\/', '/')
                    print(f"🕵️ Found M3U8 inside API JSON for {name}!")
        except:
            pass

    page.on("response", handle_response)

    try:
        print(f"🔍 Loading [{name}] -> {target_url}")
        page.goto(target_url, timeout=45000, wait_until="domcontentloaded")
        
        page.mouse.wheel(0, 500)
        
        for frame in page.frames:
            try:
                frame.evaluate("""
                    document.querySelectorAll('video').forEach(v => {
                        v.muted = true;
                        v.play().catch(e => console.log(e));
                    });
                """)
            except:
                pass

        for _ in range(8):
            if found_url:
                break
            try:
                page.mouse.click(640, 360)
                page.keyboard.press("Space")
            except:
                pass
            page.wait_for_timeout(1000)

        # Fallback สแกนโค้ด HTML (ที่ช่วยชีวิตช่อง NationTV ไว้)
        if not found_url:
            html_content = page.content()
            match = re.search(r'(https?:\/\/[^"\'<>\s]+\.m3u8[^"\'<>\s]*)', html_content)
            if match:
                found_url = match.group(1).replace('\\/', '/')
                print(f"🕵️ Found M3U8 hidden in HTML source for {name}!")

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
