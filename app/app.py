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

        checkbox_state = st.checkbox("Show only modified margins", value=False, key="checkbox_modified")
        if checkbox_state != st.session_state.get('checkbox_modified', False):
            st.session_state.checkbox_modified = checkbox_state
            st.rerun()

        #modified_session_chbx = st.checkbox("Show only modified in this session", value=True, key="modified_session_chbx")
        #modified_all_chbx = st.checkbox("Show only modified in this session", value=True, key="modified_all_chbx")

        # Add a text input for searching by 'ean'
        ean_search = st.text_input("Search by EAN", "")
        displayed_df = st.session_state.df

        if ean_search:
            displayed_df = displayed_df[displayed_df['ean'].astype(str).str.contains(ean_search, na=False)]
        
        if st.session_state.checkbox_modified:
            displayed_df = displayed_df[displayed_df['margin'] != 0.2]
        
        
        editable_columns = ['gross_price']  # modify as needed
        editor = TableEditor(dataframe=displayed_df, editable_columns=editable_columns)
        edited_df = editor.display_table()
    
        if st.session_state.get('data_updated', False):
            st.session_state.data_updated = False
            st.rerun()

    if 'df' not in st.session_state:
        st.write("Loading data...")
        if 1==1:
            logging.info("Loading dataframe at init")
            
            # TODO: test data implemented for now
            df = load_data_for_frontend(1)
            
            st.session_state.df = df
            st.session_state.dfkeeper = DfKeeper(df)
            logging.info("DataFrame loaded into session state")
            st.rerun()

if __name__ == "__main__":
    main()
    logging.info("Application finished")