from worksystem.modules.users.definitions import User
from worksystem import mongo
from werkzeug.security import generate_password_hash,check_password_hash
import time

def verify_unexist(itcode):
    result = mongo.db.student.find_one(
        {
            "itcode": itcode
        }
    )
    return {
        "code": 1,
        "msg": "认证成功",
    } if result is None else {
        "code": 0,
        "msg": "该用户已注册，邮件发送失败"
    }

# 验证用户是否存在
def verify_exist(itcode):
    result = mongo.db.student.find_one(
        {
            "itcode": itcode
        }
    )
    return {
        "code": 1,
        "msg": "认证成功",
        "data": {
            "email": result["itcode"],
            "memberIsExist": "邮件发送成功"
        }
    } if result else {
        "code": 0,
        "msg": "邮件发送失败"
    }


def verify_register(itcode, password):
    mongo.db.student.create_index("itcode", unique=True)
    result = mongo.db.student.find_one(
        {
            "itcode": itcode
        }
    )
    if result:
        return {
            "code": 0,
            "msg": "用户注册失败"
        }
    mongo.db.student.insert(
        {
            "itcode": itcode,
            "email": itcode+('@sugon.com'),
            "status": 'active',
            "password": generate_password_hash(password),
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "user_roles": [],
            "manage_roles": []
        }
    )
    return {
        "code": 1,
        "msg": "用户注册成功"
    }


def verify_login(itcode, password):
    result = mongo.db.student.find_one(
        {
            "itcode": itcode
        }
    )
    if result:
        if result["status"] == "forbidden":
            return {
                "code": 3,
                "msg": "账号已被禁用"
            }
        if not check_password_hash(result['password'],password):
            return {
                "code": 0,
                "msg": "密码错误"
            }
        # password_form = generate_password_hash(password_form)
        # itcode = User.get_itcode(itcode_form)
        # if itcode_form.check_password_hash(password_form):
        return {
            "code": 1,
            "msg": "登陆成功",
            "result": {
                "_id": result["_id"],
                "itcode": result["itcode"],
                "password": result["password"],
                "email": result["email"]
            }
        }
        # else:
        #     return {
        #         "code":0,
        #         "msg":'密码错误'
        #     }
    else:
        return {
            "code": 2,
            "msg": "用户不存在"
        }


def verify_reset(itcode,password):
    result = mongo.db.student.update_one(
        {
            "itcode": itcode
        },
        {
            "$set": {"password": generate_password_hash(password)}
        }
    )
    print(result.matched_count)
    print(result.modified_count)
    if result:
        return{
            "code": 1,
            "msg": "密码修改成功"
        }
    else:
        return {
            "code": 0,
            "msg": '密码修改失败'
        }
