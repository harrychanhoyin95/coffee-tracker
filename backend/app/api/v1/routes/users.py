from sanic import Blueprint, json, Request
from sqlalchemy import select

from app.models.user import User

users_v1 = Blueprint('users', url_prefix='/users')

@users_v1.route('/', methods=['GET'])
async def get_users(request: Request):
  try:
    session = request.ctx.session
    async with session.begin():
      stmt = select(User)
      users = await session.execute(stmt)
      user_list = [
          {
            "id": user.id,
            "email": user.email,
            "created_at": str(user.created_at),
            "updated_at": str(user.updated_at)
          }
          for user in users.scalars().all()
      ]
    return json(user_list)
  except Exception as e:
    return json({"error": str(e)}, status=500)

@users_v1.route('/', methods=['POST'])
async def post_user(request: Request):
  try:
    session = request.ctx.session
    async with session.begin():
      email = request.json.get("email")
      user = User(email=email)
      session.add(user)
      await session.flush()
      await session.refresh(user)

      user_dict = {
          "id": user.id,
          "email": user.email,
          "created_at": str(user.created_at),
          "updated_at": str(user.updated_at)
      }
    return json(user_dict, status=201)
  except Exception as e:
    return json({"error": str(e)}, status=500)
