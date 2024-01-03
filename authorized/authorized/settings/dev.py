from .prod import *

load_dotenv()

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME_DEV"),
        "USER": os.environ.get("DB_USER_DEV"),
        "PASSWORD": os.environ.get("DB_PASSWORD_DEV"),
        "HOST": os.environ.get("DB_HOST_DEV"),
        "PORT": os.environ.get("DB_PORT_DEV"),
    }
}
