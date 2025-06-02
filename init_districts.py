import os
import sqlite3

def init_districts(conn, cursor):
    # 讀取所有行政區
    with open('districts/districts.txt', encoding='utf-8') as f:
        district_names = [line.strip() for line in f if line.strip()]

    for district_name in district_names:
        # 插入 district
        cursor.execute("INSERT OR IGNORE INTO districts (name) VALUES (?)", (district_name,))
        conn.commit()

        # 取得 district id
        cursor.execute("SELECT id FROM districts WHERE name = ?", (district_name,))
        district_id = cursor.fetchone()[0]

        # 插入 villages
        village_file = os.path.join('districts', f"{district_name}")
        if os.path.exists(village_file):
            with open(village_file, encoding='utf-8') as vf:
                village_names = [line.strip() for line in vf if line.strip()]
                for village_name in village_names:
                    cursor.execute("""
                        INSERT INTO villages (name, district_id)
                        VALUES (?, ?)
                    """, (village_name, district_id))
        else:
            print(f"[!] 找不到 {village_file}")

    # conn.commit()
    print("✅ 行政區資料初始化完成")

if __name__ == "__main__":
    DB_PATH = "kao_power_water.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    init_districts(conn, cursor)

    conn.commit()
    conn.close()
