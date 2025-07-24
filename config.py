import os

MONGO_URI   = os.environ.get("MONGO_URI")
SECRET_KEY  = os.environ.get("SECRET_KEY")

if not MONGO_URI or not SECRET_KEY:
    raise RuntimeError("MONGO_URI and SECRET_KEY must be set in the environment")