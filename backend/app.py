from dotenv import load_dotenv
from sanic.log import logger
import os
import asyncio

from app import create_app

# Load environment variables
load_dotenv()

# Environment variables
port = int(os.getenv("PORT", 8000))
is_dev = os.getenv("ENVIRONMENT", "development") == "development"

app = asyncio.run(create_app())

if __name__ == '__main__':
  logger.info(f"Starting server on port: {port}")
  app.run(
    host="0.0.0.0",
    port=port,
    dev=is_dev
  )
