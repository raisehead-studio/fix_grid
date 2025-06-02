import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

def init_permissions(conn, cursor):
    for pid in range(1, 27):
      cursor.execute("""
          INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
          VALUES (?, ?)
      """, (1, pid))

    admin_password = generate_password_hash(os.getenv("ADMIN_PASS", "adminpass"))
    cursor.execute("""
    INSERT INTO users (username, password, full_name, phone, district_id, village_id, role_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('admin', admin_password, 'Admin User', '0900000000', 1, 1, 1))

    cursor.executescript("""
        INSERT INTO "main"."users" ("id", "username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES (2, 'test1', 'scrypt:32768:8:1$M2UieSG9wGWOXBhV$07b02600e5aa0cc81248dceca5aca73c440c57d43ccc7d0ce889d27f96e82e4ce47c296ffde6d72ce2601c08d06e53c678c060e3e9b4788bf2bbe8fff7754ac7', '里長', '000', 1, 1, 4, NULL, NULL, NULL);
        INSERT INTO "main"."users" ("id", "username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES (3, 'test2', 'scrypt:32768:8:1$ytHsxMOdiOzFv1Lj$3ce21842c2a4707da779254d4b509b7650daa8db2739440438e276a28aa59b99ae3433c11c863f6547fba425ebfc6264102cdbf720b447bb3464554bcfb7d3b7', '台電', '000', 1, 1, 5, NULL, NULL, NULL);
        INSERT INTO "main"."users" ("id", "username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES (4, 'test3', 'scrypt:32768:8:1$UljEm5uyAPGQUcmA$7807ce9910bccaade3d86741a2d0f0797c50bab2461056e2e4d4865a79559f690bc42c15eb96422a0c50f4f16d05edfb6c4466e448efa233e3c9ee288776fc7b', '台水', '000', 1, 1, 6, NULL, NULL, NULL);
        INSERT INTO "main"."users" ("id", "username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES (5, 'test4', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '上級長官', '000', 1, 2, 7, NULL, NULL, NULL);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 7);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 8);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 9);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 10);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 11);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 12);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 14);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 15);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 16);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 7);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 8);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 9);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 13);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 21);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 24);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 25);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 7);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 8);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 9);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 17);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 18);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 19);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 20);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 22);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 23);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 26);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 7);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 8);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 9);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 10);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 14);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 18);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 22);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 24);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 25);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 26);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 1);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 2);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 3);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 4);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 5);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 6);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 7);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 8);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 9);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 7);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 8);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 9);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 10);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 11);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 12);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 14);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 15);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 16);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 25);
        INSERT INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 26);
    """)
    print("✅ 角色帳號初始化完成")

if __name__ == "__main__":
    DB_PATH = "kao_power_water.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    init_permissions(conn, cursor)

    conn.commit()
    conn.close()
