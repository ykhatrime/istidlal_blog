# تشغيل Istidlal Blog على MySQL في الإنتاج

## 1) إنشاء قاعدة البيانات

```sql
CREATE DATABASE istidlal_blog
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'istidlal_user'@'%' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON istidlal_blog.* TO 'istidlal_user'@'%';
FLUSH PRIVILEGES;
```

## 2) إعداد `.env`

```env
APP_ENV=production
DEBUG=False
SECRET_KEY=ضع_مفتاح_سري_طويل_هنا

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=istidlal_blog
MYSQL_USER=istidlal_user
MYSQL_PASSWORD=strong_password
MYSQL_CHARSET=utf8mb4

WTF_CSRF_TIME_LIMIT=3600
WTF_CSRF_SSL_STRICT=True
RATELIMIT_STORAGE_URI=redis://127.0.0.1:6379/0

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=StrongAdminPassword
```

أو استخدم:

```env
DATABASE_URL=mysql+pymysql://istidlal_user:strong_password@127.0.0.1:3306/istidlal_blog?charset=utf8mb4
```

## 3) تثبيت وتشغيل الترحيلات

```bash
pip install -r requirements.txt
flask --app run.py create-db
flask --app run.py db upgrade
flask --app run.py seed-admin
```

## 4) تشغيل Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

## ملاحظات مهمة

- استخدم HTTPS.
- لا تستخدم `memory://` في Rate Limiting مع أكثر من worker؛ استخدم Redis.
- خذ نسخة احتياطية من قاعدة البيانات ومجلد `app/static/uploads`.
- لا تستخدم `flask --app run.py init-db --force` في الإنتاج إلا إذا كنت تريد حذف البيانات.
