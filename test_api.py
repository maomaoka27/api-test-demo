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

    @allure.story("修改用户")
    @allure.title("正常修改用户信息")
    def test_update_user_success(self, client):
        with allure.step("前置操作：创建一个新用户"):
            payload = {"username": "old_name", "phone": "11111111111"}
            create_resp = client.send_request("POST", "/users", json=payload)
            user_id = create_resp.json()["data"]["id"]

        with allure.step("发送修改请求"):
            update_payload = {"username": "new_name", "phone": "22222222222"}
            update_resp = client.send_request("PUT", f"/users/{user_id}", json=update_payload)

        with allure.step("断言修改成功"):
            body = update_resp.json()
            assert body["code"] == 200
            assert body["data"]["username"] == "new_name"

    @allure.story("修改用户")
    @allure.title("修改不存在的用户")
    def test_update_not_exist_user(self, client):
        with allure.step("发送修改请求，ID传9999"):
            update_payload = {"username": "xxx", "phone": "222"}
            update_resp = client.send_request("PUT", "/users/9999", json=update_payload)

        with allure.step("断言返回 404"):
            assert update_resp.json()["code"] == 404

    @allure.story("修改用户")
    @allure.title("修改用户-异常参数测试(数据驱动)")
    @pytest.mark.parametrize("update_data, expected_code", [
        ({"username": "", "phone": "222"}, 400),                 # 用户名为空
        ({"username": "a" * 50, "phone": "222"}, 200),           # 超长用户名 (为了看你接口会不会崩溃)
        ({"username": "正常名", "phone": "我是手机号"}, 200)        # 手机号传中文 (测试后端是否有格式校验)
    ])
    def test_update_user_abnormal(self, client, update_data, expected_code):
        with allure.step("前置操作：创建一个新用户"):
            create_resp = client.send_request("POST", "/users", json={"username": "tmp", "phone": "111"})
            user_id = create_resp.json()["data"]["id"]

        with allure.step(f"发送修改请求，参数: {update_data}"):
            # 这里如果用户名是空，我们的 app.py 里没写拦截，所以我们需要去看看它返回什么
            resp = client.send_request("PUT", f"/users/{user_id}", json=update_data)

        with allure.step("断言返回结果"):
            assert resp.json()["code"] == expected_code