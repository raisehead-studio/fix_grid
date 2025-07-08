#!/bin/bash

DB_FILE="kao_power_water.db"

if [ ! -f "$DB_FILE" ]; then
  echo "Database file '$DB_FILE' not found!"
  exit 1
fi

echo "Clearing tables: power_reports, water_reports, taiwater_power_reports..."

sqlite3 "$DB_FILE" <<EOF
DELETE FROM power_reports;
DELETE FROM water_reports;
DELETE FROM taiwater_power_reports;
VACUUM;
EOF

echo "Tables cleared successfully."
