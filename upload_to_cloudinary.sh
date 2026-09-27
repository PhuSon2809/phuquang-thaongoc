#!/bin/bash

# ============================================================
# Cloudinary Upload Script cho PhuQuang-ThaoNgoc Wedding
# ============================================================
# HƯỚNG DẪN:
# 1. Điền Cloud Name, API Key, API Secret vào bên dưới
# 2. Chạy: chmod +x upload_to_cloudinary.sh && ./upload_to_cloudinary.sh
# ============================================================

CLOUD_NAME="skj8brmw"
API_KEY="894557619617355"
API_SECRET="ZGd3m3OyO0e5-XtI5k6XhMk8XJE"

# Thư mục ảnh
PHOTOS_DIR="./photos"
ALBUM_DIR="./photos/Album"

# Folder trên Cloudinary
CLOUDINARY_PHOTOS_FOLDER="phuquang-thaongoc/photos"
CLOUDINARY_ALBUM_FOLDER="phuquang-thaongoc/album"

# File lưu kết quả URLs
OUTPUT_FILE="cloudinary_urls.json"

# Kiểm tra curl
if ! command -v curl &> /dev/null; then
    echo "❌ Cần cài curl. Chạy: brew install curl"
    exit 1
fi

# Kiểm tra thông tin
if [ "$CLOUD_NAME" = "your_cloud_name" ]; then
    echo "❌ Bạn chưa điền Cloud Name! Mở file này và sửa thông tin ở đầu file."
    exit 1
fi

echo "🚀 Bắt đầu upload ảnh lên Cloudinary..."
echo "☁️  Cloud: $CLOUD_NAME"
echo ""

# Tạo chữ ký cho upload
sign_request() {
    local timestamp=$1
    local folder=$2
    local public_id=$3
    echo -n "folder=${folder}&public_id=${public_id}&timestamp=${timestamp}${API_SECRET}" | openssl dgst -sha256 | awk '{print $2}'
}

# Hàm upload một file
upload_file() {
    local file_path=$1
    local folder=$2
    local filename=$(basename "$file_path" .jpg)
    local timestamp=$(date +%s)
    local signature=$(sign_request "$timestamp" "$folder" "$filename")
    
    echo "📤 Uploading: $(basename $file_path) → $folder/$filename"
    
    response=$(curl -s -X POST \
        "https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload" \
        -F "file=@${file_path}" \
        -F "api_key=${API_KEY}" \
        -F "timestamp=${timestamp}" \
        -F "folder=${folder}" \
        -F "public_id=${filename}" \
        -F "signature=${signature}" \
        -F "quality=auto" \
        -F "fetch_format=auto")
    
    # Extract URL từ response
    url=$(echo "$response" | grep -o '"secure_url":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$url" ]; then
        echo "   ✅ OK: $url"
        echo "$url"
    else
        echo "   ❌ Lỗi: $response"
        echo "ERROR"
    fi
}

# Khởi tạo JSON output
echo "{" > "$OUTPUT_FILE"
echo "  \"photos\": {" >> "$OUTPUT_FILE"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Upload thư mục: photos/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

photo_count=0
total_photos=$(ls "$PHOTOS_DIR"/*.jpg 2>/dev/null | wc -l | tr -d ' ')

for file in "$PHOTOS_DIR"/*.jpg; do
    [ -f "$file" ] || continue
    filename=$(basename "$file" .jpg)
    photo_count=$((photo_count + 1))
    
    url=$(upload_file "$file" "$CLOUDINARY_PHOTOS_FOLDER")
    
    if [ "$url" != "ERROR" ]; then
        if [ $photo_count -lt $total_photos ]; then
            echo "    \"${filename}\": \"${url}\"," >> "$OUTPUT_FILE"
        else
            echo "    \"${filename}\": \"${url}\"" >> "$OUTPUT_FILE"
        fi
    fi
    
    sleep 0.5  # Tránh rate limit
done

echo "  }," >> "$OUTPUT_FILE"
echo "  \"album\": {" >> "$OUTPUT_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Upload thư mục: photos/Album/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

album_count=0
total_album=$(ls "$ALBUM_DIR"/*.jpg 2>/dev/null | wc -l | tr -d ' ')

for file in "$ALBUM_DIR"/*.jpg; do
    [ -f "$file" ] || continue
    filename=$(basename "$file" .jpg)
    album_count=$((album_count + 1))
    
    url=$(upload_file "$file" "$CLOUDINARY_ALBUM_FOLDER")
    
    if [ "$url" != "ERROR" ]; then
        if [ $album_count -lt $total_album ]; then
            echo "    \"${filename}\": \"${url}\"," >> "$OUTPUT_FILE"
        else
            echo "    \"${filename}\": \"${url}\"" >> "$OUTPUT_FILE"
        fi
    fi
    
    sleep 0.5  # Tránh rate limit
done

echo "  }" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ XONG! Upload hoàn tất!"
echo "📄 URLs đã lưu vào: $OUTPUT_FILE"
echo ""
echo "💡 Bước tiếp theo:"
echo "   Mở $OUTPUT_FILE để xem tất cả URLs"
echo "   Sau đó cập nhật index.html với URLs mới"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
