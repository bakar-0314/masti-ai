from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

folder = Path("static/icons")
folder.mkdir(parents=True, exist_ok=True)

for size in (192, 512):
    img = Image.new("RGB", (size, size), "#0b0b12")
    draw = ImageDraw.Draw(img)

    margin = size // 10

    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=size // 4,
        fill="#7c3aed"
    )

    try:
        font = ImageFont.truetype(
            "arial.ttf", size // 2
        )
    except OSError:
        font = ImageFont.load_default()

    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)

    x = (size - (bbox[2] - bbox[0])) / 2
    y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1]

    draw.text((x, y), text, fill="white", font=font)

    img.save(folder / f"icon-{size}.png")

print("Masti AI icons created successfully!")