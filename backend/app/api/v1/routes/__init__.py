from sanic import Blueprint

from app.api.v1.routes.users import users_v1

v1_blueprint = Blueprint.group(
  users_v1,
)