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

    @allure.story("分页查询用户列表")
    @allure.title("正常分页查询")
    def test_user_list_normal(self, client):
        with allure.step("请求第一页，每页10条"):
            resp = client.send_request("GET", "/users?pageNum=1&pageSize=10")
        with allure.step("断言"):
            assert resp.status_code == 200
            assert resp.json()["code"] == 200
            assert "rows" in resp.json()

    @allure.story("分页查询用户列表")
    @allure.title("分页参数边界测试-pageSize超大")
    def test_user_list_large_page(self, client):
        with allure.step("请求每页1000条"):
            resp = client.send_request("GET", "/users?pageNum=1&pageSize=1000")
        with allure.step("断言系统能正常处理不崩溃"):
            assert resp.status_code == 200

    @allure.story("分页查询用户列表")
    @allure.title("不带Token访问用户列表(鉴权测试)")
    def test_user_list_no_token(self):
        # 这里我们故意不用 client，直接用 requests 发请求
        import requests
        with allure.step("发送无Token请求"):
            resp = requests.get("http://127.0.0.1:8000/users")
        with allure.step("断言返回 401 未授权"):
            assert resp.status_code == 401

    @allure.story("新增用户")
    @allure.title("正常新增用户")
    def test_create_user_success(self, client):
        with allure.step("发送新增用户请求"):
            payload = {"username": "test_user_01", "phone": "13912345678"}
            resp = client.send_request("POST", "/users", json=payload)
        with allure.step("断言新增成功并返回ID"):
            assert resp.status_code == 200
            assert resp.json()["code"] == 200
            assert "id" in resp.json()["data"]

    @allure.story("新增用户")
    @allure.title("新增用户-用户名为空(异常测试)")
    def test_create_user_empty_username(self, client):
        with allure.step("发送用户名为空的请求"):
            payload = {"username": "", "phone": "13912345678"}
            resp = client.send_request("POST", "/users", json=payload)
        with allure.step("断言返回业务错误码 400"):
            # 这里要注意，我们的app.py里写了如果username为空，返回code 400
            assert resp.json()["code"] == 400

    @allure.story("删除用户")
    @allure.title("删除不存在的用户")
    def test_delete_not_exist_user(self, client):
        with allure.step("请求删除一个不存在的用户ID (9999)"):
            resp = client.send_request("DELETE", "/users/9999")
        with allure.step("断言返回 404 用户不存在"):
            assert resp.json()["code"] == 404