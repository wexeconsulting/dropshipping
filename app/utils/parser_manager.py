from utils.db import get_config_settings, get_margins
from utils.http_tools import send_get_request
from utils.converter import parse_xml_to_dataframe, df_processor, apply_margin_to_df, df_visualiser
from utils.xml_parser import parse_df_to_result_xml
from utils.ftp_connector import load_file_to_ftp
import os

#for testing only
from utils.xml_test import run_tests


def main_df_parser(config_id):
    name, settings, url = get_config_settings(config_id)
    default_margin = settings.get("default_margin", 0.2)
    margins_dict = get_margins(config_id)
    payload = send_get_request(url)
    df = parse_xml_to_dataframe(payload, settings)
    df = df_processor(df)
    df = apply_margin_to_df(df, margins_dict, default_margin)
    return df

def load_data_for_frontend(config_id):
    df = main_df_parser(config_id)
    df = df_visualiser(df)
    return df

def run_batch_task(config_id):
    df = main_df_parser(config_id)
    result_xml = parse_df_to_result_xml(df)
    file_path = f"xml_result_{config_id}.xml"
    with open(file_path, "w") as file:
        file.write(result_xml)
    
    run_tests()

    HOST = os.getenv("FTP_HOST")
    USER = os.getenv("FTP_USERNAME")
    PASSWORD = os.getenv("FTP_PASSWORD")

    load_file_to_ftp(file_path, HOST, USER, PASSWORD)
    #os.remove(file_path)