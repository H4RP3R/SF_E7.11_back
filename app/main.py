from uuid import UUID

from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from models import Ad, Comment


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
        ad.check_uid()
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
    if ad:
        return {'ad': ad}
    raise HTTPException(status_code=404, detail='Not found')


@app.post('/ads/{uid}/tags/')
def update_tags(uid: UUID, tags: set, request: Request):
    try:
        error = Ad.update_tags(uid, 'tags', tags)
    except (ValidationError, AttributeError) as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')


@app.post('/ads/{uid}/comments/')
def add_comment(uid: UUID, comment: Comment, request: Request):
    try:
        Ad.add_comment(uid, comment)
    except ValidationError as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')


@app.get('/ads/{uid}/statistics/')
def get_ad_statistics(uid: UUID, request: Request):
    try:
        stat_data = Ad.get_statistics(uid)
    except AttributeError as err:
        raise HTTPException(status_code=400, detail=f'Error: {err}')
    return stat_data
