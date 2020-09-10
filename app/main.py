from uuid import UUID

from fastapi import FastAPI, Request, HTTPException
from pydantic import ValidationError

from .models import Ad, Comment


app = FastAPI()


@app.post('/new_ad/')
def create_new_ad(title: str, text: str, author: str, tags: set):
    try:
        ad = Ad(title=title, text=text, author=author, tags=tags)
        ad.save()
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')


@app.get('/ads/')
def ads_list():
    ads = Ad.query_all()
    return {'ads': ads}


@app.get('/ads/{uid}')
def single_ad(uid: UUID, request: Request):
    ad = Ad.query_one(uid)
    return {'ad': ad}


@app.post('/ads/{uid}')
def update_tags(uid: UUID, tags: set, request: Request):
    try:
        Ad.update_tags(uid, 'tags', tags)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')


@app.post('/ads/{uid}/comments/')
def add_comment(uid: UUID, comment: Comment, request: Request):
    try:
        Ad.add_comment(uid, comment)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')
