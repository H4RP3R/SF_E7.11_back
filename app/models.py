from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

from pydantic import BaseModel, Field, validator

from .utils.db import mongo_db, redis_db


class Comment(BaseModel):
    author: str
    text: str
    created: datetime = Field(default_factory=datetime.utcnow)

    def __str__(self):
        return f'{self.uid}|{self.author}|{self.created}'

    @validator('created')
    def check_created(cls, v):
        if v != datetime.utcnow():
            v = datetime.utcnow()
        return v

    @validator('text')
    def text_length(cls, v):
        if len(v) == 0:
            raise ValueError('Text can not be empty.')
        return v


class Ad(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    title: str
    updated: datetime = Field(default_factory=datetime.utcnow)
    text: str
    author: str
    tags: Optional[set] = None
    comments: Optional[List[Comment]] = []  # handle nested models

    def __str__(self):
        return f'{self.uid}|{self.title}|{self.updated}'

    def save(self):
        redis_db.save(str(self.dict()['uid']), self.dict())
        mongo_db.save(self.dict())

    @classmethod
    def query_all(cls):
        '''Returns all ads from the db as an Ad objects'''
        ad_objects = mongo_db.find_all(cls)
        return ad_objects

    @classmethod
    def query_one(cls, uid):
        '''Searches an ad by the uid and returns as an Ad object'''
        ad = redis_db.query_one(cls, uid) or mongo_db.find_one(cls, uid)
        return ad

    @classmethod
    def update_tags(cls, uid, key, new_data):
        mongo_db.update_tags(uid, key, new_data)
        new_data = mongo_db.find_one(cls, uid)
        redis_db.save(str(uid), new_data.dict())

    @classmethod
    def add_comment(cls, uid, comment):
        mongo_db.add_comment(uid, comment)
        new_data = mongo_db.find_one(cls, uid)
        redis_db.save(str(uid), new_data.dict())

    @validator('author')
    def author_name_length(cls, v):
        if len(v) < 3:
            raise ValueError('Author name at least 3 characters.')
        return v

    @validator('text')
    def text_length(cls, v):
        if len(v) == 0:
            raise ValueError('Text can not be empty.')
        return v

    @validator('title')
    def title_length(cls, v):
        if len(v) == 0:
            raise ValueError('Title can not be empty.')
        return v

    @validator('tags')
    def tag_length(cls, tags):
        for tag in tags:
            if not 2 <= len(tag) <= 32:
                raise ValueError('The tag must be between 2 and 32 characters long.')
        return tags
