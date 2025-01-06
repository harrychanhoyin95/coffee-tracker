from sanic import Blueprint, json, Request
from sqlalchemy import select

from app.services.user_service import UserService

users_v1 = Blueprint('users', url_prefix='/users')

@users_v1.route('/', methods=['GET'])
async def get_users(request: Request):
  try:
    user_service = UserService(request.ctx.session)
    users = await user_service.get_users()

    return json(users, status=200)
  except Exception as e:
    return json({"error": str(e)}, status=500)

@users_v1.route('/', methods=['POST'])
async def post_user(request: Request):
  try:
      email = request.json.get("email")
      user_service = UserService(request.ctx.session)
      user = await user_service.create_user(email)
      
      return json(user, status=201)
  except Exception as e:
    return json({"error": str(e)}, status=500)
