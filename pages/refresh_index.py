import streamlit as st
import time

from web_mirror.service.refresh_es_index import refresh_web_info

if st.button("Start progress"):
    progress_text = st.empty()
    my_bar = st.progress(0)


    def callback(idx, size):
        pro = int(idx / size * 100)
        my_bar.progress(pro, text=f"{idx}/{size}={pro}%")


    refresh_web_info(callback)

    progress_text.text("Done!")
