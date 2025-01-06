from sanic import Sanic
from sanic.response import text
from types import SimpleNamespace

from app.database import init_db, close_db
from app.api import healthcheck_blueprint, v1_blueprint

async def create_app() -> Sanic:
  # Initialize Sanic app with context
  app = Sanic("CoffeeTrackerAPI")
  app.ctx = SimpleNamespace()

  app.register_listener(init_db, "before_server_start")
  app.register_listener(close_db, "after_server_stop")

  # Register blueprints
  app.blueprint(healthcheck_blueprint, url_prefix="/")
  app.blueprint(v1_blueprint, url_prefix="/api/v1")

  return app
