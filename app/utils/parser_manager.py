from utils.db import get_config_settings, get_margins
from utils.http_tools import send_get_request
from utils.converter import parse_xml_to_dataframe, df_processor, apply_margin_to_df, df_visualiser
from utils.xml_parser import parse_df_to_result_xml
from utils.ftp_connector import load_file_to_ftp
from utils.logger import get_technical_logger, get_user_logger
import os

#for testing only
from utils.xml_test import run_tests

logger = get_technical_logger(__name__)
user_logger = get_user_logger(__name__)


def main_df_parser(config_id):
    name, settings, url = get_config_settings(config_id)
    default_margin = settings.get("defaultMargin", 0.2)
    logger.debug(f"Parsing data for config: {name}, default_margin: {default_margin}")
    margins_dict = get_margins(config_id)
    logger.debug(f"Loaded {len(margins_dict)} custom margins")
    payload = send_get_request(url)
    df = parse_xml_to_dataframe(payload, settings)
    logger.debug(f"Parsed XML to dataframe: {len(df)} rows")
    df = df_processor(df)
    df = apply_margin_to_df(df, margins_dict, default_margin)
    logger.info(f"Processed {len(df)} products for config_id={config_id}")
    return df

def load_data_for_frontend(config_id):
    df = main_df_parser(config_id)
    df = df_visualiser(df)
    return df

def run_batch_task(config_id):
    logger.info(f"Starting batch task for config_id: {config_id}")
    df = main_df_parser(config_id)
    logger.debug(f"Generating XML output for {len(df)} products")
    result_xml = parse_df_to_result_xml(df)
    file_path = f"xml_result_{config_id}.xml"
    with open(file_path, "w") as file:
        file.write(result_xml)
    logger.debug(f"XML written to {file_path}")
    
    run_tests()

    HOST = os.getenv("FTP_HOST")
    USER = os.getenv("FTP_USERNAME")
    PASSWORD = os.getenv("FTP_PASSWORD")

    load_file_to_ftp(file_path, HOST, USER, PASSWORD)
    logger.info(f"Batch task completed for config_id: {config_id}")
    #os.remove(file_path)