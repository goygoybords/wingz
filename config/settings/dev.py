from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = env.bool('DEBUG', default=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='27ccw6=vv%*m=0+u)duqrtby6!nzw$f(l7v(!in1hxm129)+du')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '*', ])

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
