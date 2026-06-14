# Flask Enterprise Architecture

هذه النسخة منظمة بحيث يكون التطوير المستقبلي أسهل وأقل مخاطرة.

## المبادئ المعتمدة

1. **Application Factory**: إنشاء التطبيق داخل `create_app()` بدل كائن عالمي ثابت.
2. **Blueprints**: تقسيم الواجهة العامة، المصادقة، ولوحة التحكم إلى وحدات مستقلة.
3. **Services Layer**: نقل منطق الأعمال من routes إلى خدمات قابلة لإعادة الاستخدام والاختبار.
4. **Thin Routes**: وظيفة route تستقبل الطلب وتستدعي الخدمة ثم تعرض القالب أو تعيد التوجيه.
5. **Config by Environment**: إعدادات منفصلة للتطوير، الاختبار، والإنتاج.
6. **CLI خارج run.py**: أوامر قاعدة البيانات والبيانات التجريبية في `app/cli.py`.
7. **Security by Default**: CSRF، Rate Limiting، تنظيف HTML، منع SVG uploads، Security Headers.
8. **Database Migrations**: الاعتماد على Flask-Migrate/Alembic للتغييرات المستقبلية.
9. **Soft Delete + Audit Log**: حماية البيانات وتتبع العمليات الإدارية.
10. **Testable Design**: إمكانية إنشاء تطبيق اختباري بقاعدة in-memory عبر `TestingConfig`.

## الهيكلة

```text
app/
  __init__.py              # create_app + تسجيل المكونات
  cli.py                   # أوامر flask cli
  extensions.py            # db / csrf / migrate / limiter
  security.py              # تنظيف HTML والنصوص والتحقق من الروابط والبريد
  audit.py                 # تسجيل العمليات الإدارية
  blueprints/
    main/                  # صفحات الموقع العامة
    auth/                  # تسجيل الدخول والخروج
    admin/                 # لوحة التحكم
  services/
    content_service.py        # البحث، الفرز، التصنيفات، والمحتوى المرتبط
    offering_service.py       # بيانات صفحة الخدمات العامة
    comment_service.py        # التعليقات الخاصة
    admin_content_service.py  # حفظ بيانات المقالات والمشاريع من لوحة التحكم
    upload_service.py         # رفع الملفات والتحقق منها
    permission_service.py     # الأدوار والصلاحيات
  utils/
    request_utils.py       # أدوات الطلب مثل IP
  models/                  # SQLAlchemy models
  templates/               # Jinja templates
  static/                  # CSS/JS/images/uploads
```

## متى تضيف Service جديدة؟

أضف Service إذا كان المنطق:

- يستخدمه أكثر من route.
- يحتوي على استعلامات قاعدة بيانات متعددة.
- يحتوي على قواعد أعمال مثل الصلاحيات، الحالات، الفلترة، أو التحقق.
- تريد اختباره لاحقًا بدون تشغيل المتصفح.

## قاعدة مهمة

لا تضع منطق الأعمال داخل القوالب أو routes. القالب للعرض، route للتوجيه، service للمنطق، model للبيانات.

## طبقة إحصائيات الزوار

أضيفت وحدة مستقلة لإحصائيات الزوار:

```text
app/models/page_view.py
app/services/analytics_service.py
app/templates/admin/analytics.html
migrations/versions/20260605_internal_analytics.py
```

آلية العمل:

1. `after_request` في `app/__init__.py` يسجل فقط طلبات GET العامة الناجحة من نوع HTML.
2. `analytics_service.py` يستثني `admin`, `auth`, `static`, `uploads`, `robots.txt`, و `sitemap.xml`.
3. يتم إنشاء Cookie للزائر باسم `istidlal_visitor_id`، لكن قاعدة البيانات تحفظ HMAC hash فقط.
4. لا يتم تخزين IP خام؛ يتم تخزين `ip_hash` فقط.
5. لوحة التحكم تقرأ التقارير عبر `get_analytics_report()` بدل كتابة الاستعلامات داخل routes.

هذا يحافظ على فصل المسؤوليات وسهولة التوسع مستقبلًا، مثل إضافة geolocation اختياري أو ربط Google Analytics/Plausible دون تغيير القوالب الأساسية.
