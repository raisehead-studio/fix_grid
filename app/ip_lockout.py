import sqlite3
from datetime import datetime, timedelta
import json

class IPLockoutManager:
    def __init__(self, db_path="kao_power_water.db"):
        self.db_path = db_path
        self.max_attempts = 3  # 最大失敗次數
        self.lockout_duration = 1  # 鎖定時間（分鐘）
    
    def check_ip_lockout(self, ip_address):
        """檢查 IP 是否被鎖定"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 檢查是否有鎖定記錄
            cursor.execute("""
                SELECT is_locked, locked_until, failed_attempts
                FROM ip_lockouts 
                WHERE ip_address = ?
            """, (ip_address,))
            
            result = cursor.fetchone()
            
            if not result:
                return False, 0, None  # 沒有記錄，未鎖定
            
            is_locked, locked_until, failed_attempts = result
            
            if not is_locked:
                return False, failed_attempts, None
            
            # 檢查鎖定時間是否已過期
            if locked_until:
                locked_until_dt = datetime.fromisoformat(locked_until)
                if datetime.now() > locked_until_dt:
                    # 鎖定時間已過，解除鎖定並重置失敗次數
                    self._unlock_ip(ip_address)
                    return False, 0, None  # 重置失敗次數為 0
            
            return True, failed_attempts, locked_until
            
        except Exception as e:
            print(f"Error checking IP lockout: {e}")
            return False, 0, None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def record_failed_login(self, ip_address):
        """記錄登入失敗"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 檢查是否已有記錄
            cursor.execute("""
                SELECT id, failed_attempts, is_locked
                FROM ip_lockouts 
                WHERE ip_address = ?
            """, (ip_address,))
            
            result = cursor.fetchone()
            current_time = datetime.now()
            
            if result:
                # 更新現有記錄
                record_id, current_attempts, is_locked = result
                
                if is_locked:
                    # 如果已經被鎖定，檢查是否應該延長鎖定時間
                    cursor.execute("""
                        SELECT locked_until FROM ip_lockouts WHERE id = ?
                    """, (record_id,))
                    
                    locked_until_result = cursor.fetchone()
                    if locked_until_result and locked_until_result[0]:
                        locked_until_dt = datetime.fromisoformat(locked_until_result[0])
                        if current_time <= locked_until_dt:
                            # 仍在鎖定期間，延長鎖定時間
                            new_locked_until = current_time + timedelta(minutes=self.lockout_duration)
                            cursor.execute("""
                                UPDATE ip_lockouts 
                                SET locked_until = ?, updated_at = ?
                                WHERE id = ?
                            """, (new_locked_until.isoformat(), current_time.isoformat(), record_id))
                        else:
                            # 鎖定已過期，重新開始計數
                            cursor.execute("""
                                UPDATE ip_lockouts 
                                SET failed_attempts = 1, is_locked = 0, locked_until = NULL,
                                    first_failed_at = ?, last_failed_at = ?, updated_at = ?
                                WHERE id = ?
                            """, (current_time.isoformat(), current_time.isoformat(), current_time.isoformat(), record_id))
                    else:
                        # 沒有鎖定時間，重新開始計數
                        cursor.execute("""
                            UPDATE ip_lockouts 
                            SET failed_attempts = 1, is_locked = 0, locked_until = NULL,
                                first_failed_at = ?, last_failed_at = ?, updated_at = ?
                            WHERE id = ?
                        """, (current_time.isoformat(), current_time.isoformat(), current_time.isoformat(), record_id))
                else:
                    # 未鎖定，增加失敗次數
                    new_attempts = current_attempts + 1
                    
                    if new_attempts >= self.max_attempts:
                        # 達到最大失敗次數，鎖定 IP
                        locked_until = current_time + timedelta(minutes=self.lockout_duration)
                        cursor.execute("""
                            UPDATE ip_lockouts 
                            SET failed_attempts = ?, is_locked = 1, locked_until = ?,
                                last_failed_at = ?, updated_at = ?
                            WHERE id = ?
                        """, (new_attempts, locked_until.isoformat(), current_time.isoformat(), current_time.isoformat(), record_id))
                    else:
                        # 未達到鎖定條件，只更新失敗次數
                        cursor.execute("""
                            UPDATE ip_lockouts 
                            SET failed_attempts = ?, last_failed_at = ?, updated_at = ?
                            WHERE id = ?
                        """, (new_attempts, current_time.isoformat(), current_time.isoformat(), record_id))
            else:
                # 創建新記錄
                cursor.execute("""
                    INSERT INTO ip_lockouts 
                    (ip_address, failed_attempts, first_failed_at, last_failed_at, created_at, updated_at)
                    VALUES (?, 1, ?, ?, ?, ?)
                """, (ip_address, current_time.isoformat(), current_time.isoformat(), current_time.isoformat(), current_time.isoformat()))
            
            conn.commit()
            
            # 返回當前狀態
            return self.check_ip_lockout(ip_address)
            
        except Exception as e:
            print(f"Error recording failed login: {e}")
            return False, 0, None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def record_successful_login(self, ip_address):
        """記錄成功登入，重置失敗計數"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 重置該 IP 的失敗記錄
            cursor.execute("""
                UPDATE ip_lockouts 
                SET failed_attempts = 0, is_locked = 0, locked_until = NULL,
                    updated_at = ?
                WHERE ip_address = ?
            """, (datetime.now().isoformat(), ip_address))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error recording successful login: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _unlock_ip(self, ip_address):
        """解除 IP 鎖定並重置失敗計數"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ip_lockouts 
                SET is_locked = 0, locked_until = NULL, failed_attempts = 0, updated_at = ?
                WHERE ip_address = ?
            """, (datetime.now().isoformat(), ip_address))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error unlocking IP: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def force_unlock_ip(self, ip_address):
        """強制解除 IP 鎖定並完全重置記錄"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # 檢查 IP 是否存在記錄
            cursor.execute("""
                SELECT id FROM ip_lockouts WHERE ip_address = ?
            """, (ip_address,))
            
            result = cursor.fetchone()
            
            if result:
                # 更新現有記錄，完全重置
                cursor.execute("""
                    UPDATE ip_lockouts 
                    SET is_locked = 0, locked_until = NULL, failed_attempts = 0, 
                        first_failed_at = NULL, last_failed_at = NULL, updated_at = ?
                    WHERE ip_address = ?
                """, (datetime.now().isoformat(), ip_address))
            else:
                # 創建新記錄，狀態為未鎖定
                cursor.execute("""
                    INSERT INTO ip_lockouts 
                    (ip_address, failed_attempts, is_locked, created_at, updated_at)
                    VALUES (?, 0, 0, ?, ?)
                """, (ip_address, datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error force unlocking IP: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_remaining_attempts(self, ip_address):
        """獲取剩餘嘗試次數"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT failed_attempts FROM ip_lockouts WHERE ip_address = ?
            """, (ip_address,))
            
            result = cursor.fetchone()
            if result:
                return max(0, self.max_attempts - result[0])
            else:
                return self.max_attempts
                
        except Exception as e:
            print(f"Error getting remaining attempts: {e}")
            return self.max_attempts
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_lockout_info(self, ip_address):
        """獲取鎖定資訊"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT failed_attempts, is_locked, locked_until, last_failed_at
                FROM ip_lockouts WHERE ip_address = ?
            """, (ip_address,))
            
            result = cursor.fetchone()
            if result:
                failed_attempts, is_locked, locked_until, last_failed_at = result
                
                # 檢查鎖定時間是否已過期
                current_time = datetime.now()
                is_still_locked = False
                
                if is_locked and locked_until:
                    try:
                        locked_until_dt = datetime.fromisoformat(locked_until)
                        if current_time <= locked_until_dt:
                            is_still_locked = True
                        else:
                            # 鎖定已過期，自動更新資料庫狀態
                            cursor.execute("""
                                UPDATE ip_lockouts 
                                SET is_locked = 0, locked_until = NULL, failed_attempts = 0, updated_at = ?
                                WHERE ip_address = ?
                            """, (current_time.isoformat(), ip_address))
                            conn.commit()
                            is_still_locked = False
                            failed_attempts = 0  # 重置失敗次數
                    except:
                        # 如果時間格式有問題，假設已過期
                        is_still_locked = False
                        failed_attempts = 0
                
                return {
                    'failed_attempts': failed_attempts,
                    'is_locked': is_still_locked,
                    'locked_until': locked_until,
                    'last_failed_at': last_failed_at,
                    'remaining_attempts': max(0, self.max_attempts - failed_attempts)
                }
            else:
                return {
                    'failed_attempts': 0,
                    'is_locked': False,
                    'locked_until': None,
                    'last_failed_at': None,
                    'remaining_attempts': self.max_attempts
                }
                
        except Exception as e:
            print(f"Error getting lockout info: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
