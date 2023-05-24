// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        *://*/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=bandwagonhost.com
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    let insertHtml = `
    <div id="ext_container">
        <button id="sub_btm">submit mirror</button>
        <style>
            #ext_container {
                position: fixed;
                top: 10px;
                right: 10px;
            }
        </style>
    </div>
    `
    document.body.insertAdjacentHTML("beforeend", insertHtml)
    document.getElementById("sub_btm").addEventListener("click", function () {
        console.log("click");
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:5000/mirror_web/submit_html", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText);    // 获取响应文本
                console.log(xhr.responseXML);    // 获取响应 XML
            }
        };
        xhr.send(JSON.stringify({
            "url": window.location.href,
            "html": document.documentElement.outerHTML
        }));
        let html = document.documentElement.outerHTML;
    }, false);

})();