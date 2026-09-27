#!/usr/bin/env python3
"""
Upload tất cả ảnh wedding lên Cloudinary dùng official SDK
"""
import os
import json
import warnings
warnings.filterwarnings("ignore")

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

PHOTOS_DIR = "./photos"
ALBUM_DIR = "./photos/Album"
CLOUDINARY_PHOTOS_FOLDER = "phuquang-thaongoc/photos"
CLOUDINARY_ALBUM_FOLDER = "phuquang-thaongoc/album"
OUTPUT_FILE = "cloudinary_urls.json"


def upload_folder(folder_path, cloudinary_folder, label):
    results = {}
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")])
    total = len(files)

    print(f"\n{'━'*45}")
    print(f"📁 {label} ({total} ảnh)")
    print(f"{'━'*45}")

    for i, filename in enumerate(files, 1):
        file_path = os.path.join(folder_path, filename)
        public_id = os.path.splitext(filename)[0]
        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        print(f"[{i}/{total}] 📤 {filename} ({size_mb:.1f}MB)...", end=" ", flush=True)

        try:
            response = cloudinary.uploader.upload(
                file_path,
                folder=cloudinary_folder,
                public_id=public_id,
                quality="auto",
                fetch_format="auto",
                overwrite=True,
            )
            url = response.get("secure_url", "")
            print(f"✅")
            results[filename] = url
        except Exception as e:
            print(f"❌ {e}")

    return results


def main():
    print("🚀 Cloudinary Upload - PhuQuang & ThaoNgoc")
    print(f"☁️  Cloud: {CLOUD_NAME}\n")

    all_results = {}

    photos_results = upload_folder(PHOTOS_DIR, CLOUDINARY_PHOTOS_FOLDER, "photos/")
    all_results["photos"] = photos_results

    album_results = upload_folder(ALBUM_DIR, CLOUDINARY_ALBUM_FOLDER, "photos/Album/")
    all_results["album"] = album_results

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    total_ok = len(photos_results) + len(album_results)
    total_all = (
        len([f for f in os.listdir(PHOTOS_DIR) if f.endswith(".jpg")]) +
        len([f for f in os.listdir(ALBUM_DIR) if f.endswith(".jpg")])
    )

    print(f"\n{'━'*45}")
    print(f"✅ XONG! {total_ok}/{total_all} ảnh upload thành công")
    print(f"📄 URLs đã lưu: {OUTPUT_FILE}")
    print(f"{'━'*45}")


if __name__ == "__main__":
    main()
