-- 添加 original_count 欄位到 power_reports 表
-- 執行時間: 2025-07-27

-- 1. 備份現有資料
CREATE TABLE power_reports_backup AS SELECT * FROM power_reports;

-- 2. 刪除現有表格並重新建立
DROP TABLE power_reports;
-- 執行 power_reports.sql 來重新建立表格（包含 original_count 欄位）

-- 3. 將備份資料還原到新表格
INSERT INTO power_reports (
    id, district_id, village_id, location, reason, count, 
    contact_name, contact_phone, created_by, created_at, updated_at, deleted_at,
    report_status, report_restored_at, taipower_status, taipower_restored_at, 
    taipower_note, taipower_eta_hours, taipower_support, original_count
)
SELECT 
    id, district_id, village_id, location, reason, count,
    contact_name, contact_phone, created_by, created_at, updated_at, deleted_at,
    report_status, report_restored_at, taipower_status, taipower_restored_at,
    taipower_note, taipower_eta_hours, taipower_support, count as original_count
FROM power_reports_backup;

-- 4. 刪除備份表格
DROP TABLE power_reports_backup;

-- 5. 驗證資料
-- SELECT id, count, original_count FROM power_reports LIMIT 10; 