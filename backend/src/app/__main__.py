import uvicorn

from app.main import app
from app.settings import Settings

listen_address = Settings().listen_address
uvicorn.run(app, host=str(listen_address.host), port=listen_address.port)
