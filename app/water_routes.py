from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import sqlite3
from datetime import datetime

water_bp = Blueprint('water_bp', __name__)

def get_db():
    conn = sqlite3.connect("kao_power_water.db")
    conn.row_factory = sqlite3.Row
    return conn

@water_bp.route('/api/water_reports', methods=['GET'])
@login_required
def get_water_reports():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    if current_user.role_id == 4:  # 里幹事
        cursor.execute("""
            SELECT po.*, d.name, v.name
            FROM water_reports po
            LEFT JOIN districts d ON po.district_id = d.id
            LEFT JOIN villages v ON po.village_id = v.id
            WHERE po.deleted_at IS NULL AND po.created_by = ?
            ORDER BY po.created_at
        """, (current_user.id,))
    else:
        cursor.execute("""
            SELECT po.*, d.name, v.name
            FROM water_reports po
            LEFT JOIN districts d ON po.district_id = d.id
            LEFT JOIN villages v ON po.village_id = v.id
            WHERE po.deleted_at IS NULL
            ORDER BY po.created_at
        """)
    rows = cursor.fetchall()
    data = [dict(
        id=row[0],
        district_id=row[1],
        district=row[-2],
        village_id=row[2],
        village=row[-1],
        location=row[3],
        water_station=row[4],
        contact=row[5],
        phone=row[6],
        report_status=row[11],
        report_restored_at=row[12],
        taiwater_status=row[13],
        taiwater_description=row[15],
        taiwater_eta_hours=row[16],
        taiwater_water_station_status=row[17],
        taiwater_support=row[18],
        taiwater_restored_at=row[14],
        created_at=row[8],
        remarks=row[19]
    ) for row in rows]
    conn.close()
    return jsonify(data)

@water_bp.route("/api/water_reports", methods=["POST"])
@login_required
def create_water_report():
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO water_reports (district_id, village_id, location, water_station, contact_name, contact_phone, created_by, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.district_id,
        data["village_id"],
        data["location"],
        data["water_station"],
        data["contact_name"],
        data["contact_phone"],
        current_user.id,
        data["remarks"]
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@water_bp.route('/api/water_reports/<int:id>/update_report', methods=['POST'])
@login_required
def update_water_outage_report(id):
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE water_reports
        SET location = ?, water_station = ?, contact_name = ?, contact_phone = ?, updated_at = datetime('now'), remarks = ?
        WHERE id = ? AND report_status = 0
    """, (
        data['location'],
        data['water_station'],
        data['contact_name'],
        data['contact_phone'],
        data['remarks'],
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@water_bp.route('/api/water_reports/<int:id>/toggle_report_status', methods=['POST'])
@login_required
def toggle_report_status(id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE water_reports
        SET report_status = 1, report_restored_at = current_timestamp
        WHERE id = ? AND report_status = 0
    """, (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "restored"})

@water_bp.route('/api/water_reports/<int:id>/update_taiwater', methods=['POST'])
@login_required
def update_taiwater_status(id):
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE water_reports
        SET taiwater_note = ?, taiwater_water_station_status = ?, taiwater_eta_hours = ?, taiwater_support = ?, taiwater_restored_at = current_timestamp
        WHERE id = ?
    """, (
        data['taiwater_note'], data['taiwater_water_station_status'], data['taiwater_eta_hours'], data['taiwater_support'], id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@water_bp.route('/api/water_reports/<int:id>/toggle_taiwater_status', methods=['POST'])
@login_required
def toggle_taiwater_status(id):
    data = request.get_json()
    if not data or 'taiwater_status' not in data:
        return jsonify({"error": "Missing taiwater_status"}), 400

    try:
        status = int(data['taiwater_status'])
        if status not in (0, 1):
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid taiwater_status, must be 0 or 1"}), 400

    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE water_reports
        SET taiwater_status = ?, taiwater_restored_at = current_timestamp
        WHERE id = ?
    """, (status, id))

    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "taiwater_status": status})
