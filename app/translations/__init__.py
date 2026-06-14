TRANSLATIONS = {
    'ar': {
        'site_name': 'مدونة استدلال',
        'tagline': 'تحليل، فهم، اتخاذ قرار',
        'home': 'الرئيسية', 'articles': 'المقالات', 'projects': 'المشروعات', 'services': 'الخدمات', 'about': 'عن المدونة', 'contact': 'تواصل معي',
        'welcome': 'مرحباً بك في مدونة استدلال ',
        'hero_subtitle': 'أحوّل البيانات إلى رؤى، والرؤى إلى قرارات',
        'hero_desc':'مساحة معرفية أشارك فيها خبراتي ومقالاتي ومشروعاتي في عالم البيانات، من تحليل البيانات وذكاء الأعمال إلى مستودعات البيانات والذكاء الاصطناعي، مع التركيز على إدارة البيانات وحوكمتها ودورها في دعم التحول الرقمي وصناعة القرار.',
        'browse_articles': 'تصفح المقالات', 'view_projects': 'استعراض المشروعات', 'latest_articles': 'أحدث المقالات', 'latest_projects': 'أحدث المشروعات',
        'view_all': 'عرض الجميع', 'read_more': 'قراءة المزيد', 'view_project': 'عرض المشروع', 'categories': 'الأقسام', 'keywords': 'الكلمات المفتاحية',
        'newsletter_title': 'اشترك في نشرتي البريدية', 'newsletter_desc': 'احصل على أحدث المقالات والمشروعات مباشرة في بريدك الإلكتروني.',
        'email_placeholder': 'أدخل بريدك الإلكتروني', 'subscribe': 'اشترك الآن', 'about_me': 'مطور ومحلل بيانات',
        'about_me_desc': 'مهتم بتحليل البيانات وتحويلها إلى معلومات ذات قيمة تساعد على اتخاذ قرارات أفضل.',
        'admin': 'لوحة التحكم', 'logout': 'تسجيل الخروج', 'login': 'تسجيل الدخول', 'username': 'اسم المستخدم', 'password': 'كلمة المرور',
        'dashboard': 'الرئيسية', 'analytics': 'الزوار', 'new_article': 'مقال جديد', 'new_project': 'مشروع جديد', 'newsletter': 'القوائم البريدية', 'messages': 'الرسائل', 'comments': 'التعليقات',
        'save': 'حفظ', 'edit': 'تعديل', 'delete': 'حذف', 'published': 'منشور', 'draft': 'مسودة', 'actions': 'الإجراءات', 'title': 'العنوان',
        'all_rights': 'جميع الحقوق محفوظة', 'search': 'بحث', 'send': 'إرسال', 'name': 'الاسم', 'subject': 'الموضوع', 'message': 'الرسالة',
        'comment': 'التعليق',
        'contact_success': 'تم إرسال الرسالة بنجاح.', 'subscribe_success': 'تم الاشتراك في القائمة البريدية بنجاح.', 'subscribe_exists': 'هذا البريد مشترك مسبقاً.',
    },
    'en': {
        'site_name': 'Data Blog',
        'tagline': 'Analyze, Understand, Decide',
        'home': 'Home', 'articles': 'Articles', 'projects': 'Projects', 'services': 'Services', 'about': 'About', 'contact': 'Contact',
        'welcome': 'Welcome to Data Blog',
        'hero_subtitle': 'Turning data into insights, insights into decisions',
        'hero_desc': 'I share latest articles, projects, and practical experiences in data analysis, business intelligence, databases, data warehouses, and AI.',
        'browse_articles': 'Browse Articles', 'view_projects': 'View Projects', 'latest_articles': 'Latest Articles', 'latest_projects': 'Latest Projects',
        'view_all': 'View All', 'read_more': 'Read More', 'view_project': 'View Project', 'categories': 'Categories', 'keywords': 'Keywords',
        'newsletter_title': 'Subscribe to my newsletter', 'newsletter_desc': 'Get the latest articles and projects directly in your inbox.',
        'email_placeholder': 'Enter your email', 'subscribe': 'Subscribe', 'about_me': 'Data Developer & Analyst',
        'about_me_desc': 'Interested in analyzing data and transforming it into valuable information for better decisions.',
        'admin': 'Admin', 'logout': 'Logout', 'login': 'Login', 'username': 'Username', 'password': 'Password',
        'dashboard': 'Dashboard', 'analytics': 'Analytics', 'new_article': 'New Article', 'new_project': 'New Project', 'newsletter': 'Newsletter', 'messages': 'Messages', 'comments': 'Comments',
        'save': 'Save', 'edit': 'Edit', 'delete': 'Delete', 'published': 'Published', 'draft': 'Draft', 'actions': 'Actions', 'title': 'Title',
        'all_rights': 'All rights reserved', 'search': 'Search', 'send': 'Send', 'name': 'Name', 'subject': 'Subject', 'message': 'Message',
        'comment': 'Comment',
        'contact_success': 'Message sent successfully.', 'subscribe_success': 'You have subscribed successfully.', 'subscribe_exists': 'This email is already subscribed.',
    }
}

def get_translations(lang='ar'):
    return TRANSLATIONS.get(lang, TRANSLATIONS['ar'])
