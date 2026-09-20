export default async function handler(req, res) {
  const { channel } = req.query;

  // รายชื่อช่องทั้งหมดที่ระบบรองรับ
  const supportedChannels = [
    'amarin', 'thairath', 'true4u', 
    'ch7', 'ch3', 'tv5', 
    'thaich8', 'one31', 'gmm25', 'mcot', 'pptv', 'thaipbs', 'tpchannel', 'workpoint', 'nationtv', 'tnn'
  ];

  if (supportedChannels.includes(channel)) {
    try {
      const redisUrl = process.env.UPSTASH_REDIS_REST_URL;
      const redisToken = process.env.UPSTASH_REDIS_REST_TOKEN;

      const response = await fetch(`${redisUrl}/get/${channel}`, {
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
