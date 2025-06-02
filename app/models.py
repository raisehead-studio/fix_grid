from collections import defaultdict
import sqlite3

def get_user_by_username(username):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            users.id, users.username, users.password, users.full_name, 
            users.phone, districts.name, villages.name, users.role_id, 
            roles.name AS role_name
        FROM users
        LEFT JOIN roles ON users.role_id = roles.id
        LEFT JOIN districts ON users.district_id = districts.id
        LEFT JOIN villages ON users.village_id = villages.id
        WHERE users.username = ?
    """, (username,))
    
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'full_name': row[3],
            'phone': row[4],
            'district': row[5],
            'village': row[6],
            'role_id': row[7],
            'role_name': row[8]
        }
    return None

def get_user_by_id_with_role(user_id):
    conn = sqlite3.connect("kao_power_water.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.id, users.username, users.role_id, roles.name AS role_name, users.full_name
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE users.id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'username': row[1],
            'role_id': row[2],
            'role_name': row[3],
            'full_name': row[4]
        }
    return None

def get_role_page_permissions_from_db(db_path="kao_power_water.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.name, p.page, p.permission
        FROM role_permissions rp
        JOIN roles r ON rp.role_id = r.id
        JOIN permissions p ON rp.permission_id = p.id
    """)
    rows = cursor.fetchall()
    conn.close()

    result = defaultdict(lambda: defaultdict(list))
    for role_name, page, permission in rows:
        result[role_name][page].append(permission)
    
    return {role: dict(pages) for role, pages in result.items()}
