DROP TABLE IF EXISTS power_reports;
CREATE TABLE IF NOT EXISTS power_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    village_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    reason TEXT NOT NULL,
    count INTEGER NOT NULL CHECK (count >= 1),
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

    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (village_id) REFERENCES villages(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
