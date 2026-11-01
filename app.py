from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

TOKEN = "test-token-123"
users = [{"id": 1, "username": "admin", "phone": "13800000000"}]
next_id = 2


class LoginIn(BaseModel):
    username: str
    password: str


class UserIn(BaseModel):
    username: str
    phone: str


def check_token(authorization: Optional[str]):
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="unauthorized")


@app.post("/login")
def login(data: LoginIn):
    if data.username == "admin" and data.password == "admin123":
        return {"code": 200, "token": TOKEN, "msg": "success"}
    return {"code": 500, "msg": "用户名或密码错误"}


@app.get("/users")
def list_users(
        pageNum: int = 1,
        pageSize: int = 10,
        authorization: Optional[str] = Header(None),
):
    check_token(authorization)
    start = (pageNum - 1) * pageSize
    return {"code": 200, "rows": users[start:start + pageSize], "total": len(users)}


@app.post("/users")
def create_user(data: UserIn, authorization: Optional[str] = Header(None)):
    global next_id
    check_token(authorization)
    if not data.username:
        return {"code": 400, "msg": "用户名不能为空"}
    user = {"id": next_id, "username": data.username, "phone": data.phone}
    users.append(user)
    next_id += 1
    return {"code": 200, "data": user}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, authorization: Optional[str] = Header(None)):
    global users
    check_token(authorization)
    before = len(users)
    users = [u for u in users if u["id"] != user_id]
    if len(users) == before:
        return {"code": 404, "msg": "用户不存在"}
    return {"code": 200, "msg": "删除成功"}


@app.put("/users/{user_id}")
def update_user(user_id: int, data: UserIn, authorization: Optional[str] = Header(None)):
    check_token(authorization)

    if not data.username:
        return {"code":400, "msg": "用户名不能为空"}

    for user in users:
        if user["id"] == user_id:
            user["username"] = data.username
            user["phone"] = data.phone
            return {"code": 200, "msg": "修改成功", "data": user}

    return {"code": 404, "msg": "用户不存在"}