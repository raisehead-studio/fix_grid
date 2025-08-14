#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫 2FA 更新腳本
一鍵更新資料庫結構，添加 Google Authenticator 雙因素認證相關功能
"""

import sqlite3
import sys
import os

def update_database():
    """更新資料庫結構，添加 2FA 相關欄位和表格"""
    
    db_path = "kao_power_water.db"
    
    # 檢查資料庫是否存在
    if not os.path.exists(db_path):
        print(f"❌ 錯誤：找不到資料庫檔案 {db_path}")
        return False
    
    try:
        # 連接到資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔗 已連接到資料庫")
        
        # 檢查 users 表是否已有 2FA 欄位
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 目前 users 表欄位：{', '.join(columns)}")
        
        # 添加 2FA 相關欄位到 users 表
        if 'two_factor_secret' not in columns:
            print("➕ 添加 two_factor_secret 欄位...")
            cursor.execute("ALTER TABLE users ADD COLUMN two_factor_secret TEXT")
            print("✅ two_factor_secret 欄位已添加")
        else:
            print("ℹ️  two_factor_secret 欄位已存在")
        
        if 'two_factor_enabled' not in columns:
            print("➕ 添加 two_factor_enabled 欄位...")
            cursor.execute("ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0")
            print("✅ two_factor_enabled 欄位已添加")
        else:
            print("ℹ️  two_factor_enabled 欄位已存在")
        
        if 'backup_codes' not in columns:
            print("➕ 添加 backup_codes 欄位...")
            cursor.execute("ALTER TABLE users ADD COLUMN backup_codes TEXT")
            print("✅ backup_codes 欄位已添加")
        else:
            print("ℹ️  backup_codes 欄位已存在")
        
        # 建立 two_factor_settings 表
        print("🏗️  建立 two_factor_settings 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS two_factor_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                secret_key TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 0,
                backup_codes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ two_factor_settings 表已建立")
        
        # 建立 two_factor_attempts 表
        print("🏗️  建立 two_factor_attempts 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS two_factor_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ip_address TEXT NOT NULL,
                attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ two_factor_attempts 表已建立")
        
        # 建立索引
        print("🔍 建立索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_two_factor_settings_user_id ON two_factor_settings(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_two_factor_attempts_user_id ON two_factor_attempts(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_two_factor_attempts_time ON two_factor_attempts(attempt_time)")
        print("✅ 索引已建立")
        
        # 檢查是否需要添加 2FA 管理權限
        print("🔐 檢查權限設定...")
        cursor.execute("SELECT COUNT(*) FROM permissions WHERE page = 'two_factor' AND permission = 'manage'")
        permission_count = cursor.fetchone()[0]
        
        if permission_count == 0:
            print("➕ 添加 2FA 管理權限...")
            cursor.execute("INSERT INTO permissions (page, permission) VALUES ('two_factor', 'manage')")
            
            # 為超級管理員和管理員角色添加 2FA 管理權限
            cursor.execute("SELECT id FROM roles WHERE name IN ('超級管理員', '管理員')")
            admin_roles = cursor.fetchall()
            
            permission_id = cursor.lastrowid
            
            for role_id in admin_roles:
                cursor.execute("""
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id) 
                    VALUES (?, ?)
                """, (role_id[0], permission_id))
            
            print("✅ 2FA 管理權限已添加")
        else:
            print("ℹ️  2FA 管理權限已存在")
        
        # 提交變更
        conn.commit()
        print("💾 資料庫變更已提交")
        
        # 驗證更新結果
        print("\n🔍 驗證更新結果...")
        
        # 檢查 users 表結構
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 更新後 users 表欄位：{', '.join(updated_columns)}")
        
        # 檢查新建立的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%two_factor%'")
        two_factor_tables = [table[0] for table in cursor.fetchall()]
        print(f"🏗️  2FA 相關表格：{', '.join(two_factor_tables)}")
        
        # 檢查權限
        cursor.execute("SELECT page, permission FROM permissions WHERE page = 'two_factor'")
        two_factor_permissions = cursor.fetchall()
        print(f"🔐 2FA 相關權限：{', '.join([f'{p[0]}:{p[1]}' for p in two_factor_permissions])}")
        
        print("\n🎉 資料庫更新完成！")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite 錯誤：{e}")
        return False
    except Exception as e:
        print(f"❌ 一般錯誤：{e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 資料庫連線已關閉")

def show_current_status():
    """顯示目前資料庫狀態"""
    
    db_path = "kao_power_water.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 資料庫檔案 {db_path} 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 目前資料庫狀態：")
        print("=" * 50)
        
        # 檢查 users 表結構
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("👥 Users 表欄位：")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\n🏗️  2FA 相關表格：")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%two_factor%'")
        two_factor_tables = cursor.fetchall()
        
        if two_factor_tables:
            for table in two_factor_tables:
                print(f"  - {table[0]}")
                # 顯示表格結構
                cursor.execute(f"PRAGMA table_info({table[0]})")
                table_columns = cursor.fetchall()
                for col in table_columns:
                    print(f"    * {col[1]} ({col[2]})")
        else:
            print("  - 尚無 2FA 相關表格")
        
        print("\n🔐 2FA 相關權限：")
        cursor.execute("SELECT page, permission FROM permissions WHERE page = 'two_factor'")
        two_factor_permissions = cursor.fetchall()
        
        if two_factor_permissions:
            for perm in two_factor_permissions:
                print(f"  - {perm[0]}: {perm[1]}")
        else:
            print("  - 尚無 2FA 相關權限")
        
        print("=" * 50)
        
    except sqlite3.Error as e:
        print(f"❌ SQLite 錯誤：{e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """主函數"""
    print("🚀 Google Authenticator 2FA 資料庫更新工具")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        show_current_status()
        return
    
    print("此腳本將更新資料庫結構以支援 Google Authenticator 雙因素認證")
    print("⚠️  請確保已備份資料庫檔案")
    
    # 詢問確認
    response = input("\n是否繼續執行？(y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ 操作已取消")
        return
    
    print("\n開始更新資料庫...")
    success = update_database()
    
    if success:
        print("\n✅ 資料庫更新成功！")
        print("\n接下來您可以：")
        print("1. 重新啟動應用程式")
        print("2. 登入系統後前往「雙因素認證管理」頁面")
        print("3. 設定您的 Google Authenticator")
    else:
        print("\n❌ 資料庫更新失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()
