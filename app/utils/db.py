import psycopg2
import os

print(os.getenv('POSTGRES_DB', None))
print(os.getenv('POSTGRES_PASSWORD', None))

db_conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'pass'),
        host=os.getenv('POSTGRES_HOST', 'db'),
        port=5432
    )

def get_margins(config_id) -> dict:
    cursor = db_conn.cursor()
    cursor.execute("SELECT ean, margin FROM margin_data WHERE configs_id = %s", (config_id,))
    margins = cursor.fetchall()
    cursor.close()
    result_dict = {ean: margin for ean, margin in margins}
    return result_dict

def get_config_settings(config_id) -> tuple:
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, value, url FROM configs WHERE id = %s", (config_id,))
    result = cursor.fetchone()
    cursor.close()
    return result #config_name, config_settings, config_url

def update_margin(config_id, ean, margin):
    # check if margin for ean exists:
    cursor = db_conn.cursor()
    print(f"EAN = {ean}")
    print(f"EAN = {margin}")
    cursor.execute("SELECT * FROM margin_data WHERE configs_id = %s AND ean = %s", (config_id, ean))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO margin_data (configs_id, ean, margin) VALUES (%s, %s, %s)", (config_id, ean, margin))
    else:
        cursor.execute("UPDATE margin_data SET margin = %s WHERE configs_id = %s AND ean = %s", (margin, config_id, ean))
    db_conn.commit()
    cursor.close()

