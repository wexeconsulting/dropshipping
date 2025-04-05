from typing import Any, List
import pandas as pd
import streamlit as st
import logging
import time
import threading
from copy import deepcopy
from utils.db import update_margin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

COLUMNS_CONFIG = {
            "gross_price": st.column_config.TextColumn("Cena sprzedaży brutto", disabled=False),
            "tax_rate": st.column_config.NumberColumn("VAT", format="percent", disabled=True),
            "price": st.column_config.NumberColumn("Cena zakupu netto", disabled=True),
            "ean": st.column_config.TextColumn("EAN", disabled=True),
            "margin": st.column_config.NumberColumn("Marża", format="percent", disabled=True),
            "name": st.column_config.TextColumn("Nazwa", disabled=True),
            "category_name": st.column_config.TextColumn("Kategoria", disabled=True),
            "quantity": st.column_config.NumberColumn("Ilość", disabled=True),
        }

def calculate_margin(gross_price, tax_rate, original_price):
    margin = (gross_price / (1+tax_rate) - original_price) / original_price
    return margin

class DfKeeper:
    def __init__(self, df):
        self.full_dataframe = deepcopy(df)
        logging.info("DfKeeper initialized")
    
    def load_dataframe(self, dataframe):
        self.full_dataframe = deepcopy(dataframe)

class TableEditor:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
        self.original_dataframe = deepcopy(self.dataframe)
        logging.info("TableEditor initialized with dataframe")

    def process_edit(self) -> None:
        logging.info("Edit")
        self.dataframe["gross_price"] = self.dataframe["gross_price"].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)
        self.original_dataframe["gross_price"] = self.original_dataframe["gross_price"].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)

        diff = self.original_dataframe[["gross_price"]].compare(self.dataframe[["gross_price"]])

        if not diff.empty:
            changed_rows = diff.index.tolist()
            changed_rows_edited = self.dataframe.loc[changed_rows]

            logging.info("Edited changed rows:\n%s", changed_rows_edited)
            logging.info("Number of changed rows: %d", len(changed_rows_edited))

            for index, row in changed_rows_edited.iterrows():
                logging.info("Processing row: %s", row)
                margin = calculate_margin(row["gross_price"], row["tax_rate"], row["price"])
                logging.info('EAN: %s', row["ean"])
                logging.info('Margin: %s', margin)
                if margin < 0:
                    st.error(f"Margin for EAN {row['ean']} is negative. Reverting changes.")
                    self.dataframe.loc[index, "gross_price"] = self.original_dataframe.loc[index, "gross_price"]
                    continue
                update_margin(1, row["ean"], margin)
                orig_df = st.session_state.dfkeeper.full_dataframe
                orig_df.loc[index, "gross_price"] = row["gross_price"]
                orig_df.loc[index, "margin"] = margin
                st.session_state.dfkeeper = DfKeeper(orig_df)
            #self.dataframe = deepcopy(self.original_dataframe)
            st.session_state.data_updated = True
            st.session_state.df = deepcopy(st.session_state.dfkeeper.full_dataframe)
        else:
            logging.info("No changes detected")

    def display_table(self):
        if not self.dataframe.empty and not isinstance(self.dataframe["gross_price"].iloc[0], str):
            self.dataframe["gross_price"] = self.dataframe["gross_price"].apply(lambda x: f"{x:,.2f}".replace(",", " ").replace(".", ","))
            max_length = self.dataframe["gross_price"].str.len().max()
            self.dataframe["gross_price"] = self.dataframe["gross_price"].apply(lambda x: x.rjust(max_length))

        self.dataframe = self.dataframe.style.format(
            {
                
                "price": lambda x : '{:,.2f}'.format(x),
            },
            thousands=' ',
            decimal=',',
        )

        edited_dataframe = st.data_editor(
            self.dataframe,
            key="data_editor",
            use_container_width=True,
            hide_index=True,
            column_config=COLUMNS_CONFIG
        )
        self.dataframe = edited_dataframe
        self.process_edit()
        logging.info("Table displayed and edited")
        return edited_dataframe