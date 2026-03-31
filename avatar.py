from PIL import Image, ImageDraw, ImageFont
import os

EXPRESSIONS = {
    "idle":     {"label": "idle~"},
    "thinking": {"label": "thinking~"},
    "talking":  {"label": "talking~"},
    "happy":    {"label": "happy!"},
    "error":    {"label": "oops~"},
}

def make_placeholder(expression: str, size=110) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, size-2, size-2], fill="#352d5e", outline="#7a56ae", width=2)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    text = "◕‿◕"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((size-tw)/2, (size-th)/2 - 4), text, fill="#e0dee0", font=font)
    return img

def load_avatar(expression: str, images_dir="assets") -> Image.Image:
    path = os.path.join(images_dir, f"{expression}.png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA").resize((110, 110), Image.LANCZOS)
    return make_placeholder(expression)