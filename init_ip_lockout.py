#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化 IP 鎖定表
"""

import sqlite3
import os

def init_ip_lockout_table():
    """初始化 IP 鎖定表"""
    db_path = "kao_power_water.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 資料庫檔案 {db_path} 不存在")
        return False
    
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        # 創建 IP 鎖定表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_lockouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 1,
                first_failed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_failed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                locked_until DATETIME,
                is_locked BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 創建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ip_lockouts_ip ON ip_lockouts(ip_address)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ip_lockouts_locked ON ip_lockouts(is_locked, locked_until)
        """)
        
        conn.commit()
        print("✅ IP 鎖定表創建成功")
        
        # 檢查表結構
        cursor.execute("PRAGMA table_info(ip_lockouts)")
        columns = cursor.fetchall()
        
        print(f"📋 表結構：")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ 創建 IP 鎖定表失敗：{e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 開始初始化 IP 鎖定表...")
    
    if init_ip_lockout_table():
        print("🎉 IP 鎖定表初始化完成！")
    else:
        print("💥 IP 鎖定表初始化失敗！")
        exit(1)
