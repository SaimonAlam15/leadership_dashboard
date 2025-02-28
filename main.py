import streamlit as st
from dashboard import dashboard

def main():
    # st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Leadership Dashboard</h1>", unsafe_allow_html=True)
    dashboard()

if __name__ == '__main__':
    main()
