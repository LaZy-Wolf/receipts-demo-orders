from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker

from .auth import require_api_key
from .config import Settings
from .db import Base, make_engine
from .errors import DomainError
from .routers import coupons, customers, orders, products


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)

    app = FastAPI(title="orders-service", version="2.3.0")
    app.state.settings = settings
    app.state.sessionmaker = sessionmaker(bind=engine, expire_on_commit=False)

    @app.exception_handler(DomainError)
    def domain_error(request: Request, exc: DomainError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    protected = [Depends(require_api_key)]
    for module in (products, customers, coupons, orders):
        app.include_router(module.router, dependencies=protected)
    return app


def __getattr__(name):
    # `uvicorn orders.main:app` builds the app lazily so importing this module has no side effects.
    if name == "app":
        return create_app()
    raise AttributeError(name)
