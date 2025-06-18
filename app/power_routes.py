from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import sqlite3
from datetime import datetime

power_bp = Blueprint('power_bp', __name__)

def get_db():
    conn = sqlite3.connect("kao_power_water.db")
    conn.row_factory = sqlite3.Row
    return conn

@power_bp.route('/api/power_reports', methods=['GET'])
@login_required
def get_power_reports():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    if current_user.role_id == 4:  # 里幹事
        cursor.execute("""
            SELECT po.*, d.name, v.name
            FROM power_reports po
            LEFT JOIN districts d ON po.district_id = d.id
            LEFT JOIN villages v ON po.village_id = v.id
            WHERE po.deleted_at IS NULL AND po.created_by = ?
            ORDER BY po.created_at
        """, (current_user.id,))
    else:
        cursor.execute("""
            SELECT po.*, d.name, v.name
            FROM power_reports po
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
        reason=row[4],
        count=row[5],
        contact=row[6],
        phone=row[7],
        report_status=row[12],
        report_restored_at=row[13],
        taipower_status=row[14],
        taipower_description=row[16],
        taipower_eta_hours=row[17],
        taipower_support=row[18],
        taipower_restored_at=row[15],
        created_at=row[9]
    ) for row in rows]
    conn.close()
    return jsonify(data)

@power_bp.route("/api/power_reports", methods=["POST"])
@login_required
def create_power_report():
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO power_reports (district_id, village_id, location, reason, count, contact_name, contact_phone, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user.district_id,
        data["village_id"],
        data["location"],
        data["reason"],
        data["count"],
        data["contact_name"],
        data["contact_phone"],
        current_user.id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@power_bp.route('/api/power_reports/<int:id>/update_report', methods=['POST'])
@login_required
def update_power_outage_report(id):
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE power_reports
        SET location = ?, reason = ?, count = ?, contact_name = ?, contact_phone = ?, updated_at = datetime('now')
        WHERE id = ? AND report_status = 0
    """, (
        data['location'],
        data['reason'],
        data['count'],
        data['contact_name'],
        data['contact_phone'],
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@power_bp.route('/api/power_reports/<int:id>/toggle_report_status', methods=['POST'])
@login_required
def toggle_report_status(id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE power_reports
        SET report_status = 1, report_restored_at = current_timestamp
        WHERE id = ? AND report_status = 0
    """, (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "restored"})

@power_bp.route('/api/power_reports/<int:id>/update_taipower', methods=['POST'])
@login_required
def update_taipower_status(id):
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE power_reports
        SET taipower_note = ?, taipower_eta_hours = ?, taipower_support = ?, taipower_restored_at = current_timestamp
        WHERE id = ?
    """, (
        data['taipower_note'], data['taipower_eta_hours'], data['taipower_support'], id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@power_bp.route('/api/power_reports/<int:id>/toggle_taipower_status', methods=['POST'])
@login_required
def toggle_taipower_status(id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE power_reports
        SET taipower_status = 1, taipower_restored_at = current_timestamp
        WHERE id = ? AND taipower_status = 0
    """, (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "restored"})
