DROP TABLE IF EXISTS water_reports;
CREATE TABLE IF NOT EXISTS water_reports (
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

    taiwater_status BOOLEAN DEFAULT 0,
    taiwater_restored_at DATETIME,
    taiwater_note TEXT,
    taiwater_eta_hours INTEGER,
    taiwater_water_station_status TEXT,
    taiwater_support TEXT,

    remarks TEXT,

    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (village_id) REFERENCES villages(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
