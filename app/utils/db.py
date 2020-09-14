import os
import pickle
import logging
from datetime import datetime
from uuid import uuid4

import pymongo
import redis

from .typecodecs import codec_options


MONGO_HOST = 'localhost'
MONGO_PORT = '27017'

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    # 'host':  os.environ.get('REDIS_HOST'),
    # 'port': os.environ.get('REDIS_PORT'),
    'db': 0,
}


logger = logging.getLogger('db-logger')
logger.setLevel(logging.INFO)
logging.info('')


class MongoDb:

    def __init__(self):
        client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')
        db = client['addb']
        self.ads_collection = db.get_collection('ads_collection', codec_options=codec_options)

    def save(self, ad):
        self.ads_collection.insert(ad)
        logger.info(' INSERT DATA INTO MONGO')

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
        ad.pop('_id')
        logger.info(' FIND ONE IN MONGO')
        try:
            return cls(**ad)
        except:
            return None

    def update_tags(self, uid, key, new_data):
        self.ads_collection.update_one({'uid': uid}, {'$set': {key: new_data,
                                                               'updated': datetime.utcnow()}})
        logger.info(' UPDATE TAGS IN MONGO')

    def add_comment(self, uid, comment):
        comment.created = datetime.utcnow()
        self.ads_collection.update_one({'uid': uid}, {'$push': {'comments': dict(comment)}})
        logger.info(' SAVE COMMENT IN MONGO')

    def get_statistic(self, cls, uid):
        '''Returns dict with two keys: tags_num, comments_num'''
        logger.info(' GET STATISTICS FROM MONGO')
        ad = self.find_one(cls, uid)
        tags_num, comments_num = len(ad.tags), len(ad.comments)
        return {'tags_num': tags_num, 'comments_num': comments_num}


class RedisDb:

    def __init__(self):
        self.client = redis.StrictRedis(**REDIS_CONFIG)

    def save(self, key, value):
        data = pickle.dumps(value)
        self.client.set(key, data)
        logger.info(' INSERT DATA INTO REDIS')

    def query_one(self, cls, uid):
        key = str(uid)
        val = self.client.get(key)
        if val:
            ad = pickle.loads(val)
            logger.info(' QUERY ONE FROM REDIS')
            return cls(**ad)
        return None

    def get_statistic(self, uid):
        key = 'stat_' + str(uid)
        try:
            logger.info(' GET STATISTICS FROM REDIS')
            return pickle.loads(self.client.get(key))
        except:
            return None

    def set_statistic(self, uid, stat_data):
        key = 'stat_' + str(uid)
        self.client.set(key, pickle.dumps(stat_data))
        logger.info(' SAVE STATISTICS TO REDIS')


mongo_db = MongoDb()
redis_db = RedisDb()
