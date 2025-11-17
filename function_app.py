import sys
from pathlib import Path

import azure.functions as func
from azure.functions import AsgiMiddleware

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.main import app as fastapi_app

asgi = AsgiMiddleware(fastapi_app)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="FastAPIHost")
@app.route(
    route="{*segments}",
    methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
    auth_level=func.AuthLevel.ANONYMOUS,
)
def fastapi_host(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Entrypoint que entrega toda a aplicação FastAPI através do Azure Functions."""
    return asgi.handle(req, context)
