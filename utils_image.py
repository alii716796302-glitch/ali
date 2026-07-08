import io, requests
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from config import HF_API_KEY, HF_URL

def generate_image(prompt):
    if HF_API_KEY == "hf_xxxxx":
        return None
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        r = requests.post(HF_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        if r.status_code == 200:
            return r.content
        return None
    except:
        return None

def resize_img(data, w, h):
    img = Image.open(io.BytesIO(data))
    img = img.resize((w, h), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def crop_img(data, x, y, w, h):
    img = Image.open(io.BytesIO(data))
    img = img.crop((x, y, x+w, y+h))
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def rotate_img(data, deg):
    img = Image.open(io.BytesIO(data))
    img = img.rotate(deg, expand=True)
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def grayscale_img(data):
    img = Image.open(io.BytesIO(data))
    img = img.convert('L')
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def sepia_img(data):
    img = Image.open(io.BytesIO(data)).convert('RGB')
    w, h = img.size
    px = img.load()
    for x in range(w):
        for y in range(h):
            r, g, b = px[x, y]
            px[x, y] = (
                min(int(0.393*r + 0.769*g + 0.189*b), 255),
                min(int(0.349*r + 0.686*g + 0.168*b), 255),
                min(int(0.272*r + 0.534*g + 0.131*b), 255)
            )
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def blur_img(data):
    img = Image.open(io.BytesIO(data))
    img = img.filter(ImageFilter.BLUR)
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def sharpen_img(data):
    img = Image.open(io.BytesIO(data))
    img = img.filter(ImageFilter.SHARPEN)
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def watermark_img(data, text):
    img = Image.open(io.BytesIO(data)).convert('RGBA')
    txt = Image.new('RGBA', img.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    try:
        font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 30)
    except:
        try:
            font = ImageFont.truetype("/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf", 30)
        except:
            font = ImageFont.load_default()
    draw.text((20, img.height-60), text, font=font, fill=(255,255,255,200))
    combined = Image.alpha_composite(img, txt)
    out = io.BytesIO()
    combined.convert('RGB').save(out, format='PNG')
    return out.getvalue()

def compress_img(data, quality):
    img = Image.open(io.BytesIO(data))
    out = io.BytesIO()
    img.save(out, format='JPEG', quality=quality, optimize=True)
    return out.getvalue()
