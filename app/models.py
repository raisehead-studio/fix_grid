from collections import defaultdict
import sqlite3

def get_user_by_username(username):
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                users.id, users.username, users.password, users.full_name, 
                users.phone, users.district_id, districts.name, users.village_id, villages.name, users.role_id, 
                roles.name AS role_name,
                users.password_updated_at
            FROM users
            LEFT JOIN roles ON users.role_id = roles.id
            LEFT JOIN districts ON users.district_id = districts.id
            LEFT JOIN villages ON users.village_id = villages.id
            WHERE users.username = ?
        """, (username,))
        row = cursor.fetchone()
    except Exception as e:
        print("DB error in get_user_by_username:", e)
        return None
    finally:
        if 'conn' in locals():
            conn.close()

    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'full_name': row[3],
            'phone': row[4],
            'district_id': row[5],
            'district': row[6],
            'village_id': row[7],
            'village': row[8],
            'role_id': row[9],
            'role_name': row[10],
            'password_updated_at': row[11],
        }
    return None

def get_user_by_id_with_role(user_id):
    try:
        conn = sqlite3.connect("kao_power_water.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.id, users.username, users.password, users.full_name, 
                users.phone, users.district_id, districts.name, users.village_id, villages.name, users.role_id, 
                roles.name AS role_name,
                users.password_updated_at
            FROM users
            LEFT JOIN roles ON users.role_id = roles.id
            LEFT JOIN districts ON users.district_id = districts.id
            LEFT JOIN villages ON users.village_id = villages.id
            WHERE users.id = ?
        """, (user_id,))
        row = cursor.fetchone()
    except Exception as e:
        print("DB error in get_user_by_id_with_role:", e)
        return None
    finally:
        if 'conn' in locals():
            conn.close()

    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'full_name': row[3],
            'phone': row[4],
            'district_id': row[5],
            'district': row[6],
            'village_id': row[7],
            'village': row[8],
            'role_id': row[9],
            'role_name': row[10],
            'password_updated_at': row[11],
        }
    return None

def get_role_page_permissions_from_db(db_path="kao_power_water.db"):
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.name, p.page, p.permission
            FROM role_permissions rp
            JOIN roles r ON rp.role_id = r.id
            JOIN permissions p ON rp.permission_id = p.id
        """)
        rows = cursor.fetchall()
    except Exception as e:
        print("DB error in get_role_page_permissions_from_db:", e)
        return {}
    finally:
        if 'conn' in locals():
            conn.close()

    result = defaultdict(lambda: defaultdict(list))
    for role_name, page, permission in rows:
        result[role_name][page].append(permission)
    
    return {role: dict(pages) for role, pages in result.items()}
