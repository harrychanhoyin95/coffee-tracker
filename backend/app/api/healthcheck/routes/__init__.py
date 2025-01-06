from sanic import Blueprint, Request, json

healthcheck_blueprint = Blueprint('health')

@healthcheck_blueprint.route('/', methods=['GET'])
async def healthcheck(request: Request):
  return json({
    "message": "API is running!",
  })
