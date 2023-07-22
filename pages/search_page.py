import streamlit as st

from common.es_util import es

search_text = st.text_input('输入搜索内容')
search_text = search_text.strip()
if not search_text:
    st.stop()


result = es.search(index="web_info_2023_07_16", body={
    "size": 300,
    "query": {
        "bool": {
            "should": [
                {
                    "match": {
                        "content": search_text
                    }
                }, {
                    "match": {
                        "title": {
                            "query": search_text,
                            "operator": "and",
                            "boost": 2,
                        },

                    }
                }
            ]
        }
    },
    "_source": ["title", "url", "_id"],
    "highlight": {
        "fields": {
            "content": {},
            "title": {}
        }
    }
})

result_data = result["hits"]["hits"]

show_data = []
for data in result_data:
    show_data.append({
        "id": data["_id"],
        "title": data["highlight"]["title"][0] if "title" in data["highlight"] else data["_source"]["title"],
        "url": data["_source"]["url"],
        "content": data["highlight"]["content"][0] if "content" in data["highlight"] else data["_source"]["content"],
    })

# st.write(result)

# 设置每页显示的数据数量
items_per_page = 100

# 计算总页数
total_pages = len(show_data) // items_per_page + 1

# 获取当前页码
current_page = st.slider('选择页码', 1, total_pages)

# 计算当前页的起始和结束索引
start = (current_page - 1) * items_per_page
end = start + items_per_page

# 获取当前页的数据
current_page_data = show_data[start:end]

# 显示当前页的数据
idx = start
for item in current_page_data:
    title_html = str(idx + 1) + ". " + item["title"]
    # 标题h3, 修改em标签的样式，红色、加粗，取消斜体
    title_html = f"<h3>{title_html}</h3>"
    st.markdown(title_html.replace("<em>", "<em style='color:red;font-weight:bold;font-style:normal'>"),
                unsafe_allow_html=True)

    url = "http://192.168.31.148:9140/mirror_web/get/" + item["id"]
    st.write(url)
    # st.write("content:", item["content"])

    # st.markdown(item["content"], unsafe_allow_html=True)
    # 修改em标签的样式，红色、加粗，取消斜体
    st.markdown(item["content"].replace("<em>", "<em style='color:red;font-weight:bold;font-style:normal'>"),
                unsafe_allow_html=True)

    st.write("--------------------------------------------------")
    idx += 1
