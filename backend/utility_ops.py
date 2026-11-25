import secrets
import string
import zipfile
import tempfile
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFont


# Code 128B encoding table (subset B: ASCII 32..126)
_CODE128_PATTERNS = [
    "212222", "222122", "222221", "121223", "121322", "131222", "122213", "122312", "132212", "221213",
    "221312", "231212", "112232", "122132", "122231", "113222", "123122", "123221", "223211", "221132",
    "221231", "213212", "223112", "312131", "311222", "321122", "321221", "312212", "322112", "322211",
    "212123", "212321", "232121", "111323", "131123", "131321", "112313", "132113", "132311", "211313",
    "231113", "231311", "112133", "112331", "132131", "113123", "113321", "133121", "313121", "211331",
    "231131", "213113", "213311", "213131", "311123", "311321", "331121", "312113", "312311", "332111",
    "314111", "221411", "431111", "111224", "111422", "121124", "121421", "141122", "141221", "112214",
    "112412", "122114", "122411", "142112", "142211", "241211", "221114", "413111", "241112", "134111",
    "111242", "121142", "121241", "114212", "124112", "124211", "411212", "421112", "421211", "212141",
    "214121", "412121", "111143", "111341", "131141", "114113", "114311", "411113", "411311", "113141",
    "114131", "311141", "411131", "211412", "211214", "211232", "2331112"
]


def generate_code128_barcode(text: str, output_path: Path, bar_width: int = 3, height: int = 120) -> Path:
    if not text:
        raise ValueError("Barcode text cannot be empty.")
    codes = [104]  # Start B
    for ch in text:
        val = ord(ch) - 32
        if val < 0 or val > 95:
            val = 0
        codes.append(val)
    checksum = codes[0]
    for idx, c in enumerate(codes[1:], start=1):
        checksum += idx * c
    codes.append(checksum % 103)
    codes.append(106)  # Stop

    bars = []
    for c in codes:
        pat = _CODE128_PATTERNS[c]
        is_bar = True
        for d in pat:
            bars.append((is_bar, int(d) * bar_width))
            is_bar = not is_bar

    total_w = sum(w for _, w in bars) + 40
    img = Image.new("RGB", (total_w, height + 40), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    x = 20
    for is_bar, w in bars:
        if is_bar:
            draw.rectangle([x, 12, x + w - 1, height], fill=(0, 0, 0))
        x += w
    draw.text((20, height + 10), text, fill=(0, 0, 0))
    img.save(str(output_path), format="PNG")
    return output_path


def generate_password(
    length: int = 16,
    uppercase: bool = True,
    lowercase: bool = True,
    numbers: bool = True,
    symbols: bool = True,
) -> str:
    length = max(4, min(128, int(length)))
    pool = ""
    guaranteed = []
    if uppercase:
        pool += string.ascii_uppercase
        guaranteed.append(secrets.choice(string.ascii_uppercase))
    if lowercase:
        pool += string.ascii_lowercase
        guaranteed.append(secrets.choice(string.ascii_lowercase))
    if numbers:
        pool += string.digits
        guaranteed.append(secrets.choice(string.digits))
    if symbols:
        syms = "!@#$%^&*()-_=+[]{};:,.?"
        pool += syms
        guaranteed.append(secrets.choice(syms))
    if not pool:
        pool = string.ascii_letters + string.digits
    rest = [secrets.choice(pool) for _ in range(max(0, length - len(guaranteed)))]
    chars = guaranteed + rest
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars[:length])


def make_zip(input_paths: List[Path], output_zip: Path) -> Path:
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        seen = {}
        for p in input_paths:
            name = p.name
            if name in seen:
                seen[name] += 1
                name = f"{p.stem}_{seen[name]}{p.suffix}"
            else:
                seen[name] = 0
            zf.write(p, arcname=name)
    return output_zip


def extract_zip_info(input_zip: Path) -> List[dict]:
    items = []
    with zipfile.ZipFile(input_zip, "r") as zf:
        for info in zf.infolist():
            if not info.is_dir():
                items.append({
                    "filename": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                })
    return items
