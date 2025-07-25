import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

import sqlite3
from init_districts import init_districts
from init_permissions import init_permissions
from init_data import execute_sql_file

conn = sqlite3.connect("kao_power_water.db")
cursor = conn.cursor()

cursor.executescript("""
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS districts;
DROP TABLE IF EXISTS villages;
DROP TABLE IF EXISTS user_login_logs;
""")

cursor.executescript("""
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page TEXT NOT NULL,
    permission TEXT NOT NULL,
    UNIQUE(page, permission)
);
CREATE TABLE role_permissions (
    role_id INTEGER,
    permission_id INTEGER,
    FOREIGN KEY(role_id) REFERENCES roles(id),
    FOREIGN KEY(permission_id) REFERENCES permissions(id),
    PRIMARY KEY(role_id, permission_id)
);
CREATE TABLE districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE villages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    district_id INTEGER,
    FOREIGN KEY(district_id) REFERENCES districts(id)
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    district_id INTEGER,
    village_id INTEGER,
    role_id INTEGER,
    created_at DATETIME DEFAULT current_timestamp,
    updated_at DATETIME DEFAULT current_timestamp,
    deleted_at DATETIME,
    password_updated_at DATETIME DEFAULT current_timestamp,
    FOREIGN KEY(role_id) REFERENCES roles(id),
    FOREIGN KEY(district_id) REFERENCES districts(id),
    FOREIGN KEY(village_id) REFERENCES villages(id)
);
CREATE TRIGGER update_users_updated_at
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = current_timestamp WHERE id = NEW.id;
END;
CREATE TABLE user_login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ip TEXT NOT NULL,
    login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS taipower_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  district_id INTEGER,
  village_id INTEGER,
  count INTEGER,
  created_by INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
roles = ['超級管理員', '管理員', '民政局幹事', '里幹事', '台電人員', '台水人員', '上級長官']
cursor.executemany("INSERT INTO roles (name) VALUES (?)", [(r,) for r in roles])

permissions = [
    ('manage_accounts', 'view'),
    ('manage_roles', 'view'),
    ('profile', 'view'),
    ('power_outage', 'view'),
    ('power_outage', 'create_report'),
    ('power_outage', 'edit_report'),
    ('power_outage', 'view_status'),
    ('power_outage', 'edit_status'),
    ('water_outage', 'view'),
    ('water_outage', 'create_report'),
    ('water_outage', 'edit_report'),
    ('water_outage', 'view_status'),
    ('water_outage', 'edit_status'),
    ('taiwater_power_outage', 'view'),
    ('taiwater_power_outage', 'create_report'),
    ('taiwater_power_outage', 'edit_report'),
    ('taiwater_power_outage', 'view_status'),
    ('taiwater_power_outage', 'edit_status'),
    ('taipower_support', 'view'),
    ('power_stats', 'view'),
    ('water_stats', 'view'),
    ('taiwater_disaster', 'view'),
    ('taiwater_disaster', 'edit'),
    ('power_outage', 'excel'),
    ('water_outage', 'excel'),
    ('taiwater_power_outage', 'excel'),
]
cursor.executemany("INSERT INTO permissions (page, permission) VALUES (?, ?)", permissions)

init_districts(conn, cursor)
init_permissions(conn, cursor)
execute_sql_file(conn, cursor, 'db/power_reports.sql')
execute_sql_file(conn, cursor, 'db/water_reports.sql')
execute_sql_file(conn, cursor, 'db/taiwater_power_reports.sql')
execute_sql_file(conn, cursor, 'db/taiwater_disasters.sql')

execute_sql_file(conn, cursor, 'db/init_data.sql')

conn.commit()
conn.close()
print("✅ 資料庫初始化完成")
