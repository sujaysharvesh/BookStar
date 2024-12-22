from fastapi import FastAPI
from app.Books.Router import router as Book_router
from app.Auth.Router import Auth_router
from app.Review.Router import review_router
from app.Tag.Router import tags_router
from contextlib import asynccontextmanager
from app.DataBase.main import init_db
from app.error import register_all_errors
from app.middleware import register_middleware
from app.DataBase.config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is Starting.....")
    await init_db()  
    yield
    print("Server is Stopping.....")

version = "v1"

app = FastAPI(
    title="BookStar",
    version=version,
    description="A REST API for a Book review web server",
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    openapi_url=f"/api/{version}/openapi.json",
    contact={
        "email": Config.MAIL_FROM 
    }
)
register_all_errors(app)

register_middleware(app)

app.include_router(Book_router, prefix=f"/api/{version}/Books", tags=["Books"])
app.include_router(Auth_router, prefix=f"/api/{version}/Auth", tags=["Auth"])
app.include_router(review_router, prefix=f"/api/{version}/Review", tags=["Review"])
app.include_router(tags_router, prefix=f"/api/{version}/Tag", tags=["Tag"])
