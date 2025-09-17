from utils.xml_parser import parse_xml_to_dict
import pandas as pd
import json
from utils.db import get_product_ids

def parse_xml_to_dataframe(xml_content, mapping):
    return pd.DataFrame(parse_xml_to_dict(xml_content, mapping))

def load_json_file_as_df(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        data = json.load(file)
    return pd.DataFrame(data)

def parse_tax_rate(tax_rate):
    tax_rate = tax_rate.replace(",", ".")
    tax_rate = tax_rate.replace("%", "")
    tax_rate = float(tax_rate)
    if tax_rate > 1:
        tax_rate = tax_rate / 100
    
    return tax_rate

def df_processor(df):
    df["price"] = df["price"].str.replace("zł", "").str.replace("\xa0", "").str.replace(",", ".").str.strip()
    df["price"] = df["price"].astype(float)
    df["quantity"] = df["quantity"].astype(int)
    #df = df[df["quantity"].notnull() & (df["quantity"] > 0)]
    df = df[df["price"].notnull()].copy()
    df["ean"] = df["ean"].astype(str)
    df["tax_rate"] = df["tax_rate"].apply(parse_tax_rate)
    prod_ids = get_product_ids()
    df["product_id"] = df["ean"].map(prod_ids)
    return df

def apply_margin_to_df(df, margin_dict, default_margin):
    df['margin'] = df['ean'].apply(lambda ean: margin_dict.get(ean, default_margin))
    df["gross_price"] = (df["price"] * (1 + df["margin"]) * (1 + df["tax_rate"])).round(2)
    return df

def df_visualiser(df):
    columns_to_keep = ["name", "ean", "category_name", "quantity", "price", "tax_rate", "margin", "gross_price"]
    df = df[columns_to_keep]
    # initialize columns for frontend
    #df['modified'] = False
    return df
