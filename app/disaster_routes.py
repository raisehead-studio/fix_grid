import os
import sqlite3
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
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
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
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
