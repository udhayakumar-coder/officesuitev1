import io
import zipfile
import tempfile
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw
import numpy as np


def _ensure_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
        return bg
    if img.mode != "RGB":
        return img.convert("RGB")
    return img


def compress_image(input_path: Path, output_path: Path, quality: int = 70, target_format: str = "") -> Path:
    quality = max(10, min(95, int(quality)))
    img = Image.open(str(input_path))
    fmt = target_format.upper() if target_format else (img.format or "JPEG").upper()
    if fmt == "JPG":
        fmt = "JPEG"

    if fmt in ("JPEG", "WEBP"):
        if fmt == "JPEG":
            img = _ensure_rgb(img)
        img.save(str(output_path), format=fmt, quality=quality, optimize=True)
    elif fmt == "PNG":
        # Quantize slightly if strong compression requested
        if quality < 75:
            colors = max(32, int(256 * (quality / 100.0)))
            img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors)
        img.save(str(output_path), format="PNG", optimize=True)
    else:
        img = _ensure_rgb(img)
        img.save(str(output_path), format="JPEG", quality=quality, optimize=True)
    return output_path


def convert_image(input_path: Path, output_path: Path, target_format: str = "JPEG") -> Path:
    fmt = target_format.upper()
    if fmt == "JPG":
        fmt = "JPEG"
    img = Image.open(str(input_path))
    if fmt in ("JPEG", "BMP"):
        img = _ensure_rgb(img)
    img.save(str(output_path), format=fmt, quality=92)
    return output_path


def crop_image(
    input_path: Path,
    output_path: Path,
    left_pct: float = 0,
    top_pct: float = 0,
    right_pct: float = 0,
    bottom_pct: float = 0,
) -> Path:
    img = Image.open(str(input_path))
    w, h = img.size
    l = int(w * (max(0.0, min(45.0, left_pct)) / 100.0))
    t = int(h * (max(0.0, min(45.0, top_pct)) / 100.0))
    r = int(w * (1.0 - max(0.0, min(45.0, right_pct)) / 100.0))
    b = int(h * (1.0 - max(0.0, min(45.0, bottom_pct)) / 100.0))
    cropped = img.crop((l, t, max(l + 1, r), max(t + 1, b)))
    cropped.save(str(output_path), format=img.format or "PNG")
    return output_path


def resize_image(
    input_path: Path,
    output_path: Path,
    width: int = 800,
    height: int = 0,
    keep_aspect: bool = True,
) -> Path:
    img = Image.open(str(input_path))
    orig_w, orig_h = img.size
    if keep_aspect:
        if width > 0 and height <= 0:
            height = max(1, int(orig_h * (width / orig_w)))
        elif height > 0 and width <= 0:
            width = max(1, int(orig_w * (height / orig_h)))
        elif width > 0 and height > 0:
            ratio = min(width / orig_w, height / orig_h)
            width = max(1, int(orig_w * ratio))
            height = max(1, int(orig_h * ratio))
    width = max(1, width or orig_w)
    height = max(1, height or orig_h)
    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    resized.save(str(output_path), format=img.format or "PNG")
    return output_path


def rotate_image(input_path: Path, output_path: Path, angle: int = 90) -> Path:
    img = Image.open(str(input_path))
    rotated = img.rotate(-int(angle), expand=True)
    rotated.save(str(output_path), format=img.format or "PNG")
    return output_path


def crop_circle_image(input_path: Path, output_path: Path) -> Path:
    img = Image.open(str(input_path)).convert("RGBA")
    size = min(img.size)
    left = (img.width - size) // 2
    top = (img.height - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)
    result.save(str(output_path), format="PNG")
    return output_path


def merge_images(input_paths: List[Path], output_path: Path, direction: str = "horizontal") -> Path:
    imgs = [_ensure_rgb(Image.open(str(p))) for p in input_paths]
    if not imgs:
        raise ValueError("No images provided.")
    if direction == "vertical":
        max_w = max(i.width for i in imgs)
        total_h = sum(i.height for i in imgs)
        canvas = Image.new("RGB", (max_w, total_h), (255, 255, 255))
        y = 0
        for i in imgs:
            canvas.paste(i, ((max_w - i.width) // 2, y))
            y += i.height
    else:
        total_w = sum(i.width for i in imgs)
        max_h = max(i.height for i in imgs)
        canvas = Image.new("RGB", (total_w, max_h), (255, 255, 255))
        x = 0
        for i in imgs:
            canvas.paste(i, (x, (max_h - i.height) // 2))
            x += i.width
    canvas.save(str(output_path), format="PNG")
    return output_path


def photo_signature_resize(
    input_path: Path,
    output_path: Path,
    width: int = 200,
    height: int = 230,
    max_kb: int = 50,
) -> Path:
    img = _ensure_rgb(Image.open(str(input_path)))
    resized = img.resize((max(10, width), max(10, height)), Image.Resampling.LANCZOS)
    target_bytes = max(5, int(max_kb)) * 1024
    best_data = None
    for q in range(95, 10, -5):
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=q, optimize=True)
        data = buf.getvalue()
        best_data = data
        if len(data) <= target_bytes:
            break
    output_path.write_bytes(best_data)
    return output_path


def images_to_gif(input_paths: List[Path], output_path: Path, duration_ms: int = 500) -> Path:
    imgs = [_ensure_rgb(Image.open(str(p))) for p in input_paths]
    if not imgs:
        raise ValueError("No images provided.")
    base_size = imgs[0].size
    frames = [i.resize(base_size, Image.Resampling.LANCZOS) for i in imgs]
    frames[0].save(
        str(output_path),
        save_all=True,
        append_images=frames[1:],
        duration=max(50, int(duration_ms)),
        loop=0,
    )
    return output_path


def gif_to_images(input_path: Path, output_zip: Path) -> Path:
    gif = Image.open(str(input_path))
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            idx = 0
            while True:
                try:
                    gif.seek(idx)
                    frame = gif.convert("RGBA")
                    out_p = Path(tmpdir) / f"frame_{idx + 1}.png"
                    frame.save(str(out_p), format="PNG")
                    zf.write(out_p, arcname=out_p.name)
                    idx += 1
                except EOFError:
                    break
    return output_zip


def extract_colors(input_path: Path, num_colors: int = 8) -> List[dict]:
    img = _ensure_rgb(Image.open(str(input_path)))
    img.thumbnail((200, 200))
    quantized = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=max(2, min(16, num_colors)))
    palette = quantized.getpalette()
    counts = quantized.getcolors() or []
    counts.sort(reverse=True, key=lambda x: x[0])
    total = sum(c[0] for c in counts) or 1
    results = []
    for cnt, color_idx in counts[:num_colors]:
        r = palette[color_idx * 3]
        g = palette[color_idx * 3 + 1]
        b = palette[color_idx * 3 + 2]
        hex_code = f"#{r:02X}{g:02X}{b:02X}"
        results.append({
            "hex": hex_code,
            "rgb": f"rgb({r}, {g}, {b})",
            "percent": round((cnt / total) * 100, 1),
        })
    return results
