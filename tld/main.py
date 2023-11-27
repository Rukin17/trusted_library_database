
import uvicorn

from fastapi import FastAPI
from fastapi.routing import APIRouter
from tld.handlers.handlers import user_router
from tld.handlers.login_handler import login_router


from . import models
from tld.db import engine


models.Base.metadata.create_all(bind=engine)


app = FastAPI()

main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix='/user', tags=['user'])
main_api_router.include_router(login_router, prefix='/login', tags=['login'])

app.include_router(main_api_router)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

