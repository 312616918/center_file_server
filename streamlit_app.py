import streamlit as st
from pandas import DataFrame

from web_mirror.service import html_service

x = st.slider("Select a value")
st.write(x, "squared is", x * x)

info_list = html_service.get_all_web_info()
info_data = []


def to_a_tag(text, url):
    return '<a href="{}" target="_blank">{}</a>'.format(url, text)


for info in info_list:
    mirror_url = "http://localhost:5000/mirror_web/get/" + info["id"]
    info_data.append({
        "title": info["title"],
        "url": to_a_tag(info["url"], info["url"]),
        "mirror_url": to_a_tag(mirror_url, mirror_url),
    })

df = DataFrame(info_data)
st.write(df.to_html(escape=False), unsafe_allow_html=True)
