#!/bin/bash
set -e

echo "Starting deployment..."

# 更新專案
git pull origin main

# 解壓縮 libs.zip 到 libs/
echo "Unzipping dependencies..."
rm -rf libs  # 先清空舊的 libs（若存在）
unzip -q libs.zip

# 執行應用程式
echo "Running app..."
python3 app.py

echo "Deployment complete!"
