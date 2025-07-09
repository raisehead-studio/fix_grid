import os
import sqlite3
from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from werkzeug.utils import secure_filename
# import pandas as pd
from datetime import datetime

disaster_bp = Blueprint('disaster', __name__)
UPLOAD_SUBDIR = os.path.join("uploads", "taiwater")

@disaster_bp.route("/api/taiwater_disasters")
def list_disasters():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM taiwater_disasters ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])

@disaster_bp.route("/api/taiwater_disasters", methods=["POST"])
def create_disaster():
    name = request.form.get("name")
    created_at = datetime.now().isoformat()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO taiwater_disasters (name, created_at) VALUES (?, ?)", (name, created_at))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@disaster_bp.route("/api/taiwater_disasters/<int:disaster_id>/upload", methods=["POST"])
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

    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE taiwater_disasters SET file_path = ? WHERE id = ?", (file_path, disaster_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)

# @disaster_bp.route("/api/taiwater_disasters/<int:disaster_id>/data")
# def read_excel_data(disaster_id):
#     conn = sqlite3.connect("kao_power_water.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT file_path FROM taiwater_disasters WHERE id = ?", (disaster_id,))
#     row = cursor.fetchone()
#     conn.close()
#     if not row or not row[0] or not os.path.exists(row[0]):
#         return jsonify(data=[])

#     df = pd.read_excel(row[0])
#     return jsonify(data=df.to_dict(orient="records"))

@disaster_bp.route("/api/taiwater_disasters/<int:disaster_id>/download")
def download_excel(disaster_id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM taiwater_disasters WHERE id = ?", (disaster_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return "Not found", 404

    print(row[0])
    return send_file(row[0], as_attachment=True)

@disaster_bp.route("/api/taiwater_disasters/example")
def download_example():
    file_path = os.path.join(current_app.root_path, "static", "example.xlsx")
    return send_file(file_path, as_attachment=True)
