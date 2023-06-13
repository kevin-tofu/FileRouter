import os, sys
sys.path.append(f"{os.pardir}/filerouter/")

from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

import router
from config import config_org

from logconf import mylogger
logger = mylogger(__name__)


app = FastAPI()
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    # allow_credentials=False,
    allow_methods=["*"],
    # allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

serverinfo = {
    "version": config_org.app_version,
    "author": config_org.app_author
}

@app.get("/")
def root():
    return serverinfo

app.include_router(router.test_router)

if __name__ == "__main__":

    import uvicorn
    import argparse

    myport = config_org.app_port
    logger.info(f"myport: {myport}")
    logger.info(f"config.PATH_DATA : {config_org.app_data_path}")

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-P', type=int, default=myport, help='port for http server')
    args = parser.parse_args()

    uvicorn.run('server:app', host="0.0.0.0", port=args.port)