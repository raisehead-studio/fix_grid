def execute_sql_file(conn, cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)

    print(f"✅ Executed SQL file: {filepath}")
