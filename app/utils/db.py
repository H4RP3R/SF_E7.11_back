import os
import pickle
import logging
from datetime import datetime
from uuid import uuid4

import pymongo
import redis

from utils.typecodecs import codec_options


MONGO_PORT = os.environ['MONGO-PORT']
MONGO_HOST = os.environ['MONGO_HOST']

REDIS_CONFIG = {
    'host':  os.environ['REDIS_HOST'],
    'port': os.environ['REDIS_PORT'],
    'db': 0,
}


logger = logging.getLogger('db-logger')
logger.setLevel(logging.DEBUG)
logging.debug('')


class MongoDb:

    def __init__(self):
        client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')
        db = client['addb']
        self.ads_collection = db.get_collection('ads_collection', codec_options=codec_options)

    def save(self, ad):
        self.ads_collection.insert(ad)
        logger.debug(' INSERT DATA INTO MONGO')

    def find_all(self, cls):
        cursor = self.ads_collection.find({})
        ad_objects = []
        try:
            for c in cursor:
                c.pop('_id')
                obj = cls(**c)
                ad_objects.append(obj)
        except:
            pass
        return ad_objects

    def find_one(self, cls, uid):
        ad = self.ads_collection.find_one({'uid': uid})
        if not ad:
            return None
        ad.pop('_id')
        logger.debug(' FIND ONE IN MONGO')
        try:
            return cls(**ad)
        except:
            return None

    def update_tags(self, uid, key, new_data):
        acknowledged = self.ads_collection.update_one({'uid': uid}, {'$set': {key: new_data,
                                                                              'updated': datetime.utcnow()}})
        if acknowledged.modified_count:
            logger.debug(' UPDATE TAGS IN MONGO')

    def add_comment(self, uid, comment):
        comment.created = datetime.utcnow()
        self.ads_collection.update_one({'uid': uid}, {'$push': {'comments': dict(comment)}})
        logger.debug(' SAVE COMMENT IN MONGO')

    def get_statistic(self, cls, uid):
        '''Returns dict with two keys: tags_num, comments_num'''
        logger.debug(' GET STATISTICS FROM MONGO')
        ad = self.find_one(cls, uid)
        tags_num, comments_num = len(ad.tags), len(ad.comments)
        return {'tags_num': tags_num, 'comments_num': comments_num}


class RedisDb:

    def __init__(self):
        self.client = redis.StrictRedis(**REDIS_CONFIG)

    def save(self, key, value):
        data = pickle.dumps(value)
        self.client.set(key, data)
        logger.debug(' INSERT DATA INTO REDIS')

    def query_one(self, cls, uid):
        key = str(uid)
        val = self.client.get(key)
        if val:
            ad = pickle.loads(val)
            logger.debug(' QUERY ONE FROM REDIS')
            return cls(**ad)
        return None

    def get_statistic(self, uid):
        key = 'stat_' + str(uid)
        try:
            logger.debug(' GET STATISTICS FROM REDIS')
            return pickle.loads(self.client.get(key))
        except:
            return None

    def set_statistic(self, uid, stat_data):
        key = 'stat_' + str(uid)
        self.client.set(key, pickle.dumps(stat_data))
        logger.debug(' SAVE STATISTICS TO REDIS')


mongo_db = MongoDb()
redis_db = RedisDb()
