-- 更新 power_reports 表格的 count 欄位約束
-- 允許 count 為 0，以便支援停電戶數為 0 時自動復電的功能

-- 1. 建立備份表格
CREATE TABLE power_reports_backup AS SELECT * FROM power_reports;

-- 2. 刪除原始表格
DROP TABLE power_reports;

-- 3. 重新建立表格，移除 count 欄位的 CHECK 約束
CREATE TABLE power_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    village_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    reason TEXT NOT NULL,
    count INTEGER NOT NULL CHECK (count >= 0),  -- 修改為允許 0
    contact_name TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    report_status BOOLEAN DEFAULT 0,
    report_restored_at DATETIME,

    taipower_status BOOLEAN DEFAULT NULL,
    taipower_restored_at DATETIME,
    taipower_note TEXT,
    taipower_eta_hours INTEGER,
    taipower_support TEXT,

    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (village_id) REFERENCES villages(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 4. 還原資料
INSERT INTO power_reports SELECT * FROM power_reports_backup;

-- 5. 刪除備份表格
DROP TABLE power_reports_backup;

-- 6. 重新建立索引（如果有的話）
-- 注意：這裡假設沒有其他索引，如果有索引需要重新建立

-- 完成
SELECT 'power_reports 表格更新完成，count 欄位現在允許 0 值' as message; 