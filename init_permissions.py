import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

def init_permissions(conn, cursor):
    for pid in range(1, 32):
      cursor.execute("""
          INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
          VALUES (?, ?)
      """, (1, pid))

    admin_password = generate_password_hash(os.getenv("ADMIN_PASS", "adminpass"))
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, full_name, phone, district_id, village_id, role_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('admin', admin_password, 'Admin User', '0900000000', 1, 1, 1))

    cursor.executescript("""
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('test1', 'scrypt:32768:8:1$M2UieSG9wGWOXBhV$07b02600e5aa0cc81248dceca5aca73c440c57d43ccc7d0ce889d27f96e82e4ce47c296ffde6d72ce2601c08d06e53c678c060e3e9b4788bf2bbe8fff7754ac7', '里幹事', '000', 1, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('台電', 'scrypt:32768:8:1$ytHsxMOdiOzFv1Lj$3ce21842c2a4707da779254d4b509b7650daa8db2739440438e276a28aa59b99ae3433c11c863f6547fba425ebfc6264102cdbf720b447bb3464554bcfb7d3b7', '台電人員', '000', 1, NULL, 5, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('台水', 'scrypt:32768:8:1$UljEm5uyAPGQUcmA$7807ce9910bccaade3d86741a2d0f0797c50bab2461056e2e4d4865a79559f690bc42c15eb96422a0c50f4f16d05edfb6c4466e448efa233e3c9ee288776fc7b', '台水人員', '000', 1, NULL, 6, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('輪值', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '輪值人員', '000', 1, NULL, 7, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('民政局', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '民政局幹事', '000', 1, NULL, 3, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('鹽埕區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '鹽埕區公所', '000', 1, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('鼓山區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '鼓山區公所', '000', 2, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('左營區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '左營區公所', '000', 3, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('楠梓區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '楠梓區公所', '000', 4, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('三民區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '三民區公所', '000', 5, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('新興區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '新興區公所', '000', 6, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('前金區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '前金區公所', '000', 7, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('苓雅區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '苓雅區公所', '000', 8, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('前鎮區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '前鎮區公所', '000', 9, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('旗津區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '旗津區公所', '000', 10, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('小港區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '小港區公所', '000', 11, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('鳳山區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '鳳山區公所', '000', 12, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('林園區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '林園區公所', '000', 13, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('大寮區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '大寮區公所', '000', 14, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('大樹區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '大樹區公所', '000', 15, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('大社區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '大社區公所', '000', 16, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('仁武區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '仁武區公所', '000', 17, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('鳥松區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '鳥松區公所', '000', 18, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('岡山區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '岡山區公所', '000', 19, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('橋頭區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '橋頭區公所', '000', 20, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('燕巢區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '燕巢區公所', '000', 21, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('田寮區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '田寮區公所', '000', 22, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('阿蓮區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '阿蓮區公所', '000', 23, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('路竹區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '路竹區公所', '000', 24, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('湖內區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '湖內區公所', '000', 25, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('茄萣區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '茄萣區公所', '000', 26, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('永安區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '永安區公所', '000', 27, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('彌陀區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '彌陀區公所', '000', 28, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('梓官區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '梓官區公所', '000', 29, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('旗山區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '旗山區公所', '000', 30, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('美濃區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '美濃區公所', '000', 31, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('六龜區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '六龜區公所', '000', 32, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('甲仙區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '甲仙區公所', '000', 33, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('杉林區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '杉林區公所', '000', 34, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('內門區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '內門區公所', '000', 35, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('茂林區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '茂林區公所', '000', 36, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('桃源區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '桃源區公所', '000', 37, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."users" ("username", "password", "full_name", "phone", "district_id", "village_id", "role_id", "created_at", "updated_at", "deleted_at") VALUES ('那瑪夏區', 'scrypt:32768:8:1$90lzNDDC87M3jsuN$7886cab1dafeb5a0bb2c32d371ebc5d3674a6463e0ad22c9ebbc4a6e28f73f0c5b738dd40e557639ce1ac9d6cbf515394642d436816ea9fd1abaf6aa346b8f74', '那瑪夏區公所', '000', 38, NULL, 4, NULL, NULL, NULL);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 1);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 2);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 3);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 4);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 5);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 6);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 7);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 8);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 9);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 10);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 13);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 15);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 18);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 20);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 23);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 25);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 27);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 28);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (2, 29);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 7);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 8);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 9);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 10);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 11);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 12);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 15);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 16);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (4, 17);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 7);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 8);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 9);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 10);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 11);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 12);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 15);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 16);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 17);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 30);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (3, 31);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 7);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 8);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 9);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 10);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 13);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 14);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 20);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 23);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 24);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (5, 30);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 7);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 8);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 9);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 15);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 18);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 19);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 20);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 21);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 22);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 23);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (6, 29);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 7);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 8);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 9);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 10);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 12);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 13);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 14);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 15);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 17);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 18);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 19);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 20);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 22);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 23);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 24);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 25);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 26);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 27);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 28);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 29);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 30);
        INSERT OR IGNORE INTO "main"."role_permissions" ("role_id", "permission_id") VALUES (7, 31);
    """)
    print("✅ 角色帳號初始化完成")

if __name__ == "__main__":
    DB_PATH = "kao_power_water.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    init_permissions(conn, cursor)

    conn.commit()
    conn.close()
