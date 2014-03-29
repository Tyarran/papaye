import configparser
import os


def get_settings(inifile):
    parser = configparser.ConfigParser()
    current_dir = os.path.abspath(os.path.curdir)
    parser.read(inifile)
    return dict(parser.items('app:main', vars={"here": current_dir}))
