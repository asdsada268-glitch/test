export default async function handler(req, res) {
  const { channel } = req.query;

  // 1. ระบุ Referer หลอกให้ตรงกับช่องนั้นๆ เพื่อทะลวงระบบป้องกัน
  const referers = {
    'amarin': 'https://www.amarintv.com/',
    'thairath': 'https://www.thairath.co.th/',
    'true4u': 'https://true4u.com/',
    'ch7': 'https://www.ch7.com/',
    'tv5': 'https://thaitv5hd.com/',
    'thaich8': 'https://www.thaich8.com/',
    'pptv': 'https://www.pptvhd36.com/',
    'thaipbs': 'https://www.thaipbs.or.th/',
    'tpchannel': 'https://www.tpchannel.org/',
    'workpoint': 'https://workpointtv.com/',
    'nationtv': 'https://www.nationtv.tv/'
  };

  if (referers[channel]) {
    try {
      const redisUrl = process.env.UPSTASH_REDIS_REST_URL;
      const redisToken = process.env.UPSTASH_REDIS_REST_TOKEN;

      // 2. ดึงลิงก์ดิบจาก Upstash Redis ที่ GitHub Actions กวาดมาให้
      const response = await fetch(`${redisUrl}/get/${channel}`, {
        headers: { Authorization: `Bearer ${redisToken}` },
      });
      
      const data = await response.json();
      const streamUrl = data.result;

      if (streamUrl && streamUrl.startsWith('http')) {
        
        // 3. Vercel รับบทตัวแทน ไปดึงไฟล์ .m3u8 มาให้ พร้อมแนบ Header จำลอง
        const m3u8Response = await fetch(streamUrl, {
          headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": referers[channel]
          }
        });

        if (!m3u8Response.ok) {
           return res.status(m3u8Response.status).send(`Stream CDN blocked the request. Status: ${m3u8Response.status}`);
        }

        let m3u8Content = await m3u8Response.text();

        // 4. แปลง URL ซับซ้อนภายในไฟล์ (Relative Path) ให้เป็นลิงก์ตรง (Absolute URL)
        const baseUrl = streamUrl.substring(0, streamUrl.lastIndexOf('/') + 1);
        // ใช้ Regex แทรก Base URL นำหน้าไฟล์ .ts และ .m3u8 ตัวลูก
        m3u8Content = m3u8Content.replace(/^(?!http|#)(.*)$/gm, `${baseUrl}$1`);

        // 5. ส่งไฟล์สตรีมที่ผ่านการแปลงแล้วกลับไปให้ผู้ใช้งานเล่นได้โดยตรง
        res.setHeader('Content-Type', 'application/vnd.apple.mpegurl');
        res.setHeader('Access-Control-Allow-Origin', '*'); // ปลดล็อก CORS ให้ดูในเว็บหรือแอพไหนก็ได้
        return res.status(200).send(m3u8Content);
      }
    } catch (error) {
      console.error('Error proxying stream:', error);
      return res.status(500).send('Internal Server Error');
    }
  }

  return res.status(404).send('Channel not found or stream offline.');
}
