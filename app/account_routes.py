import sqlite3

from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

account_bp = Blueprint('account_bp', __name__)

@account_bp.route('/api/accounts')
@login_required
def get_accounts():
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
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
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@account_bp.route('/api/delete_account/<int:user_id>', methods=['DELETE'])
@login_required
def delete_account(user_id):
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# 取得所有角色
@account_bp.route('/api/roles')
@login_required
def get_roles():
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify(roles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# 取得所有行政區
@account_bp.route('/api/districts')
@login_required
def get_districts():
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM districts")
        districts = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify(districts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# 依區取得里
@account_bp.route('/api/villages/<int:district_id>')
@login_required
def get_villages(district_id):
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM villages WHERE district_id = ?", (district_id,))
        villages = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify(villages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# 建立新帳號
@account_bp.route('/api/create_account', methods=['POST'])
@login_required
def create_account():
    data = request.get_json()
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()

        # 先檢查 username 是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (data['username'],))
        if cursor.fetchone():
            return jsonify({'status': 'error', 'message': '帳號已存在'}), 400

        cursor.execute(
            "INSERT INTO users (username, password, full_name, phone, role_id, district_id, password_updated_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (
                data['username'],
                generate_password_hash(data['password']),
                data['full_name'],
                data['phone'],
                data['role_id'],
                data['district_id'],
            )
        )
        conn.commit()
        return jsonify({'status': 'ok'})
    except IntegrityError:
        return jsonify({'status': 'error', 'message': '資料庫錯誤'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@account_bp.route("/profile", methods=["POST"])
@login_required
def profile():
    user_id = current_user.id

    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form

    phone = data.get("phone")
    district_id = data.get("district")
    old_pw = data.get("old_password")
    new_pw = data.get("new_password")
    confirm_pw = data.get("confirm_password")

    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "找不到使用者"}), 404

        current_hashed_pw = row[0]

        # 更新基本資料
        cursor.execute("UPDATE users SET phone = ?, district_id = ? WHERE id = ?", (phone, district_id, user_id))

        # 如果有密碼欄位要改
        if old_pw or new_pw or confirm_pw:
            if not check_password_hash(current_hashed_pw, old_pw):
                return jsonify({"status": "error", "message": "舊密碼錯誤"})

            if new_pw != confirm_pw:
                return jsonify({"status": "error", "message": "新密碼與確認密碼不一致"})

            cursor.execute(
                "UPDATE users SET password = ?, password_updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (generate_password_hash(new_pw), user_id)
            )

        conn.commit()
        return jsonify({"status": "success", "message": "個人資料已更新"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@account_bp.route('/api/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    # 檢查要修改的用戶是否為超級管理員
    try:
        conn = sqlite3.connect('kao_power_water.db', timeout=10)
        c = conn.cursor()
        c.execute("SELECT role_id FROM users WHERE id = ?", (user_id,))
        target_user = c.fetchone()
        
        if not target_user:
            return jsonify({"error": "User not found"}), 404
            
        target_role_id = target_user[0]
        
        # 如果要修改的是超級管理員，則只有超級管理員才能修改
        if target_role_id == 1 and current_user.role_id != 1:
            return jsonify({"error": "Only super administrators can modify other super administrators"}), 403
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

    data = request.get_json()
    password = data.get("password")
    if not password:
        return jsonify({"error": "Missing password"}), 400

    try:
        conn = sqlite3.connect('kao_power_water.db', timeout=10)
        c = conn.cursor()
        c.execute("UPDATE users SET password = ?, password_updated_at = ? WHERE id = ?",
                  (generate_password_hash(password), datetime.now().isoformat(), user_id))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()
