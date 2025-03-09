import streamlit as st
import pandas as pd
import logging
from components.table_editor import TableEditor, DfKeeper
from utils.parser_manager import load_data_for_frontend
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def page_load():
    st.set_page_config(layout="wide")

def main():
    page_load()
    st.title("Dropshipping Margin Editor")
    logging.info("Application started")

    if 'df' in st.session_state:
        df = st.session_state.df

        #modified_session_chbx = st.checkbox("Show only modified in this session", value=True, key="modified_session_chbx")
        #modified_all_chbx = st.checkbox("Show only modified in this session", value=True, key="modified_all_chbx")

        # Add a text input for searching by 'ean'
        ean_search = st.text_input("Search by EAN", "")
        if ean_search:
            displayed_df = df[df['ean'].astype(str).str.contains(ean_search, na=False)]
        else:
            displayed_df = st.session_state.df
        
        editable_columns = ['gross_price']  # modify as needed
        editor = TableEditor(dataframe=displayed_df, editable_columns=editable_columns)
        edited_df = editor.display_table()
    
        if st.session_state.get('data_updated', False):
            st.session_state.data_updated = False
            st.rerun()
    else:
        # df not loaded yet
        if st.button("Load DataFrame", key="load_dataframe"):
            logging.info("Load DataFrame button clicked")
            
            # TODO: test data implemented for now
            df = load_data_for_frontend(1)
            
            print(df)
            
            st.session_state.df = df
            st.session_state.dfkeeper = DfKeeper(df)
            logging.info("DataFrame loaded into session state")
            st.rerun()

if __name__ == "__main__":
    main()
    logging.info("Application finished")