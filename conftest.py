import pytest
from utils.request_util import RequestUtil

@pytest.fixture(scope="session")
def client():
    c = RequestUtil()
    # 自动登录
    resp = c.send_request("POST", "/login", json={"username": "admin", "password": "admin123"})
    body = resp.json()
    assert body["code"] == 200, f"登录失败: {body}"
    # 自动设置 token
    c.set_token(body["token"])
    return c