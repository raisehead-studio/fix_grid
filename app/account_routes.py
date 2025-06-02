import sqlite3

from flask import Blueprint, jsonify, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

account_bp = Blueprint('account_bp', __name__)

@account_bp.route('/api/accounts')
@login_required
def get_accounts():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.id, users.username, users.full_name,
               roles.name AS role_name,
               districts.name AS district_name,
               villages.name AS village_name
        FROM users
        LEFT JOIN roles ON users.role_id = roles.id
        LEFT JOIN districts ON users.district_id = districts.id
        LEFT JOIN villages ON users.village_id = villages.id
    """)
    result = [
        {
            'id': row[0],
            'username': row[1],
            'full_name': row[2],
            'role_name': row[3] or '',
            'district_name': row[4] or '',
            'village_name': row[5] or ''
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(result)

@account_bp.route('/api/delete_account/<int:user_id>', methods=['DELETE'])
@login_required
def delete_account(user_id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

# 取得所有角色
@account_bp.route('/api/roles')
def get_roles():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM roles")
    roles = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(roles)

# 取得所有行政區
@account_bp.route('/api/districts')
def get_districts():
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM districts")
    districts = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(districts)

# 依區取得里
@account_bp.route('/api/villages/<int:district_id>')
def get_villages(district_id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM villages WHERE district_id = ?", (district_id,))
    villages = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(villages)

# 建立新帳號
@account_bp.route('/api/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, full_name, phone, role_id, district_id, village_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data['username'],
            generate_password_hash(data['password']),
            data['full_name'],
            data['phone'],
            data['role_id'],
            data['district_id'],
            data['village_id']
        )
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})