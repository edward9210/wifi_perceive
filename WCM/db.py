#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

DB = {
    'name': 'wcm',
    'user': 'root',
    'pwd': '123456',
}

def get_db():
    """
        get wcm's database
        :return: the database
    """
    db = pymongo.MongoClient()[DB['name']]
    db.authenticate(DB['user'], DB['pwd'])
    return db


