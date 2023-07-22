import json
from urllib.parse import urljoin

from flask import Flask, request, render_template_string
from flask_cors import CORS

from web_mirror.service import html_service

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/mirror_web/submit', methods=['POST'])
def mirror_web_submit():
    req_data = request.json
    url = req_data["url"]
    result = html_service.save_web_from_engine(url)
    resp_obj = {
        "web_id": result
    }
    return resp_obj


@app.route('/mirror_web/submit_html', methods=['POST'])
def mirror_web_submit_html():
    req_data = request.json
    result = html_service.save_web_by_html(req_data)
    resp_obj = {
        "web_id": result
    }
    return resp_obj


@app.route('/mirror_web/check_mirrored', methods=['POST'])
def mirror_web_check_url_mirrored():
    result = html_service.check_mirrored(request.json)
    resp_obj = {
        "mirrored": result
    }
    return resp_obj


@app.route('/mirror_web/get/<web_id>')
def mirror_web_get(web_id):
    req_url = request.url
    base_url = req_url.removesuffix("/mirror_web/get/" + web_id)
    html = html_service.get_html_by_web_id(web_id, urljoin(base_url, "/mirror_web/get_src/"))
    # html = html_service.get_html_by_web_id(web_id, "/mirror_web/get_src/")
    return render_template_string(html)

@app.route('/mirror_web/get_src/<path:file_url>')
def mirror_web_get_src(file_url):
    return html_service.get_src_content(file_url)


@app.route('/mirror_web/list')
def mirror_web_list():
    info_list = html_service.get_all_web_info()
    for info in info_list:
        info["mirror_url"] = "/mirror_web/get/" + info["id"]
    return {
        "data": info_list
    }


if __name__ == '__main__':
    app.run()
