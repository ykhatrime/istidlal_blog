"""Public service offerings used by the services page.

Keeping this content in a small service module keeps the route thin and makes it
simple to later replace the static list with database-backed offerings from the
admin panel without changing the template contract.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceOffering:
    icon: str
    title: str
    summary: str
    outcomes: tuple[str, ...]
    tools: tuple[str, ...]


@dataclass(frozen=True)
class ServiceProcessStep:
    number: str
    title: str
    description: str


_SERVICE_OFFERINGS = {
    "ar": (
        ServiceOffering(
            icon="📊",
            title="لوحات بيانات وذكاء أعمال",
            summary="تصميم لوحات قيادية وتشغيلية تساعد الإدارة على متابعة الأداء واتخاذ القرار بسرعة.",
            outcomes=("مؤشرات أداء واضحة", "تقارير شهرية وتفاعلية", "توحيد مصادر البيانات"),
            tools=("Power BI", "SQL", "Excel", "DAX"),
        ),
        ServiceOffering(
            icon="🧱",
            title="مستودعات البيانات ونمذجة البيانات",
            summary="بناء نماذج بيانات قابلة للتوسع وربط المصادر المختلفة في مصدر موثوق واحد للتحليل.",
            outcomes=("تصميم Data Model", "Staging و Data Marts", "حوكمة جودة البيانات"),
            tools=("SQL Server", "ETL", "Data Warehouse", "Star Schema"),
        ),
        ServiceOffering(
            icon="🔄",
            title="التكاملات وواجهات API",
            summary="ربط الأنظمة وجلب البيانات آليًا من APIs أو قواعد بيانات أو ملفات لتقليل العمل اليدوي.",
            outcomes=("أتمتة السحب والتحديث", "سجلات تشغيل وأخطاء", "واجهات تكامل موثقة"),
            tools=("Python", "Flask", "REST API", "Celery"),
        ),
        ServiceOffering(
            icon="🤖",
            title="حلول الذكاء الاصطناعي والمساعدات الذكية",
            summary="تحويل المعرفة والبيانات إلى مساعدين داخليين ونماذج أولية تساعد الموظفين على الإنجاز.",
            outcomes=("مساعد بحث داخلي", "تلخيص وتحليل مستندات", "نماذج أولية قابلة للتجربة"),
            tools=("AI", "RAG", "Automation", "Python"),
        ),
        ServiceOffering(
            icon="🛡️",
            title="حوكمة البيانات وتحسين جودة البيانات",
            summary="تقييم الوضع الحالي ووضع إجراءات عملية لتحسين جودة البيانات ووضوح الملكيات والمسؤوليات.",
            outcomes=("قاموس بيانات", "مؤشرات جودة البيانات", "أدوار ومسؤوليات واضحة"),
            tools=("Data Governance", "DQ Rules", "Metadata", "Policies"),
        ),
        ServiceOffering(
            icon="🎓",
            title="التدريب وورش العمل",
            summary="ورش عملية للفرق في تحليل البيانات، Power BI، الذكاء الاصطناعي، وأفضل ممارسات التحول الرقمي.",
            outcomes=("تطبيقات عملية", "مواد تدريبية", "خطة تطوير مهارات"),
            tools=("Workshops", "Power BI", "AI Tools", "Data Literacy"),
        ),
    ),
    "en": (
        ServiceOffering(
            icon="📊",
            title="Dashboards & Business Intelligence",
            summary="Executive and operational dashboards that help leaders monitor performance and make faster decisions.",
            outcomes=("Clear KPIs", "Interactive reporting", "Unified data sources"),
            tools=("Power BI", "SQL", "Excel", "DAX"),
        ),
        ServiceOffering(
            icon="🧱",
            title="Data Warehousing & Data Modeling",
            summary="Scalable data models that connect different sources into one trusted analytical layer.",
            outcomes=("Data model design", "Staging and data marts", "Data quality governance"),
            tools=("SQL Server", "ETL", "Data Warehouse", "Star Schema"),
        ),
        ServiceOffering(
            icon="🔄",
            title="Integrations & APIs",
            summary="Automated data collection from APIs, databases, and files to reduce manual work.",
            outcomes=("Automated refresh", "Run and error logs", "Documented integrations"),
            tools=("Python", "Flask", "REST API", "Celery"),
        ),
        ServiceOffering(
            icon="🤖",
            title="AI Solutions & Smart Assistants",
            summary="AI prototypes and internal assistants that turn knowledge and data into practical productivity tools.",
            outcomes=("Internal search assistant", "Document summarization", "Testable prototypes"),
            tools=("AI", "RAG", "Automation", "Python"),
        ),
        ServiceOffering(
            icon="🛡️",
            title="Data Governance & Data Quality",
            summary="Practical assessments and operating models to improve data quality, ownership, and accountability.",
            outcomes=("Data dictionary", "Data quality KPIs", "Clear roles and responsibilities"),
            tools=("Data Governance", "DQ Rules", "Metadata", "Policies"),
        ),
        ServiceOffering(
            icon="🎓",
            title="Training & Workshops",
            summary="Hands-on workshops for data analysis, Power BI, AI tools, and digital transformation best practices.",
            outcomes=("Practical exercises", "Training material", "Skills development plan"),
            tools=("Workshops", "Power BI", "AI Tools", "Data Literacy"),
        ),
    ),
}

_SERVICE_PROCESS = {
    "ar": (
        ServiceProcessStep("01", "فهم الاحتياج", "جلسة قصيرة لتحديد المشكلة، أصحاب المصلحة، والنتيجة المطلوبة."),
        ServiceProcessStep("02", "تحليل الوضع الحالي", "مراجعة مصادر البيانات، الأنظمة، التقارير الحالية، والفجوات."),
        ServiceProcessStep("03", "تصميم الحل", "اقتراح معماري واضح يشمل البيانات، الواجهة، الأمان، وطريقة التشغيل."),
        ServiceProcessStep("04", "تنفيذ وتسليم", "تطوير تدريجي مع تجربة المستخدم، توثيق، وتسليم قابل للتوسع."),
    ),
    "en": (
        ServiceProcessStep("01", "Understand the need", "A focused session to define the problem, stakeholders, and expected outcome."),
        ServiceProcessStep("02", "Assess the current state", "Review data sources, systems, existing reports, and gaps."),
        ServiceProcessStep("03", "Design the solution", "A clear architecture covering data, interface, security, and operations."),
        ServiceProcessStep("04", "Build and hand over", "Iterative delivery with UX review, documentation, and scalable handover."),
    ),
}


def get_service_offerings(lang: str = "ar") -> tuple[ServiceOffering, ...]:
    return _SERVICE_OFFERINGS.get(lang, _SERVICE_OFFERINGS["ar"])


def get_service_process(lang: str = "ar") -> tuple[ServiceProcessStep, ...]:
    return _SERVICE_PROCESS.get(lang, _SERVICE_PROCESS["ar"])
