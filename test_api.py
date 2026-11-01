import pytest
import yaml
import allure
import os

def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@allure.feature("登录模块")
class TestLogin:
    @allure.story("用户登录功能测试")
    @pytest.mark.parametrize("data", load_yaml(os.path.join(BASE_DIR, "data", "login_data.yaml")))
    def test_login(self, client, data):
        allure.dynamic.title(data["case_title"])
        with allure.step("发送登录请求"):
            resp = client.send_request(
                "POST",
                "/login",
                json={"username": data["username"], "password": data["password"]}
            )
        with allure.step("断言返回结果"):
            assert resp.json()["code"] == data["expected_code"]

@allure.feature("用户管理模块")
class TestUser:
    @allure.story("查询用户列表")
    def test_user_list(self, client):
        with allure.step("发送查询请求"):
            resp = client.send_request("GET", "/users?pageNum=1&pageSize=10")
        with allure.step("断言"):
            assert resp.status_code == 200
            assert resp.json()["code"] == 200
            assert "rows" in resp.json()