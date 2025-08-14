import pyotp
import json
import secrets
import sqlite3
from datetime import datetime

class TwoFactorAuth:
    def __init__(self, db_path="kao_power_water.db"):
        self.db_path = db_path
    
    def generate_secret(self):
        """生成新的 TOTP 密鑰"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count=10):
        """生成備用碼"""
        codes = []
        for _ in range(count):
            # 生成 8 位數的備用碼，每 4 位用 - 分隔
            code = f"{secrets.randbelow(10000):04d}-{secrets.randbelow(10000):04d}"
            codes.append(code)
        return codes
    
    def get_totp_uri(self, username, secret, issuer="高雄市停電停水通報系統"):
        """生成 TOTP URI 用於手動設定"""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
    
    def generate_setup_instructions(self, username, secret, totp_uri):
        """生成手動設定說明，不需要 QR Code"""
        return {
            'type': 'manual',
            'content': f"""
            <div class="text-center p-6 bg-blue-50 rounded-lg border border-blue-200">
                <div class="mb-4">
                    <svg class="h-16 w-16 mx-auto text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-4">手動設定 Google Authenticator</h3>
                
                <div class="bg-white p-4 rounded-lg border mb-4 text-left">
                    <div class="mb-3">
                        <label class="block text-sm font-medium text-gray-700 mb-1">帳號名稱</label>
                        <div class="bg-gray-100 p-2 rounded font-mono text-sm">{username}</div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="block text-sm font-medium text-gray-700 mb-1">服務名稱</label>
                        <div class="bg-gray-100 p-2 rounded font-mono text-sm">高雄市停電停水通報系統</div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="block text-sm font-medium text-gray-700 mb-1">密鑰 (Secret Key)</label>
                        <div class="bg-gray-100 p-2 rounded font-mono text-sm break-all">{secret}</div>
                        <button onclick="copyToClipboard('{secret}')" class="mt-1 text-xs text-blue-600 hover:text-blue-800 underline">
                            複製密鑰
                        </button>
                    </div>
                </div>
                
                <div class="text-sm text-gray-600 space-y-2">
                    <p><strong>設定步驟：</strong></p>
                    <ol class="list-decimal list-inside space-y-1 text-left">
                        <li>開啟 Google Authenticator 應用程式</li>
                        <li>點擊「+」號新增帳號</li>
                        <li>選擇「手動輸入」</li>
                        <li>輸入上述資訊</li>
                        <li>點擊「完成」</li>
                    </ol>
                </div>
                
                <div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <p class="text-sm text-yellow-800">
                        <strong>注意：</strong>設定完成後，請在下方輸入驗證碼來啟用 2FA
                    </p>
                </div>
            </div>
            """
        }
    
    def verify_totp(self, secret, token):
        """驗證 TOTP 令牌"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    def verify_backup_code(self, user_id, backup_code):
        """驗證備用碼"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 檢查備用碼是否有效
            cursor.execute("""
                SELECT backup_codes FROM users 
                WHERE id = ? AND two_factor_enabled = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            stored_codes = json.loads(result[0] or '[]')
            
            if backup_code in stored_codes:
                # 移除已使用的備用碼
                stored_codes.remove(backup_code)
                cursor.execute("""
                    UPDATE users SET backup_codes = ? WHERE id = ?
                """, (json.dumps(stored_codes), user_id))
                conn.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error verifying backup code: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def setup_2fa(self, user_id, secret, backup_codes):
        """設定 2FA"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 更新用戶的 2FA 設定
            cursor.execute("""
                UPDATE users 
                SET two_factor_secret = ?, two_factor_enabled = 1, backup_codes = ?
                WHERE id = ?
            """, (secret, json.dumps(backup_codes), user_id))
            
            # 同時更新 two_factor_settings 表
            cursor.execute("""
                INSERT OR REPLACE INTO two_factor_settings 
                (user_id, secret_key, enabled, backup_codes, updated_at)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
            """, (user_id, secret, json.dumps(backup_codes)))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error setting up 2FA: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def disable_2fa(self, user_id):
        """停用 2FA"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 清除用戶的 2FA 設定
            cursor.execute("""
                UPDATE users 
                SET two_factor_secret = NULL, two_factor_enabled = 0, backup_codes = NULL
                WHERE id = ?
            """, (user_id,))
            
            # 更新 two_factor_settings 表
            cursor.execute("""
                UPDATE two_factor_settings 
                SET enabled = 0, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error disabling 2FA: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def is_2fa_enabled(self, user_id):
        """檢查用戶是否啟用 2FA"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT two_factor_enabled FROM users WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return result and result[0]
            
        except Exception as e:
            print(f"Error checking 2FA status: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_user_2fa_info(self, user_id):
        """取得用戶的 2FA 資訊"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT two_factor_enabled, two_factor_secret, backup_codes
                FROM users WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'enabled': bool(result[0]),
                    'secret': result[1],
                    'backup_codes': json.loads(result[2] or '[]') if result[2] else []
                }
            return None
            
        except Exception as e:
            print(f"Error getting 2FA info: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def record_attempt(self, user_id, ip_address, success):
        """記錄 2FA 嘗試"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO two_factor_attempts (user_id, ip_address, success)
                VALUES (?, ?, ?)
            """, (user_id, ip_address, success))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error recording 2FA attempt: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_recent_attempts(self, user_id, limit=5):
        """取得最近的 2FA 嘗試記錄"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ip_address, attempt_time, success
                FROM two_factor_attempts
                WHERE user_id = ?
                ORDER BY attempt_time DESC
                LIMIT ?
            """, (user_id, limit))
            
            attempts = []
            for row in cursor.fetchall():
                attempts.append({
                    'ip_address': row[0],
                    'attempt_time': row[1],
                    'success': bool(row[2])
                })
            
            return attempts
            
        except Exception as e:
            print(f"Error getting recent attempts: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
