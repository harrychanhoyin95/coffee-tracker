from sanic import Sanic, Request
from sanic.log import logger
from sanic.response import text
from sanic.exceptions import ServerError
from types import SimpleNamespace

from app.database import init_db, close_db
from app.api import v1_blueprint

async def create_app():
  # Initialize Sanic app with context
  app = Sanic("CoffeeTrackerAPI")
  app.ctx = SimpleNamespace()

  app.register_listener(init_db, "before_server_start")

  app.register_listener(close_db, "after_server_stop")
    
  app.get("/")
  async def root(request: Request):
    return text("Hello World!")

  # Register blueprints
  app.blueprint(v1_blueprint, url_prefix="/api/v1")

  return app
