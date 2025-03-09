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

    def display_error_message(self, message: str, duration: int = 2) -> None:
        error_placeholder = st.empty()
        error_placeholder.error(message)
        
        def remove_error():
            time.sleep(duration)
            error_placeholder.empty()
        
        threading.Thread(target=remove_error).start()

    def process_edit(self) -> None:
        logging.info("Edit")
        # Compare the updated self.dataframe (updated via display_table) with the original dataframe.
        diff = self.original_dataframe.compare(self.dataframe)

        if not diff.empty:
            changed_rows = diff.index.tolist()
            changed_rows_edited = self.dataframe.loc[changed_rows]

            logging.info("Edited changed rows:\n%s", changed_rows_edited)

            for index, row in changed_rows_edited.iterrows():
                logging.info("Processing row: %s", row)
                margin = calculate_margin(row["gross_price"], row["tax_rate"], row["price"])
                if margin < 0:
                    self.display_error_message("Margin cannot be below 0")
                    row["gross_price"] = row["price"] * (1+row["margin"]) * (1 + row["tax_rate"])
                    continue
                logging.info('EAN: %s', row["ean"])
                logging.info('Margin: %s', margin)
                update_margin(1, row["ean"], margin)
                orig_df = st.session_state.dfkeeper.full_dataframe
                orig_df.loc[index, "gross_price"] = row["gross_price"]
                orig_df.loc[index, "margin"] = margin
                st.session_state.dfkeeper = DfKeeper(orig_df)
            self.dataframe = deepcopy(self.original_dataframe)
            st.session_state.data_updated = True
            st.session_state.df = deepcopy(st.session_state.dfkeeper.full_dataframe)
        else:
            logging.info("No changes detected")
        # Update the original dataframe for further diffing.

    def display_table(self):
        # Build column config to only allow editing for columns in editable_columns.
        column_config = {}
        for col in self.dataframe.columns:
            if col in self.editable_columns:
                column_config[col] = {"disabled": False}
            else:
                column_config[col] = {"disabled": True}
        # Remove the on_change callback.
        edited_dataframe = st.data_editor(
            self.dataframe,
            key="data_editor",
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        # Update the instance variable with the edited dataframe.
        self.dataframe = edited_dataframe
        # Manually call the process_edit method to detect changes.
        self.process_edit()
        logging.info("Table displayed and edited")
        return edited_dataframe