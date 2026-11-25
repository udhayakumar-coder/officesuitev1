import os
import uuid
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from . import pdf_ops, image_ops, utility_ops

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
WORK_DIR = BASE_DIR / "_temp_jobs"
WORK_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="BIGPDF 11zon Localhost", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _new_job_dir() -> tuple[str, Path]:
    job_id = uuid.uuid4().hex[:12]
    jdir = WORK_DIR / job_id
    jdir.mkdir(parents=True, exist_ok=True)
    return job_id, jdir


async def _save_uploads(files: List[UploadFile], jdir: Path) -> List[Path]:
    saved = []
    for idx, f in enumerate(files):
        safe_name = Path(f.filename or f"file_{idx}").name
        dest = jdir / f"{idx}_{safe_name}"
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved.append(dest)
    return saved


def _result_payload(job_id: str, out_path: Path, orig_size: int) -> dict:
    out_size = out_path.stat().st_size if out_path.exists() else 0
    saved_pct = round(((orig_size - out_size) / orig_size) * 100, 1) if orig_size > 0 else 0.0
    return {
        "status": "ok",
        "job_id": job_id,
        "filename": out_path.name,
        "original_size": orig_size,
        "output_size": out_size,
        "saved_percent": saved_pct,
        "download_url": f"/api/download/{job_id}/{out_path.name}",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "BIGPDF Localhost"}


@app.get("/api/download/{job_id}/{filename}")
def download_file(job_id: str, filename: str):
    fpath = WORK_DIR / job_id / Path(filename).name
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(fpath), filename=fpath.name, media_type="application/octet-stream")


@app.post("/api/pdf/compress")
async def api_compress_pdf(file: UploadFile = File(...), level: int = Form(60)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"compressed_{Path(file.filename or 'doc.pdf').stem}.pdf"
    try:
        pdf_ops.compress_pdf(in_path, out_path, level=level)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/merge")
async def api_merge_pdf(files: List[UploadFile] = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads(files, jdir)
    orig_size = sum(p.stat().st_size for p in paths)
    out_path = jdir / "merged.pdf"
    try:
        pdf_ops.merge_pdfs(paths, out_path)
        return _result_payload(job_id, out_path, orig_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/merge-pdf-image")
async def api_merge_pdf_image(files: List[UploadFile] = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads(files, jdir)
    orig_size = sum(p.stat().st_size for p in paths)
    out_path = jdir / "merged_pdf_images.pdf"
    try:
        pdf_ops.merge_pdf_and_images(paths, out_path)
        return _result_payload(job_id, out_path, orig_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/split")
async def api_split_pdf(
    file: UploadFile = File(...),
    mode: str = Form("all"),
    ranges: str = Form(""),
    fixed_count: int = Form(1),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"split_{Path(file.filename or 'doc').stem}.zip"
    try:
        pdf_ops.split_pdf(in_path, out_path, mode=mode, ranges=ranges, fixed_count=fixed_count)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/crop")
async def api_crop_pdf(
    file: UploadFile = File(...),
    top_pct: float = Form(0),
    bottom_pct: float = Form(0),
    left_pct: float = Form(0),
    right_pct: float = Form(0),
    pages: str = Form(""),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"cropped_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.crop_pdf(in_path, out_path, top_pct, bottom_pct, left_pct, right_pct, pages)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/organize")
async def api_organize_pdf(file: UploadFile = File(...), order: str = Form(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"organized_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.organize_pdf(in_path, out_path, order)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/rotate")
async def api_rotate_pdf(
    file: UploadFile = File(...),
    angle: int = Form(90),
    pages: str = Form(""),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"rotated_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.rotate_pdf(in_path, out_path, angle=angle, pages_str=pages)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/remove-pages")
async def api_remove_pages(file: UploadFile = File(...), pages: str = Form(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"removed_pages_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.remove_pdf_pages(in_path, out_path, pages)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/extract-pages")
async def api_extract_pages(file: UploadFile = File(...), pages: str = Form(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"extracted_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.extract_pdf_pages(in_path, out_path, pages)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/extract-images")
async def api_extract_images(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"images_{Path(file.filename or 'doc').stem}.zip"
    try:
        pdf_ops.extract_pdf_images(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/add-page-numbers")
async def api_add_page_numbers(
    file: UploadFile = File(...),
    position: str = Form("bottom-center"),
    start_num: int = Form(1),
    font_size: int = Form(12),
    fmt: str = Form("{n}"),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"numbered_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.add_page_numbers(in_path, out_path, position=position, start_num=start_num, font_size=font_size, fmt=fmt)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/watermark")
async def api_watermark_pdf(
    file: UploadFile = File(...),
    text: str = Form("CONFIDENTIAL"),
    opacity: float = Form(0.25),
    font_size: int = Form(48),
    angle: int = Form(45),
    color_hex: str = Form("#888888"),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"watermarked_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.add_watermark(in_path, out_path, text=text, opacity=opacity, font_size=font_size, angle=angle, color_hex=color_hex)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/image-to-pdf")
async def api_image_to_pdf(files: List[UploadFile] = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads(files, jdir)
    orig_size = sum(p.stat().st_size for p in paths)
    out_path = jdir / "images_converted.pdf"
    try:
        pdf_ops.images_to_pdf(paths, out_path)
        return _result_payload(job_id, out_path, orig_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/office-to-pdf")
async def api_office_to_pdf(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.office_to_pdf(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/text-to-pdf")
async def api_text_to_pdf(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'text').stem}.pdf"
    try:
        pdf_ops.text_to_pdf(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/to-image")
async def api_pdf_to_image(file: UploadFile = File(...), fmt: str = Form("PNG"), dpi: int = Form(150)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}_images.zip"
    try:
        pdf_ops.pdf_to_images(in_path, out_path, fmt=fmt, dpi=dpi)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/to-word")
async def api_pdf_to_word(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}.docx"
    try:
        pdf_ops.pdf_to_word(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/to-pptx")
async def api_pdf_to_pptx(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}.pptx"
    try:
        pdf_ops.pdf_to_pptx(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/to-excel")
async def api_pdf_to_excel(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}.xlsx"
    try:
        pdf_ops.pdf_to_excel(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/to-text")
async def api_pdf_to_text(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}.txt"
    try:
        pdf_ops.pdf_to_text(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/to-csv")
async def api_pdf_to_csv(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'doc').stem}.csv"
    try:
        pdf_ops.pdf_to_csv(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/unlock")
async def api_unlock_pdf(file: UploadFile = File(...), password: str = Form("")):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"unlocked_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.unlock_pdf(in_path, out_path, password=password)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/pdf/protect")
async def api_protect_pdf(file: UploadFile = File(...), password: str = Form(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"protected_{Path(file.filename or 'doc').stem}.pdf"
    try:
        pdf_ops.protect_pdf(in_path, out_path, password=password)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ebook/to-pdf")
async def api_ebook_to_pdf(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"{Path(file.filename or 'ebook').stem}.pdf"
    try:
        pdf_ops.ebook_to_pdf(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ebook/from-pdf")
async def api_pdf_to_ebook(file: UploadFile = File(...), target_format: str = Form("epub")):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    ext = target_format.lower().lstrip(".")
    out_path = jdir / f"{Path(file.filename or 'ebook').stem}.{ext}"
    try:
        pdf_ops.pdf_to_ebook(in_path, out_path, target_ext=ext)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/api/download-extracted/{job_id}/{filename:path}")
def download_extracted(job_id: str, filename: str):
    fpath = (WORK_DIR / job_id / "extracted" / filename).resolve()
    base = (WORK_DIR / job_id / "extracted").resolve()
    if not str(fpath).startswith(str(base)) or not fpath.exists():
        raise HTTPException(status_code=404, detail="Extracted file not found")
    return FileResponse(path=str(fpath), filename=fpath.name, media_type="application/octet-stream")

# ---------------- IMAGE TOOLS ---------------- #

@app.post("/api/image/compress")
async def api_compress_image(
    file: UploadFile = File(...),
    quality: int = Form(70),
    target_format: str = Form(""),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    ext = target_format.lower() if target_format else in_path.suffix.lstrip(".").lower() or "jpg"
    if ext == "jpeg":
        ext = "jpg"
    out_path = jdir / f"compressed_{Path(file.filename or 'img').stem}.{ext}"
    try:
        image_ops.compress_image(in_path, out_path, quality=quality, target_format=target_format)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/convert")
async def api_convert_image(file: UploadFile = File(...), target_format: str = Form("JPEG")):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    ext = target_format.lower()
    if ext == "jpeg":
        ext = "jpg"
    out_path = jdir / f"{Path(file.filename or 'img').stem}.{ext}"
    try:
        image_ops.convert_image(in_path, out_path, target_format=target_format)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/crop")
async def api_crop_image(
    file: UploadFile = File(...),
    left_pct: float = Form(0),
    top_pct: float = Form(0),
    right_pct: float = Form(0),
    bottom_pct: float = Form(0),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"cropped_{in_path.name}"
    try:
        image_ops.crop_image(in_path, out_path, left_pct, top_pct, right_pct, bottom_pct)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/resize")
async def api_resize_image(
    file: UploadFile = File(...),
    width: int = Form(800),
    height: int = Form(0),
    keep_aspect: bool = Form(True),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"resized_{in_path.name}"
    try:
        image_ops.resize_image(in_path, out_path, width=width, height=height, keep_aspect=keep_aspect)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/rotate")
async def api_rotate_image(file: UploadFile = File(...), angle: int = Form(90)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"rotated_{in_path.name}"
    try:
        image_ops.rotate_image(in_path, out_path, angle=angle)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/crop-circle")
async def api_crop_circle(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"circle_{Path(file.filename or 'img').stem}.png"
    try:
        image_ops.crop_circle_image(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/merge")
async def api_merge_images(files: List[UploadFile] = File(...), direction: str = Form("horizontal")):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads(files, jdir)
    orig_size = sum(p.stat().st_size for p in paths)
    out_path = jdir / "merged_photo.png"
    try:
        image_ops.merge_images(paths, out_path, direction=direction)
        return _result_payload(job_id, out_path, orig_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/image/photo-signature-resize")
async def api_photo_sig_resize(
    file: UploadFile = File(...),
    width: int = Form(200),
    height: int = Form(230),
    max_kb: int = Form(50),
):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"resized_{Path(file.filename or 'photo').stem}.jpg"
    try:
        image_ops.photo_signature_resize(in_path, out_path, width=width, height=height, max_kb=max_kb)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------- GIF, ZIP & UTILITIES ---------------- #

@app.post("/api/gif/images-to-gif")
async def api_images_to_gif(files: List[UploadFile] = File(...), duration_ms: int = Form(500)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads(files, jdir)
    orig_size = sum(p.stat().st_size for p in paths)
    out_path = jdir / "animated.gif"
    try:
        image_ops.images_to_gif(paths, out_path, duration_ms=duration_ms)
        return _result_payload(job_id, out_path, orig_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/gif/gif-to-images")
async def api_gif_to_images(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    out_path = jdir / f"frames_{Path(file.filename or 'anim').stem}.zip"
    try:
        image_ops.gif_to_images(in_path, out_path)
        return _result_payload(job_id, out_path, in_path.stat().st_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/zip/make")
async def api_zip_make(files: List[UploadFile] = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads(files, jdir)
    orig_size = sum(p.stat().st_size for p in paths)
    out_path = jdir / "archive.zip"
    try:
        utility_ops.make_zip(paths, out_path)
        return _result_payload(job_id, out_path, orig_size)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/zip/extract")
async def api_zip_extract(file: UploadFile = File(...)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    in_path = paths[0]
    try:
        items = utility_ops.extract_zip_info(in_path)
        extract_dir = jdir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(in_path, "r") as zf:
            zf.extractall(extract_dir)
        return {"status": "ok", "job_id": job_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/utils/barcode")
async def api_barcode(text: str = Form(...), bar_width: int = Form(3), height: int = Form(120)):
    job_id, jdir = _new_job_dir()
    out_path = jdir / "barcode.png"
    try:
        utility_ops.generate_code128_barcode(text, out_path, bar_width=bar_width, height=height)
        return _result_payload(job_id, out_path, 0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/utils/password")
async def api_password(
    length: int = Form(16),
    uppercase: bool = Form(True),
    lowercase: bool = Form(True),
    numbers: bool = Form(True),
    symbols: bool = Form(True),
):
    pw = utility_ops.generate_password(length, uppercase, lowercase, numbers, symbols)
    return {"status": "ok", "password": pw}


@app.post("/api/utils/color-extractor")
async def api_color_extractor(file: UploadFile = File(...), num_colors: int = Form(8)):
    job_id, jdir = _new_job_dir()
    paths = await _save_uploads([file], jdir)
    try:
        colors = image_ops.extract_colors(paths[0], num_colors=num_colors)
        return {"status": "ok", "colors": colors}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Serve Frontend
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
