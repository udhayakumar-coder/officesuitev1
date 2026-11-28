"""Image processing functions for All21Tool V2. All operations are in-memory."""
import io
import math
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import fitz

MAX_PIXELS = 80_000_000

def open_image(data):
    image = Image.open(io.BytesIO(data))
    image = ImageOps.exif_transpose(image)
    if image.width * image.height > MAX_PIXELS:
        raise ValueError("Image is too large to process safely (over 80 megapixels).")
    return image

def image_info(data):
    detected_format = Image.open(io.BytesIO(data)).format or "Unknown"
    im = open_image(data)
    return {
        "width": im.width, "height": im.height, "format": detected_format,
        "mode": im.mode, "file_size_kb": round(len(data)/1024, 2),
        "aspect_ratio": round(im.width/im.height, 4),
        "dpi": im.info.get("dpi", "Not embedded"),
        "has_transparency": im.mode in ("RGBA","LA") or "transparency" in im.info
    }

def encode_image(im, fmt="PNG", quality=92, dpi=None):
    fmt = fmt.upper()
    if fmt in ("JPG","JPEG"):
        fmt = "JPEG"
        if im.mode not in ("RGB","L"): im = im.convert("RGB")
    elif fmt == "WEBP":
        if im.mode not in ("RGB","RGBA"): im = im.convert("RGB")
    elif fmt in ("BMP","TIFF"):
        if im.mode not in ("RGB","RGBA","L"): im = im.convert("RGB")
    buf=io.BytesIO()
    kwargs={}
    if fmt in ("JPEG","WEBP"): kwargs.update(quality=int(quality), optimize=True)
    if fmt=="PNG": kwargs.update(optimize=True)
    if dpi: kwargs["dpi"]=(int(dpi),int(dpi))
    im.save(buf,format=fmt,**kwargs)
    return buf.getvalue()

def resize_image(data,width,height,fmt="PNG",quality=92):
    im=open_image(data)
    width,height=int(width),int(height)
    if width<1 or height<1 or width*height>MAX_PIXELS: raise ValueError("Invalid output dimensions.")
    im=im.resize((width,height),Image.Resampling.LANCZOS)
    return encode_image(im,fmt,quality)

def compress_to_target(data,target_kb,fmt="JPEG"):
    im=open_image(data)
    target=int(target_kb*1024)
    lo,hi=10,95
    best=encode_image(im,fmt,hi)
    while lo<=hi:
        mid=(lo+hi)//2
        candidate=encode_image(im,fmt,mid)
        if len(candidate)<=target:
            best=candidate; lo=mid+1
        else: hi=mid-1
    if len(best)>target:
        # Try reducing dimensions in small steps; preserve aspect ratio.
        scale=0.9
        while scale>=0.25:
            nw=max(1,int(im.width*scale)); nh=max(1,int(im.height*scale))
            candidate_im=im.resize((nw,nh),Image.Resampling.LANCZOS)
            candidate=encode_image(candidate_im,fmt,45)
            if len(candidate)<=target:
                best=candidate; break
            scale-=0.05
    return best, len(best)<=target

def convert_image(data,fmt,quality=92):
    return encode_image(open_image(data),fmt,quality)

def transform_image(data,left=0,right=0,top=0,bottom=0,angle=0,flip="None"):
    im=open_image(data)
    x0=int(im.width*left/100); x1=int(im.width*(1-right/100))
    y0=int(im.height*top/100); y1=int(im.height*(1-bottom/100))
    if x1<=x0 or y1<=y0: raise ValueError("Crop area is empty.")
    im=im.crop((x0,y0,x1,y1))
    if angle: im=im.rotate(-int(angle),expand=True)
    if flip=="Horizontal": im=ImageOps.mirror(im)
    elif flip=="Vertical": im=ImageOps.flip(im)
    return encode_image(im,"PNG")

def fit_within(data,max_width,fmt="JPEG",quality=85):
    im=open_image(data)
    if im.width>max_width:
        nh=max(1,int(im.height*max_width/im.width))
        im=im.resize((max_width,nh),Image.Resampling.LANCZOS)
    return encode_image(im,fmt,quality)

def add_watermark(data,text,position="Center",opacity=45,font_size=48):
    im=open_image(data).convert("RGBA")
    layer=Image.new("RGBA",im.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    try: font=ImageFont.truetype("DejaVuSans.ttf",int(font_size))
    except OSError: font=ImageFont.load_default()
    bbox=draw.textbbox((0,0),text,font=font)
    tw,th=bbox[2]-bbox[0],bbox[3]-bbox[1]
    pad=max(12,int(font_size*0.4))
    positions={
        "Center":((im.width-tw)//2,(im.height-th)//2),
        "Top Left":(pad,pad),"Top Right":(im.width-tw-pad,pad),
        "Bottom Left":(pad,im.height-th-pad),"Bottom Right":(im.width-tw-pad,im.height-th-pad)
    }
    x,y=positions.get(position,positions["Center"])
    draw.text((x,y),text,font=font,fill=(255,255,255,int(opacity*2.55)),stroke_width=max(1,font_size//24),stroke_fill=(0,0,0,int(opacity*1.5)))
    return encode_image(Image.alpha_composite(im,layer),"PNG")

def photo_sheet(data,width_mm=35,height_mm=45,copies=8,dpi=300):
    im=open_image(data).convert("RGB")
    w=max(1,round(width_mm/25.4*dpi)); h=max(1,round(height_mm/25.4*dpi))
    # Fit-to-frame keeps the full portrait; no automatic face crop is applied.
    ratio=max(w/im.width,h/im.height)
    nw,nh=round(im.width*ratio),round(im.height*ratio)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    x=(nw-w)//2; y=(nh-h)//2
    im=im.crop((x,y,x+w,y+h))
    page_w,page_h=round(210/25.4*dpi),round(297/25.4*dpi)
    margin=round(5/25.4*dpi); gap=round(3/25.4*dpi)
    cols=max(1,(page_w-2*margin+gap)//(w+gap))
    rows=max(1,(page_h-2*margin+gap)//(h+gap))
    if copies>cols*rows: raise ValueError(f"Only {cols*rows} copies fit on one A4 page at this size and DPI.")
    canvas=Image.new("RGB",(page_w,page_h),"white")
    draw=ImageDraw.Draw(canvas)
    for i in range(copies):
        row,col=divmod(i,cols)
        px=margin+col*(w+gap); py=margin+row*(h+gap)
        canvas.paste(im,(px,py)); draw.rectangle((px,py,px+w-1,py+h-1),outline=(100,100,100),width=max(1,dpi//300))
    pdf=io.BytesIO()
    canvas.save(pdf,"PDF",resolution=dpi)
    return pdf.getvalue()

def adjust_image(data,brightness=1.0,contrast=1.0,sharpness=1.0):
    im=open_image(data)
    im=ImageEnhance.Brightness(im).enhance(brightness)
    im=ImageEnhance.Contrast(im).enhance(contrast)
    im=ImageEnhance.Sharpness(im).enhance(sharpness)
    return encode_image(im,"PNG")
