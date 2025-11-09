import psycopg2
import os
from utils.logger import get_technical_logger

logger = get_technical_logger(__name__)

# Lazy database connection - only connect when needed
_db_conn = None

def get_db_connection():
    """Get or create database connection."""
    global _db_conn
    if _db_conn is None:
        _db_conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'db'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'pass'),
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=5432
        )
    return _db_conn

def get_margins(config_id) -> dict:
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT ean, margin FROM margin_data WHERE configs_id = %s", (config_id,))
    margins = cursor.fetchall()
    cursor.close()
    result_dict = {ean: margin for ean, margin in margins}
    return result_dict

def get_config_settings(config_id) -> tuple:
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, value, url FROM configs WHERE id = %s", (config_id,))
    result = cursor.fetchone()
    cursor.close()
    return result #config_name, config_settings, config_url

def update_margin(config_id, ean, margin):
    db_conn = get_db_connection()
    logger.debug(f"Updating margin: config_id={config_id}, ean={ean}, margin={margin}")
    # check if margin for ean exists:
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM margin_data WHERE configs_id = %s AND ean = %s", (config_id, ean))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO margin_data (configs_id, ean, margin) VALUES (%s, %s, %s)", (config_id, ean, margin))
    else:
        cursor.execute("UPDATE margin_data SET margin = %s WHERE configs_id = %s AND ean = %s", (margin, config_id, ean))
    db_conn.commit()
    cursor.close()


def get_product_ids() -> dict:
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT ean, product_id FROM product_ean_mapping")
    result = cursor.fetchall()
    cursor.close()
    product_ids_dict = {ean: product_id for ean, product_id in result}
    return product_ids_dict

def remove_all_product_ids_mapping():
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM product_ean_mapping")
    db_conn.commit()
    cursor.close()

def insert_or_update_product_ids(ean, product_id):
    db_conn = get_db_connection()
    query = f"""
    INSERT INTO product_ean_mapping (ean, product_id)
    VALUES ('{ean}', '{product_id}')
    ON CONFLICT (ean)
    DO UPDATE SET product_id = EXCLUDED.product_id;
    """
    with db_conn.cursor() as cursor:
        cursor.execute(query, (ean, product_id))
        db_conn.commit()
