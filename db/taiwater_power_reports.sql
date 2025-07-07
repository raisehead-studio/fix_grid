-- DROP TABLE IF EXISTS taiwater_power_reports;
CREATE TABLE IF NOT EXISTS taiwater_power_reports (
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

    taipower_status BOOLEAN DEFAULT 0,
    taipower_restored_at DATETIME,
    taipower_note TEXT,
    taipower_eta_hours INTEGER,
    taipower_support TEXT,

    FOREIGN KEY (created_by) REFERENCES users(id)
);
