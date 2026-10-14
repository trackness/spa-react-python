import uvicorn

from app.main import app
from app.settings import Settings

settings = Settings()
uvicorn.run(
    app, host=str(settings.listen_address.host), port=settings.listen_address.port
)
