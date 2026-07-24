"""
测试专用设置。

- 默认使用内存 SQLite，便于本地/CI 在没有 PostgreSQL 的环境直接运行
  ``python manage.py test --settings=flight_booking.test_settings``。
- 当设置了环境变量 ``DB_ENGINE=postgres``（例如 docker compose 中）时，
  回退到生产同构的 PostgreSQL 配置，保证与部署环境一致。
"""

from .settings import *  # noqa: F401,F403

import os

if os.environ.get('DB_ENGINE', 'sqlite3') == 'postgres':
    # 保留 settings.py 中 docker compose 使用的 PostgreSQL 配置
    pass
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

# 测试时关闭 CSRF 以便 TestClient 直接 POST（本项目视图本身 @csrf_exempt，这里仅双保险）
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 测试期间关闭 DEBUG 模板以外的噪音
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
