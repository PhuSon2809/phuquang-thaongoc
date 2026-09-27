#!/usr/bin/env python3
"""
Upload Album photos lên Cloudinary - nén trước nếu > 9MB
(photos/ đã upload xong rồi, script này chỉ lo Album)
"""
import os
import io
import json
import warnings
warnings.filterwarnings("ignore")

from PIL import Image
import cloudinary
import cloudinary.uploader

CLOUD_NAME = "skj8brmw"
API_KEY = "894557619617355"
API_SECRET = "ZGd3m3OyO0e5-XtI5k6XhMk8XJE"

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)

ALBUM_DIR = "./photos/Album"
CLOUDINARY_ALBUM_FOLDER = "phuquang-thaongoc/album"
OUTPUT_FILE = "cloudinary_urls.json"
MAX_SIZE_BYTES = 9 * 1024 * 1024  # 9MB để an toàn


def compress_image(file_path, max_bytes=MAX_SIZE_BYTES):
    """Nén ảnh xuống dưới max_bytes, trả về bytes"""
    img = Image.open(file_path)
    # Chuyển sang RGB nếu cần
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    file_size = os.path.getsize(file_path)
    if file_size <= max_bytes:
        with open(file_path, "rb") as f:
            return f.read(), False  # không cần nén

    # Thử nén với quality giảm dần
    for quality in [85, 75, 65, 55, 45]:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        data = buffer.getvalue()
        if len(data) <= max_bytes:
            size_mb = len(data) / (1024 * 1024)
            orig_mb = file_size / (1024 * 1024)
            print(f"   🗜️  Nén: {orig_mb:.1f}MB → {size_mb:.1f}MB (q={quality})", end=" ")
            return data, True

    # Nếu vẫn còn lớn, resize xuống
    w, h = img.size
    for scale in [0.8, 0.6, 0.5]:
        resized = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buffer = io.BytesIO()
        resized.save(buffer, format="JPEG", quality=75, optimize=True)
        data = buffer.getvalue()
        if len(data) <= max_bytes:
            size_mb = len(data) / (1024 * 1024)
            orig_mb = file_size / (1024 * 1024)
            print(f"   🗜️  Resize+nén: {orig_mb:.1f}MB → {size_mb:.1f}MB", end=" ")
            return data, True

    raise ValueError(f"Không thể nén {file_path} xuống dưới {max_bytes/1024/1024:.0f}MB")


def main():
    print("📸 Upload Album - PhuQuang & ThaoNgoc")
    print(f"☁️  Cloud: {CLOUD_NAME}\n")

    # Load JSON hiện tại nếu có
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except Exception:
                existing = {}

    # Đảm bảo có key photos từ lần upload trước
    if "photos" not in existing:
        existing["photos"] = {}
    if "album" not in existing:
        existing["album"] = {}

    files = sorted([f for f in os.listdir(ALBUM_DIR) if f.lower().endswith(".jpg")])
    total = len(files)

    print(f"{'━'*45}")
    print(f"📁 photos/Album/ ({total} ảnh)")
    print(f"{'━'*45}\n")

    ok = 0
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(ALBUM_DIR, filename)
        public_id = os.path.splitext(filename)[0]
        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        print(f"[{i}/{total}] 📤 {filename} ({size_mb:.1f}MB)...", end=" ", flush=True)

        try:
            img_data, was_compressed = compress_image(file_path)

            # Upload từ bytes
            response = cloudinary.uploader.upload(
                img_data,
                folder=CLOUDINARY_ALBUM_FOLDER,
                public_id=public_id,
                quality="auto",
                fetch_format="auto",
                overwrite=True,
                resource_type="image",
            )
            url = response.get("secure_url", "")
            print(f"✅")
            existing["album"][filename] = url
            ok += 1

        except Exception as e:
            print(f"❌ {e}")

    # Lưu lại toàn bộ JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n{'━'*45}")
    print(f"✅ XONG! {ok}/{total} ảnh Album upload thành công")
    print(f"📄 URLs đã lưu: {OUTPUT_FILE}")
    print(f"{'━'*45}")


if __name__ == "__main__":
    main()
