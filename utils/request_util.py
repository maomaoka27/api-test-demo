import requests
import logging

BASE_URL = "http://127.0.0.1:8000"

class RequestUtil:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def send_request(self, method, url, **kwargs):
        full_url = BASE_URL + url
        logging.info(f"发送请求: {method} {full_url}, 参数: {kwargs}")
        response = self.session.request(method, full_url, timeout=5, **kwargs)
        logging.info(f"收到响应: 状态码 {response.status_code}, 内容 {response.text}")
        return response

    def set_token(self, token):
        self.session.headers.update({"Authorization": f"Bearer {token}"})