"""
 Author:           Gautam Iyer 
 Date:             02/20/2021
 Project:          CS 4485.001 Spring 2021
 Filename:         config.py
 Description:      The config file is executed by flask. Can have development, production or testing.
 
"""

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"
    DB_HOST = 'database-1.cluster-cf5kjev2ovc7.us-east-1.rds.amazonaws.com'
    DB_NAME = 'IGA_DB'
    DB_USERNAME = "admin"
    DB_PASSWORD = '8m8oqtTn'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    ALLOWED_FONTS = ["Times New Roman", "Calibri Math"]
    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = 'localhost'
    DB_NAME = 'IGA_DB'
    DB_USERNAME = "root"
    DB_PASSWORD = 'time2COMPLETE'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    ALLOWED_FONTS = {"Times New Roman", "Calibri Math"}
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True

    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    SESSION_COOKIE_SECURE = False
