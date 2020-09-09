import os

prefix = 'sqlite:////'
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "dev key")

    
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # Flag used to enable CSRF protection for image uploading
    CKEDITOR_ENABLE_CSRF = True
    # The URL or endpoint that handles file browser.
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'
    TEMPLATES_AUTO_RELOAD = True
    

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'vfinance.db')
    
config = {
    "development" :DevelopmentConfig
}