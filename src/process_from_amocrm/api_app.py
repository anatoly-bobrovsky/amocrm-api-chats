"""API App entry point."""

import uvicorn
from fastapi import FastAPI

from env_settings import env
from routers import amocrm_router

app = FastAPI(
    title="amoCRM Webhook URL",
)

app.include_router(amocrm_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile=env.SSL_KEYFILE, ssl_certfile=env.SSL_CERTFILE)
