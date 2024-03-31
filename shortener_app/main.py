import secrets

import validators
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from starlette.datastructures import URL
from starlette.responses import RedirectResponse

from shortener_app import schemas, models, crud
from shortener_app.database import engine, SessionLocal

from .config import getSettings

app = FastAPI()
models.Base.metadata.create_all(
    bind=engine)  # This line will create all models in database if they are not already created at first run


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)


@app.get("/")
def readRoot():
    return "Welcome to the URL shortener API"


@app.get("/{url_key}")
def forward_to_url(url_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_key(db, url_key):
        crud.update_db_clicks(db, db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@app.get("/admin/{secret_key}", name="Administration Info", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


@app.post("/url", response_model=schemas.URLInfo)
def createUrl(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request('Your provided URL is not valid')

    db_url = crud.create_db_url(db, url)
    return get_admin_info(db_url)

@app.delete("/admin/{secret_key}")
def delete_url(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)

def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(getSettings().base_url)
    admin_url = app.url_path_for("Administration Info", secret_key=db_url.secret_key)
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_url))
    return db_url
