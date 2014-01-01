import os
import sys

from CodernityDB.database import Database
from pyramid.scripts.common import configparser

from papaye.indexes import INDEXES


def create_db(settings):
    database_path = settings['codernity.url'][7:]
    db = Database(database_path)
    if not db.exists():
        print("Create Database at {}".format(db.path))
        db.create()
        for name, index_class in INDEXES:
            index = index_class(db.path, name)
            db.add_index(index)
    else:
        print("Database already exists at {}".format(db.path))
        db.open()
    return db


def get_settings(inifile):
    parser = configparser.ConfigParser()
    current_dir = os.path.abspath(os.path.curdir)
    parser.read(inifile)
    return dict(parser.items('app:main', vars={"here": current_dir}))


def main(*argv, **kwargs):
    settings = get_settings(sys.argv[1])
    create_db(settings)
    print("Initialization complete!")
