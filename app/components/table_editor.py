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
    def __init__(self, dataframe: pd.DataFrame, editable_columns: List[str]):
        self.dataframe = dataframe
        self.original_dataframe = deepcopy(self.dataframe)
        self.editable_columns = editable_columns
        logging.info("TableEditor initialized with dataframe")

    def process_edit(self) -> None:
        logging.info("Edit")
        # Compare the updated self.dataframe (updated via display_table) with the original dataframe.
        self.dataframe["gross_price"] = self.dataframe["gross_price"].str.replace(" ", "").str.replace(",", ".").astype(float)
        diff = self.original_dataframe.compare(self.dataframe)

        if not diff.empty:
            changed_rows = diff.index.tolist()
            changed_rows_edited = self.dataframe.loc[changed_rows]

            logging.info("Edited changed rows:\n%s", changed_rows_edited)

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
        # Update the original dataframe for further diffing.

    def display_table(self):
        # Build column config to only allow editing for columns in editable_columns.
        if type(self.dataframe["gross_price"][0]) != str:
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
        column_config = {
            "gross_price": st.column_config.TextColumn("Cena brutto", disabled=False),
            #"gross_price": st.column_config.NumberColumn("Cena dostawcy", disabled=False),
            "tax_rate": st.column_config.NumberColumn("VAT", format="percent", disabled=True),
            "price": st.column_config.NumberColumn("Cena dostawcy", disabled=True),
            "ean": st.column_config.TextColumn("EAN", disabled=True),
            "margin": st.column_config.NumberColumn("Marża", format="percent", disabled=True),
            "name": st.column_config.TextColumn("Nazwa", disabled=True),
            "category_name": st.column_config.TextColumn("Kategoria", disabled=True),
            "quantity": st.column_config.NumberColumn("Ilość", disabled=True),
        }

        edited_dataframe = st.data_editor(
            self.dataframe,
            key="data_editor",
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        self.dataframe = edited_dataframe
        self.process_edit()
        # if "error_msg" in st.session_state and st.session_state.error_msg:
        #    st.error(st.session_state.error_msg)
        logging.info("Table displayed and edited")
        return edited_dataframe