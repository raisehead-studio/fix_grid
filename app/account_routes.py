import sqlite3

from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

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

@account_bp.route("/profile", methods=["POST"])
@login_required
def profile():
    user_id = current_user.id

    if request.method == "POST":
        phone = request.form.get("phone")
        district_id = request.form.get("district")
        village_id = request.form.get("village")
        old_pw = request.form.get("old_password")
        new_pw = request.form.get("new_password")
        confirm_pw = request.form.get("confirm_password")

        conn = sqlite3.connect("kao_power_water.db")
        cursor = conn.cursor()

        # 取得目前密碼 hash
        cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            flash("找不到使用者", "error")
            conn.close()
            return redirect(url_for('page_info', page='profile'))

        current_hashed_pw = row[0]

        # 更新基本資料
        cursor.execute("""
            UPDATE users SET phone = ?, district_id = ?, village_id = ?
            WHERE id = ?
        """, (phone, district_id, village_id, user_id))

        # 若有密碼欄位，進行驗證與更新
        if old_pw or new_pw or confirm_pw:
            if not check_password_hash(current_hashed_pw, old_pw):
                flash("舊密碼錯誤", "error")
                conn.close()
                return redirect(url_for('page_info', page='profile'))

            if new_pw != confirm_pw:
                flash("新密碼與確認密碼不一致", "error")
                conn.close()
                return redirect(url_for('page_info', page='profile'))

            new_hashed_pw = generate_password_hash(new_pw)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed_pw, user_id))
            flash("密碼已更新", "success")

        conn.commit()
        conn.close()

        flash("個人資料已更新", "success")
        return redirect(url_for('page_info', page='profile'))

    return redirect(url_for('page_info', page='profile'))
