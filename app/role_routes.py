from flask import Blueprint, request, jsonify
from flask_login import login_required
import sqlite3

role_bp = Blueprint('role_bp', __name__)
DB = "kao_power_water.db"
TIMEOUT = 10  # SQLite connection timeout in seconds

@role_bp.route('/api/role_permissions/roles')
@login_required
def api_get_roles():
    try:
        conn = sqlite3.connect(DB, timeout=TIMEOUT)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = [dict(id=row[0], name=row[1]) for row in cursor.fetchall()]
        return jsonify(roles)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@role_bp.route('/api/role_permissions/<int:role_id>')
@login_required
def api_get_role_permissions(role_id):
    try:
        conn = sqlite3.connect(DB, timeout=TIMEOUT)
        cursor = conn.cursor()
        cursor.execute("SELECT id, page, permission FROM permissions")
        all_permissions = [dict(id=row[0], page=row[1], permission=row[2]) for row in cursor.fetchall()]
        cursor.execute("SELECT permission_id FROM role_permissions WHERE role_id = ?", (role_id,))
        assigned = [row[0] for row in cursor.fetchall()]
        return jsonify({
            "all_permissions": all_permissions,
            "assigned_permissions": assigned
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@role_bp.route('/api/set_role_permissions', methods=['POST'])
@login_required
def api_set_role_permissions():
    data = request.get_json()
    role_id = data.get("role_id")
    permission_ids = data.get("permission_ids", [])

    if not isinstance(role_id, int) or not isinstance(permission_ids, list):
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    try:
        conn = sqlite3.connect(DB, timeout=TIMEOUT)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
        cursor.executemany(
            "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
            [(role_id, pid) for pid in permission_ids]
        )
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@role_bp.route('/api/create_role', methods=['POST'])
@login_required
def api_create_role():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"status": "error", "message": "Role name is required."}), 400

    try:
        conn = sqlite3.connect(DB, timeout=TIMEOUT)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO roles (name) VALUES (?)", (name,))
        conn.commit()
        return jsonify({"status": "ok", "role_id": cursor.lastrowid, "name": name})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Role already exists."}), 409
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@role_bp.route('/api/delete_role/<int:role_id>', methods=['DELETE'])
@login_required
def api_delete_role(role_id):
    try:
        conn = sqlite3.connect(DB, timeout=TIMEOUT)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
        cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
