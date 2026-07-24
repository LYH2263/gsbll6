"""测试专用配置。

复用生产配置，但将数据库切换为 SQLite 内存库，使 `manage.py test`
无需依赖 PostgreSQL 即可运行（本地一条命令 / CI / docker 均可）。
用法：
    python manage.py test --settings=flight_booking.test_settings
"""

from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 测试时无需真实密码校验，加快用例执行
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
