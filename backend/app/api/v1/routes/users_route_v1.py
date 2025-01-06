from sanic import Blueprint, json, Request

from app.api.v1.controllers.users_controller_v1 import UserController

users_v1 = Blueprint('users', url_prefix='/users')

@users_v1.route('/', methods=['GET'])
async def get_users(request: Request):
  return await UserController.get_users(request)

@users_v1.route('/<user_id>', methods=['GET'])
async def get_user_by_id(request: Request, user_id: str):
  return await UserController.get_user_by_id(request, user_id)

@users_v1.route('/', methods=['POST'])
async def post_user(request: Request):
  return await UserController.post_user(request)
