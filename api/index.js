import { Redis } from '@upstash/redis';

// เชื่อมต่อ Redis โดยใช้ Environment Variables ที่เราจะไปตั้งใน Vercel
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

export default async function handler(req, res) {
  // รับพารามิเตอร์ 'channel' จาก URL เช่น ?channel=true4u
  const { channel } = req.query;

  // ถ้าไม่ได้ระบุชื่อช่องมา
  if (!channel) {
    return res.status(400).send('Please specify a channel. Example: ?channel=true4u');
  }

  try {
    // 1. ดึงลิงก์ m3u8 ล่าสุดจาก Upstash Redis
    const streamUrl = await redis.get(channel);

    // ถ้าหาช่องไม่เจอ หรือไม่มีข้อมูล
    if (!streamUrl) {
      return res.status(404).send('Channel not found or stream offline.');
    }

    // 2. ตั้งค่า Cache ให้ Vercel จำไว้ 10 นาที (600 วินาที)
    // ตรงนี้สำคัญมาก ป้องกันเว็บล่มถ้ามีคนดูพร้อมกันเยอะๆ
    res.setHeader('Cache-Control', 's-maxage=600, stale-while-revalidate');

    // 3. รองรับ CORS ให้เว็บหรือแอปอื่นเรียกใช้งานได้
    res.setHeader('Access-Control-Allow-Origin', '*');

    // 4. สั่ง Redirect นำทางแอป IPTV ไปหาลิงก์สตรีมมิ่งที่ดึงมาได้
    res.redirect(302, streamUrl);

  } catch (error) {
    console.error('Redis Error:', error);
    res.status(500).send('Internal Server Error');
  }
}
