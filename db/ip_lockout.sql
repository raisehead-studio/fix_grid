-- IP 鎖定表
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
);

-- 創建索引以提高查詢效能
CREATE INDEX IF NOT EXISTS idx_ip_lockouts_ip ON ip_lockouts(ip_address);
CREATE INDEX IF NOT EXISTS idx_ip_lockouts_locked ON ip_lockouts(is_locked, locked_until);

-- 插入測試資料（可選）
-- INSERT INTO ip_lockouts (ip_address, failed_attempts, is_locked) VALUES ('127.0.0.1', 0, 0);
