import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class SecretsManager:
    @staticmethod
    def get_secret(key):
        val = os.getenv(key)
        if val:
            return val

        # Default values for local/sandbox testing
        defaults = {
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "SECRET_KEY": "secret",
            "ALGORITHM": "HS256",
            "CLOUDINARY_NAME": "dummy",
            "CLOUDINARY_API_KEY": "dummy",
            "CLOUDINARY_API_SECRET": "dummy",
            "SQLALCHEMY_DATABASE_URL": "sqlite:///./test.db"
        }
        return defaults.get(key)
