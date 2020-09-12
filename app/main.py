from uuid import UUID

from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import Ad, Comment


app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/new_ad/')
def create_new_ad(ad: Ad):
    try:
        ad.save()
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')


@app.get('/ads/')
def ads_list():
    ads = Ad.query_all()
    return ads


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


@app.get('/ads/{uid}/statistic/')
def get_ad_statistic(uid: UUID, request: Request):
    stat_data = Ad.get_statistic(uid)
    return stat_data
