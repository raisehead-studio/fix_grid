# 資料庫更新說明

## 更新 power_reports 表格的 count 欄位約束

### 問題描述
原本 `power_reports` 表格的 `count` 欄位有 `CHECK (count >= 1)` 約束，這導致無法將停電戶數設為 0。

為了支援「將停電戶數改為 0 時自動復電」的功能，需要修改約束為 `CHECK (count >= 0)`。

### 更新步驟

1. **執行更新腳本**
   ```bash
   python update_db.py
   ```

2. **腳本會自動執行以下操作**：
   - 備份當前資料庫（檔名包含時間戳記）
   - 建立備份表格
   - 刪除原始表格
   - 重新建立表格（修改 count 欄位約束）
   - 還原所有資料
   - 刪除備份表格

### 檔案說明

- `update_count_constraint.sql`: SQL 更新腳本
- `update_db.py`: Python 執行腳本（位於根目錄）

### 注意事項

1. **執行前請確保**：
   - 沒有其他程式正在使用資料庫
   - 已備份重要資料

2. **如果更新失敗**：
   - 檢查備份檔案（檔名格式：`kao_power_water_backup_YYYYMMDD_HHMMSS.db`）
   - 可以手動還原備份檔案

3. **更新後的功能**：
   - 停電戶數可以設為 0
   - 當停電戶數為 0 時，系統會自動將狀態改為已復電
   - 會顯示確認視窗警告用戶

### 驗證更新

更新完成後，可以執行以下 SQL 查詢來驗證：

```sql
PRAGMA table_info(power_reports);
```

檢查 `count` 欄位的約束是否已更新為 `CHECK (count >= 0)`。 