DROP TABLE IF EXISTS taiwater_disasters;
CREATE TABLE IF NOT EXISTS taiwater_disasters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_path TEXT,
    created_at TEXT NOT NULL
);
