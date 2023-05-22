from playwright.sync_api import sync_playwright


class WebEngine():
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def get_info(self, url):
        try:
            self.page.goto(url)
        except Exception as e:
            print(e)
        title = self.page.title()
        html = self.page.content()
        screenshot = self.page.screenshot(full_page=True)
        return {
            "title": title,
            "html": html,
            "screenshot": screenshot
        }

    def close(self):
        self.browser.close()
        self.p.stop()
        self.browser = None

    def __del__(self):
        if self.browser is not None:
            self.close()


if __name__ == '__main__':
    engine = WebEngine()
    print(engine.get_info("https://blog.csdn.net/Mr_Gaojinchao/article/details/127872647"))
