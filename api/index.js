export default async function handler(req, res) {
  const { channel } = req.query;

  if (channel === 'amarin') {
    try {
      const redisUrl = process.env.UPSTASH_REDIS_REST_URL;
      const redisToken = process.env.UPSTASH_REDIS_REST_TOKEN;

      // ดึงลิงก์จาก Redis
      const response = await fetch(`${redisUrl}/get/amarin`, {
        headers: {
          Authorization: `Bearer ${redisToken}`,
        },
      });
      
      const data = await response.json();
      const streamUrl = data.result;

      if (streamUrl && streamUrl.startsWith('http')) {
        return res.redirect(302, streamUrl.trim());
      }
    } catch (error) {
      console.error('Error fetching stream from Redis:', error);
    }
  }

  return res.status(404).send('Channel not found or stream offline.');
}
