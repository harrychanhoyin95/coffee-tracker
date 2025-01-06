from sanic import json, Request

from app.services.user_service import UserService

class UserController:
  @staticmethod
  async def get_users(request: Request):
    """Handle GET request for all users"""
    try:
      user_service = UserService(request.ctx.session)
      users = await user_service.get_users()

      return json(users, status=200)
    except Exception as e:
      return json({"error": str(e)}, status=500)

  @staticmethod
  async def get_user_by_id(request: Request, user_id: str):
    """Handle GET request for a single user"""
    try:
      user_id: int = int(user_id)
      user_service = UserService(request.ctx.session)
      user = await user_service.get_user_by_id(user_id)

      return json(user, status=200)
    except Exception as e:
      return json({"error": str(e)}, status=500)

  @staticmethod
  async def post_user(request: Request):
    try:
        email = request.json.get("email")
        user_service = UserService(request.ctx.session)
        user = await user_service.create_user(email)
        
        return json(user, status=201)
    except Exception as e:
      return json({"error": str(e)}, status=500)
