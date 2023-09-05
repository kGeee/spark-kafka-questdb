import streamlit as st

st.set_page_config(
    page_title="Datafeeds",
    page_icon="👋",
)

st.write("# Welcome to Datafeeds! 👋")
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        .css-zq5wmm {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown(
    """
    Check around the different pages
"""
)