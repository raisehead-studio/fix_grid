import os
import sqlite3
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from datetime import datetime

disaster_bp = Blueprint('disaster', __name__)
UPLOAD_SUBDIR = os.path.join("uploads", "taiwater")

@disaster_bp.route("/api/taiwater_disasters")
@login_required
def list_disasters():
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM taiwater_disasters ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@disaster_bp.route("/api/taiwater_disasters", methods=["POST"])
@login_required
def create_disaster():
    name = request.form.get("name")
    created_at = datetime.now().isoformat()
    
    if not name or not name.strip():
        return jsonify(success=False, message="名稱不能為空"), 400
    
    name = name.strip()
    
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        
        # 檢查是否有同名
        cursor.execute("SELECT id FROM taiwater_disasters WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            return jsonify(success=False, message=f"已存在同名資料：{name}"), 409
        
        # 沒有同名，執行插入
        cursor.execute("INSERT INTO taiwater_disasters (name, created_at) VALUES (?, ?)", (name, created_at))
        conn.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    finally:
        if 'conn' in locals():
            conn.close()

@disaster_bp.route("/api/taiwater_disasters/<int:disaster_id>/upload", methods=["POST"])
@login_required
def upload_excel(disaster_id):
    file = request.files["file"]
    name = request.form.get("name")

    if not name:
        return jsonify(success=False, message="缺少檔案名稱"), 400

    name = secure_filename(name)
    ext = os.path.splitext(file.filename)[1] or ".xlsx"
    filename = f"{name}{ext}"

    upload_dir = os.path.join(current_app.root_path, "uploads", "taiwater")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("UPDATE taiwater_disasters SET file_path = ? WHERE id = ?", (file_path, disaster_id))
        conn.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    finally:
        if 'conn' in locals():
            conn.close()

@disaster_bp.route("/api/taiwater_disasters/<int:disaster_id>/download")
@login_required
def download_excel(disaster_id):
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM taiwater_disasters WHERE id = ?", (disaster_id,))
        row = cursor.fetchone()
    except Exception as e:
        return "Database error", 500
    finally:
        if 'conn' in locals():
            conn.close()

    if not row or not row[0]:
        return "Not found", 404

    file_path = row[0]
    if not os.path.exists(file_path):
        return "File not found", 404

    filename = os.path.basename(file_path)
    return send_file(file_path, as_attachment=True, download_name=filename)

@disaster_bp.route("/api/taiwater_disasters/example")
@login_required
def download_example():
    file_path = os.path.join(current_app.root_path, "static", "sheet7.xlsx")
    return send_file(file_path, as_attachment=True)

@disaster_bp.route("/api/taiwater_disasters/<int:disaster_id>", methods=["DELETE"])
@login_required
def delete_disaster(disaster_id):
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        
        # 先查詢檔案路徑
        cursor.execute("SELECT file_path FROM taiwater_disasters WHERE id = ?", (disaster_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify(success=False, message="找不到指定的災害資料"), 404
        
        file_path = row[0]
        
        # 刪除資料庫記錄
        cursor.execute("DELETE FROM taiwater_disasters WHERE id = ?", (disaster_id,))
        conn.commit()
        
        # 如果存在檔案，則刪除檔案
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                # 檔案刪除失敗，記錄錯誤但不影響資料庫刪除
                current_app.logger.warning(f"無法刪除檔案 {file_path}: {e}")
        
        return jsonify(success=True)
        
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    finally:
        if 'conn' in locals():
            conn.close()
