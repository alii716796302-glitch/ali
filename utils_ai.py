import random, time, json, requests
from collections import deque
from config import AI_SEEK_URL, AI_SEEK_TOKEN, AI_SEEK_MODELS

context_store = {}

def get_context(user_id):
    if user_id not in context_store:
        context_store[user_id] = deque(maxlen=200)
    return context_store[user_id]

def update_context(user_id, user_msg, bot_msg):
    ctx = get_context(user_id)
    ctx.append({"role": "user", "content": user_msg})
    if bot_msg:
        ctx.append({"role": "assistant", "content": bot_msg})

def clear_context(user_id):
    if user_id in context_store:
        del context_store[user_id]

def format_context(user_id):
    ctx = get_context(user_id)
    if not ctx:
        return ""
    return "\n".join([f"{'مستخدم' if m['role']=='user' else 'مساعد'}: {m['content']}" for m in ctx]) + "\n\n"

def ask_ai_seek(prompt, ctx_text=""):
    try:
        headers = {
            'User-Agent': "okhttp/4.12.0",
            'Accept': "text/event-stream",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'x-app-id': "ai-seek",
            'x-device-info': "appIdentifier=ai.chatbot.ask.chat.deep.seek.assistant.search.free;appVersion=2.7.1-26042486;deviceType=android;deviceCountry=EG;appCountry=eg;local=ar_EG;language=ar;timezone=Asia/Baghdad;brand=POCO;model=2311DRK48G;androidId=6a33f4473da78ff9",
            'x-guru-internal-send-timeout-ms': "60000",
            'x-guru-internal-connect-timeout-ms': "60000",
            'x-access-token': AI_SEEK_TOKEN,
            'x-guru-internal-receive-timeout-ms': "120000"
        }
        ms = int(time.time() * 1000)
        rand = random.getrandbits(80)
        uuid_int = (ms << 80) | (0x7 << 76) | (rand & 0x0FFFFFFFFFFFFFFFFFFFFFFF)
        h = f'{uuid_int:032x}'
        ai_msg_id = f'{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}'
        payload = {
            "sessionId": "019def83-b582-7410-95dd-b747cc648582",
            "userMessageId": "019def8d-103e-78ba-9329-c9b714b900d0",
            "aiMessageId": ai_msg_id,
            "model": AI_SEEK_MODELS[0],
            "text": f"{ctx_text}المستخدم: {prompt}\nالمساعد:",
            "restrictedType": "FREE_USER",
            "sessionType": "NORMAL"
        }
        r = requests.post(AI_SEEK_URL, json=payload, headers=headers, stream=True, timeout=15)
        ans = ""
        for line in r.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if 'content' in data:
                        ans += data['content']
        return ans.strip() or None
    except:
        return None

def get_ai_response(prompt, user_id=None):
    ctx_text = format_context(user_id) if user_id else ""
    ans = ask_ai_seek(prompt, ctx_text)
    if ans:
        if user_id:
            update_context(user_id, prompt, ans)
        return ans
    q = prompt.lower()
    replies = {
        "مرحب": "مرحباً! كيف يمكنني مساعدتك اليوم؟ 😊",
        "شكر": "العفو! أنا هنا لمساعدتك في أي وقت. 🤝",
        "اسم": "أنا بوت ذكي تم تطويره لمساعدتك في استفساراتك. 🤖",
        "كيف حال": "أنا بخير، الحمد لله! كيف أنت؟ 😊",
        "وقت": f"الوقت الآن هو {time.strftime('%H:%M')} ⏰",
        "تاريخ": f"اليوم هو {time.strftime('%Y-%m-%d')} 📅",
    }
    for key, val in replies.items():
        if key in q:
            if user_id:
                update_context(user_id, prompt, val)
            return val
    fallback = "سؤال جيد! دعني أفكر في ذلك وأعود إليك بإجابة مفيدة. 💭"
    if user_id:
        update_context(user_id, prompt, fallback)
    return fallback
