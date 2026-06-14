# Istidlal Blog — Flask Enterprise Structure

مدونة وموقع مشاريع ثنائي اللغة مبني بـ Flask، مع واجهة عامة ولوحة تحكم لإدارة المقالات، المشاريع، صفحة الخدمات، الترميز، التعليقات الخاصة، الرسائل، القائمة البريدية، المستخدمين، وسجل العمليات.

هذه النسخة أعيد تنظيمها لتكون أقرب إلى هيكلة Flask احترافية قابلة للتوسع والصيانة.

## أهم التحسينات المعمارية

- اعتماد **Application Factory** داخل `app/__init__.py`.
- تقسيم التطبيق إلى **Blueprints**:
  - `main`: الواجهة العامة.
  - `auth`: تسجيل الدخول والخروج.
  - `admin`: لوحة التحكم.
- نقل منطق الأعمال إلى **Services Layer** بدل تضخيم ملفات routes.
- إضافة إعدادات منفصلة حسب البيئة: Development / Testing / Production.
- نقل أوامر قاعدة البيانات والتهيئة إلى `app/cli.py` بدل `run.py`.
- إضافة `TestingConfig` وقاعدة in-memory لتسهيل الاختبارات.
- إضافة `tests/` و `pyproject.toml` و `requirements-dev.txt`.
- إضافة `docs/ARCHITECTURE.md` لتوثيق الهيكلة وقواعد التوسعة.
- المحافظة على مزايا الأمان السابقة: CSRF، Rate Limiting، HTML Sanitization، منع SVG Uploads، Soft Delete، Audit Log، Roles & Permissions.
- إضافة Security Headers أساسية: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`.

## الهيكلة الجديدة

```text
app/
  __init__.py                 # create_app + تسجيل المكونات
  cli.py                      # أوامر Flask CLI
  extensions.py               # db / csrf / migrate / limiter
  security.py                 # تنظيف HTML والنصوص والتحقق من الروابط والبريد
  audit.py                    # تسجيل العمليات الإدارية
  blueprints/
    main/
      routes.py               # صفحات الموقع العامة
    auth/
      routes.py               # تسجيل الدخول والخروج
    admin/
      routes.py               # لوحة التحكم
  services/
    content_service.py        # البحث، الفرز، المحتوى المرتبط، sidebar
    comment_service.py        # التعليقات الخاصة
    admin_content_service.py  # حفظ بيانات المقالات والمشاريع من لوحة التحكم
    upload_service.py         # رفع الصور والتحقق منها
    permission_service.py     # الأدوار والصلاحيات
  utils/
    request_utils.py          # IP وأدوات الطلب
  models/                     # SQLAlchemy Models
  templates/                  # Jinja Templates
  static/                     # CSS / JS / Images / Uploads
config.py                     # Config Classes
run.py                        # تشغيل محلي فقط
wsgi.py                       # نقطة تشغيل Production WSGI
migrations/                   # Alembic / Flask-Migrate
tests/                        # اختبارات أولية
```

## التشغيل المحلي

```bash
cd istidlal_blog
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask --app run.py create-db
flask --app run.py seed-data
python run.py
```

افتح الموقع:

```text
http://127.0.0.1:5000/ar/
```

لوحة التحكم:

```text
http://127.0.0.1:5000/ar/auth/login
```

بيانات الدخول الافتراضية للتطوير فقط:

```text
username: admin
password: admin123
```

> غيّر كلمة المرور مباشرة قبل أي نشر فعلي.

## أوامر قاعدة البيانات

```bash
# إنشاء الجداول دون حذف بيانات
flask --app run.py create-db

# إنشاء مستخدم المدير فقط
flask --app run.py seed-admin

# إنشاء بيانات تجريبية للتطوير
flask --app run.py seed-data

# تهيئة كاملة للتطوير، مع خيار حذف الجداول
flask --app run.py init-db --force

# تطبيق ترحيلات Alembic
flask --app run.py db upgrade
```

## الاختبارات وأدوات الجودة

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
black .
```

## الأدوار والصلاحيات

| الدور | الصلاحيات |
|---|---|
| admin | كل شيء: المحتوى، التعليقات، الرسائل، القائمة البريدية، المستخدمون، سجل العمليات |
| editor | إدارة المقالات والمشروعات والترميز ورفع الصور |
| moderator | إدارة التعليقات الخاصة واستعراض الرسائل |
| viewer | دخول لوحة التحكم للعرض العام فقط |

إدارة المستخدمين:

```text
/ar/admin/users
```

سجل العمليات:

```text
/ar/admin/audit
```


## صفحة الخدمات

تمت إضافة صفحة عامة للخدمات:

```text
/ar/services
/en/services
```

تعرض الصفحة الخدمات التي يقدمها صاحب الموقع مثل لوحات البيانات، مستودعات البيانات، التكاملات، حلول الذكاء الاصطناعي، حوكمة البيانات، والتدريب. تم حفظ بيانات الخدمات داخل:

```text
app/services/offering_service.py
```

وذلك للحفاظ على Route بسيط وقابل للتوسع لاحقًا إلى إدارة الخدمات من لوحة التحكم أو قاعدة البيانات.

## التعليقات الخاصة

- الزائر يرسل تعليقًا من صفحة المقال أو المشروع.
- التعليقات لا تظهر للعامة.
- تعرض فقط لصاحب الموقع أو من لديه صلاحية إدارة التعليقات داخل لوحة التحكم:

```text
/ar/admin/comments
```

الحالات المدعومة:

```text
new / read / archived / spam
```

## إعدادات الإنتاج المهمة

- غيّر `SECRET_KEY` في `.env`.
- غيّر بيانات المدير الافتراضية.
- استخدم HTTPS.
- استخدم قاعدة إنتاج مثل MySQL أو PostgreSQL عند التوسع.
- استخدم Redis لتخزين حدود Rate Limiting مع أكثر من worker:

```env
RATELIMIT_STORAGE_URI=redis://127.0.0.1:6379/0
```

- لا تستخدم `memory://` في إنتاج متعدد الـ workers إلا للتجارب.
- خذ نسخة احتياطية من قاعدة البيانات ومجلد:

```text
app/static/uploads
```

## تشغيل MySQL في الإنتاج

```sql
CREATE DATABASE istidlal_blog
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'istidlal_user'@'%' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON istidlal_blog.* TO 'istidlal_user'@'%';
FLUSH PRIVILEGES;
```

ملف `.env` للإنتاج:

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
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Lax
SECURITY_HEADERS_ENABLED=True
RATELIMIT_STORAGE_URI=redis://127.0.0.1:6379/0
```

تشغيل الإنتاج باستخدام Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

## قاعدة التطوير المستقبلية

- أضف Route داخل Blueprint المناسب.
- ضع الاستعلامات ومنطق الأعمال داخل `app/services/`.
- ضع التحقق والتنظيف داخل `security.py` أو service مستقل.
- لا تضف منطقًا معقدًا داخل القوالب.
- أي تغيير في قاعدة البيانات يجب أن يتم عبر Flask-Migrate.

## إحصائيات الزوار الداخلية

تمت إضافة نظام Analytics داخلي وخفيف داخل Flask:

```text
/ar/admin/analytics
```

يعرض:

- زوار اليوم.
- زيارات اليوم.
- زوار هذا الشهر.
- زيارات هذا الشهر.
- إجمالي الزوار.
- إجمالي الزيارات.
- مخطط الزيارات اليومية.
- أكثر الصفحات زيارة.
- مصادر الزيارة.
- آخر الزيارات.

ملاحظات الخصوصية:

- لا يتم حفظ عنوان IP بشكل صريح.
- يتم حفظ `ip_hash` و `visitor_hash` باستخدام HMAC.
- يتم استثناء لوحة التحكم، تسجيل الدخول، الملفات الثابتة، والـ sitemap/robots.
- يحترم المتصفح عند إرسال `DNT: 1` إذا كان `ANALYTICS_RESPECT_DNT=True`.

إعدادات اختيارية في `.env`:

```env
INTERNAL_ANALYTICS_ENABLED=True
ANALYTICS_RESPECT_DNT=True
ANALYTICS_HASH_SECRET=ضع_مفتاح_مختلف_أو_اتركه_ليستخدم_SECRET_KEY
```

بعد النشر أو التحديث على قاعدة موجودة، نفّذ Migration:

```bash
flask --app run.py db upgrade
```

أو في بيئة التطوير فقط يمكن استخدام:

```bash
flask --app run.py create-db
```
