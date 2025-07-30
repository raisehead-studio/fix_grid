-- 更新三張表格的結構，包含 report_updated_time 欄位
-- 同時更新 power_reports 的 count 欄位約束和 original_count 欄位

-- ==================== power_reports 表格 ====================

-- 1. 建立 power_reports 備份表格
CREATE TABLE power_reports_backup AS SELECT * FROM power_reports;

-- 2. 刪除原始 power_reports 表格
DROP TABLE power_reports;

-- 3. 重新建立 power_reports 表格，包含 report_updated_time 欄位
CREATE TABLE power_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    village_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    reason TEXT NOT NULL,
    count INTEGER NOT NULL CHECK (count >= 0),  -- 允許 0
    original_count INTEGER NOT NULL,  -- 新增 original_count 欄位
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

    report_updated_time DATETIME DEFAULT NULL,  -- 新增 report_updated_time 欄位

    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (village_id) REFERENCES villages(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 4. 還原 power_reports 資料，設定 original_count = count
INSERT INTO power_reports (
    id, district_id, village_id, location, reason, count, original_count,
    contact_name, contact_phone, created_by, created_at, updated_at, deleted_at,
    report_status, report_restored_at, taipower_status, taipower_restored_at,
    taipower_note, taipower_eta_hours, taipower_support, report_updated_time
)
SELECT 
    id, district_id, village_id, location, reason, count, count as original_count,
    contact_name, contact_phone, created_by, created_at, updated_at, deleted_at,
    report_status, report_restored_at, taipower_status, taipower_restored_at,
    taipower_note, taipower_eta_hours, taipower_support, 
    CASE 
        WHEN report_restored_at IS NOT NULL THEN report_restored_at
        ELSE created_at 
    END as report_updated_time
FROM power_reports_backup;

-- 5. 刪除 power_reports 備份表格
DROP TABLE power_reports_backup;

-- ==================== water_reports 表格 ====================

-- 1. 建立 water_reports 備份表格
CREATE TABLE water_reports_backup AS SELECT * FROM water_reports;

-- 2. 刪除原始 water_reports 表格
DROP TABLE water_reports;

-- 3. 重新建立 water_reports 表格，包含 report_updated_time 欄位
CREATE TABLE water_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    village_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    water_station TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,

    report_status BOOLEAN DEFAULT 0,
    report_restored_at DATETIME,

    taiwater_status BOOLEAN DEFAULT NULL,
    taiwater_restored_at DATETIME,
    taiwater_note TEXT,
    taiwater_eta_hours INTEGER,
    taiwater_water_station_status TEXT,
    taiwater_support TEXT,

    remarks TEXT,

    report_updated_time DATETIME DEFAULT NULL,  -- 新增 report_updated_time 欄位

    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (village_id) REFERENCES villages(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 4. 還原 water_reports 資料
INSERT INTO water_reports (
    id, district_id, village_id, location, water_station, contact_name, contact_phone,
    created_by, created_at, updated_at, deleted_at, report_status, report_restored_at,
    taiwater_status, taiwater_restored_at, taiwater_note, taiwater_eta_hours,
    taiwater_water_station_status, taiwater_support, remarks, report_updated_time
)
SELECT 
    id, district_id, village_id, location, water_station, contact_name, contact_phone,
    created_by, created_at, updated_at, deleted_at, report_status, report_restored_at,
    taiwater_status, taiwater_restored_at, taiwater_note, taiwater_eta_hours,
    taiwater_water_station_status, taiwater_support, remarks, 
    CASE 
        WHEN report_restored_at IS NOT NULL THEN report_restored_at
        ELSE created_at 
    END as report_updated_time
FROM water_reports_backup;

-- 5. 刪除 water_reports 備份表格
DROP TABLE water_reports_backup;

-- ==================== taiwater_power_reports 表格 ====================

-- 1. 建立 taiwater_power_reports 備份表格
CREATE TABLE taiwater_power_reports_backup AS SELECT * FROM taiwater_power_reports;

-- 2. 刪除原始 taiwater_power_reports 表格
DROP TABLE taiwater_power_reports;

-- 3. 重新建立 taiwater_power_reports 表格，包含 report_updated_time 欄位
CREATE TABLE taiwater_power_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility TEXT NOT NULL,
    pole_number TEXT NOT NULL,
    electricity_number TEXT NOT NULL,
    reason TEXT NOT NULL,
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
    location TEXT NOT NULL DEFAULT '',

    report_updated_time DATETIME DEFAULT NULL,  -- 新增 report_updated_time 欄位

    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 4. 還原 taiwater_power_reports 資料
INSERT INTO taiwater_power_reports (
    id, facility, pole_number, electricity_number, reason, contact_name, contact_phone,
    created_by, created_at, updated_at, deleted_at, report_status, report_restored_at,
    taipower_status, taipower_restored_at, taipower_note, taipower_eta_hours,
    taipower_support, location, report_updated_time
)
SELECT 
    id, facility, pole_number, electricity_number, reason, contact_name, contact_phone,
    created_by, created_at, updated_at, deleted_at, report_status, report_restored_at,
    taipower_status, taipower_restored_at, taipower_note, taipower_eta_hours,
    taipower_support, location, 
    CASE 
        WHEN report_restored_at IS NOT NULL THEN report_restored_at
        ELSE created_at 
    END as report_updated_time
FROM taiwater_power_reports_backup;

-- 5. 刪除 taiwater_power_reports 備份表格
DROP TABLE taiwater_power_reports_backup;

-- ==================== 完成訊息 ====================

SELECT '✅ 三張表格更新完成！' as message;
SELECT '📝 power_reports: 新增 original_count 和 report_updated_time 欄位，count 允許 0 值' as message;
SELECT '📝 water_reports: 新增 report_updated_time 欄位' as message;
SELECT '📝 taiwater_power_reports: 新增 report_updated_time 欄位' as message; 