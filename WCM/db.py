#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

DB = {
    'name': 'wcm',
}

def get_db():
    """
        get wcm's database
        :return: the database
    """
    db = pymongo.MongoClient()[DB['name']]
    return db


