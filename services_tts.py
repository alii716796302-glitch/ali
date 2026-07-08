import io, requests, json
from gtts import gTTS

def text_to_speech(text, voice="alloy"):
    # ChatX TTS (fallback)
    try:
        url = "https://chatx.ai/audio_speech"
        payload = {
            "text": text,
            "model": "tts-1-hd",
            "voice": voice,
            "current_model": "gpt54_mini",
            "response_format": "pcm"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) Chrome/147.0.0.0 Mobile Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'x-csrf-token': 'BCEYoOvITvRuw2w7rdnYotzIchvNAEYJzL4OuYPU',
            'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?1',
            'origin': 'https://chatx.ai',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://chatx.ai/gpt',
            'accept-language': 'ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i'
        }
        r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
        if r.status_code == 200 and r.headers.get('content-type', '').startswith('audio/'):
            return r.content
    except:
        pass
    # gTTS fallback
    try:
        tts = gTTS(text=text, lang='ar', slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except:
        return None
