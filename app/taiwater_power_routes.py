from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import sqlite3
from datetime import datetime

taiwater_power_bp = Blueprint('taiwater_power_bp', __name__)

def get_db():
    conn = sqlite3.connect("kao_power_water.db")
    conn.row_factory = sqlite3.Row
    return conn

@taiwater_power_bp.route('/api/taiwater_power_reports', methods=['GET'])
@login_required
def get_taiwater_power_reports():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM taiwater_power_reports
        WHERE deleted_at IS NULL
        ORDER BY created_at
    """)
    rows = cursor.fetchall()
    data = [dict(
        id=row[0],
        facility=row[1],
        pole_number=row[2],
        electricity_number=row[3],
        reason=row[4],
        contact=row[5],
        phone=row[6],
        report_status=row[11],
        report_restored_at=row[12],
        taipower_status=row[13],
        taipower_restored_at=row[14],
        taipower_description=row[15],
        taipower_eta_hours=row[16],
        taipower_support=row[17],
        created_at=row[8],
        location=row[18],
    ) for row in rows]
    conn.close()
    return jsonify(data)

@taiwater_power_bp.route("/api/taiwater_power_reports", methods=["POST"])
@login_required
def create_taiwater_power_report():
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO taiwater_power_reports (facility, pole_number, electricity_number, reason, contact_name, contact_phone, created_by, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["facility"],
        data["pole_number"],
        data["electricity_number"],
        data["reason"],
        data["contact_name"],
        data["contact_phone"],
        current_user.id,
        data["location"],
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@taiwater_power_bp.route('/api/taiwater_power_reports/<int:id>/update_report', methods=['POST'])
@login_required
def update_taiwater_power_outage_report(id):
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE taiwater_power_reports
        SET facility = ?, pole_number = ?, electricity_number = ?, reason = ?, contact_name = ?, contact_phone = ?, updated_at = datetime('now')
        WHERE id = ? AND report_status = 0
    """, (
        data["facility"],
        data["pole_number"],
        data["electricity_number"],
        data["reason"],
        data["contact_name"],
        data["contact_phone"],
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@taiwater_power_bp.route('/api/taiwater_power_reports/<int:id>/toggle_report_status', methods=['POST'])
@login_required
def toggle_report_status(id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE taiwater_power_reports
        SET report_status = 1, report_restored_at = current_timestamp
        WHERE id = ? AND report_status = 0
    """, (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "restored"})

@taiwater_power_bp.route('/api/taiwater_power_reports/<int:id>/update_taipower', methods=['POST'])
@login_required
def update_taiwater_taipower_status(id):
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE taiwater_power_reports
        SET taipower_note = ?, taipower_eta_hours = ?, taipower_support = ?, taipower_restored_at = current_timestamp
        WHERE id = ?
    """, (
        data['taipower_note'], data['taipower_eta_hours'], data['taipower_support'], id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@taiwater_power_bp.route('/api/taiwater_power_reports/<int:id>/toggle_taipower_status', methods=['POST'])
@login_required
def toggle_taiwater_taipower_status(id):
    data = request.get_json()
    if not data or 'taipower_status' not in data:
        return jsonify({"error": "Missing taipower_status"}), 400

    try:
        status = int(data['taipower_status'])
        if status not in (0, 1):
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid taipower_status, must be 0 or 1"}), 400

    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE taiwater_power_reports
        SET taipower_status = ?, taipower_restored_at = current_timestamp
        WHERE id = ?
    """, (status, id))

    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "taipower_status": status})
