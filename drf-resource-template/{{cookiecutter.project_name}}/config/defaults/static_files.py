"""静态资源配置"""
import os
from config import BASE_DIR, ENVIRONMENT

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

if ENVIRONMENT == "production":
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
