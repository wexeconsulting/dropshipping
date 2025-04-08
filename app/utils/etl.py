from utils.http_tools import send_get_request
import xml.etree.ElementTree as ET
from utils.db import insert_or_update_product_ids

def import_product_ids(config: dict):
    url = config["url"]
    # url = "https://panel-e.baselinker.com/inventory_export.php?hash=2842f5bb1c19498c5cfa69f0216b94be"
    response = send_get_request(url)
    root = ET.fromstring(response)
    ean_product_id_list = []
    for product in root.findall('product'):
        product_id = product.find('product_id').text
        ean = product.find('ean').text
        ean_product_id_list.append((ean, product_id))
    
    for ean, product_id in ean_product_id_list:
        insert_or_update_product_ids(ean, product_id)


def run_etl_task(name, parameters):
    if name == "ETL_import_product_ids":
        import_product_ids(parameters)