"""
Localization strings for the bot.
"""

# English strings
en_strings = {
    # General
    "welcome": "👋 Welcome to the File Sharing Bot!\n\nThis bot allows you to upload and share files with others using unique links.",
    "not_authorized": "⛔ You are not authorized to use this feature.",
    "operation_cancelled": "❌ Operation cancelled.",
    "no_active_operation": "ℹ️ There is no active operation to cancel.",
    "error_occurred": "❌ An error occurred. Please try again later.",
    "select_option": "Please select an option:",
    
    # Buttons
    "upload_button": "📤 Upload File",
    "my_files_button": "📁 My Files",
    "search_button": "🔍 Search",
    "settings_button": "⚙️ Settings",
    "language_button": "🌐 Language",
    "help_button": "❓ Help",
    "admin_button": "🛠️ Admin Panel",
    "back_button": "« Back",
    "cancel_button": "❌ Cancel",
    "skip_button": "⏩ Skip",
    "yes_button": "✅ Yes",
    "no_button": "❌ No",
    "try_again": "🔄 Try Again",
    
    # File Upload
    "send_file": "📤 Please send the file you want to upload.",
    "invalid_file": "❌ Invalid file. Please send a valid file.",
    "file_too_large": "❌ File is too large. Maximum size is {max_size} MB.",
    "file_received": "✅ File received!\n\nFile Name: {file_name}\nFile Size: {file_size}\nFile Type: {file_type}",
    "select_category": "📂 Please select a category for your file:",
    "select_subcategory": "📂 Please select a subcategory:",
    "select_format": "📄 Please select a format for your file:",
    "enter_source": "🔗 Please enter the source URL for your file (optional):",
    "enter_filename": "📝 Please enter a name for your file (optional):",
    "enter_tags": "🏷️ Please enter tags for your file, separated by commas (optional):",
    "set_password": "🔒 Do you want to set a password for this file?",
    "enter_password": "🔑 Please enter a password for your file:",
    "processing_file": "⏳ Processing file...",
    "file_uploaded": "✅ File uploaded successfully!",
    "share_link_created": "🔗 Share Link: {link}",
    
    # File Download
    "file_not_found": "❌ File not found.",
    "enter_password_to_download": "🔑 This file is password protected. Please enter the password:",
    "incorrect_password": "❌ Incorrect password. Please try again.",
    "downloading_file": "⏳ Downloading file...",
    "file_sent": "✅ File sent!",
    
    # Search
    "search_by_name": "🔍 Search by Name",
    "search_by_tag": "🏷️ Search by Tag",
    "search_by_category": "📂 Search by Category",
    "search_by_format": "📄 Search by Format",
    "search_prompt": "🔍 Please enter your search query:",
    "no_results": "❌ No results found.",
    "search_results": "🔍 Found {count} results:",
    
    # Settings
    "settings": "Settings",
    "language_changed": "✅ Language changed successfully!",
    "my_referral": "🔗 Your referral link: {link}\n\nYou have referred {count} users.",
    "referral_button": "🔗 My Referral",
    
    # Files
    "no_files": "📂 You haven't uploaded any files yet.",
    "my_files": "📂 Your files:",
    
    # Subscription
    "subscription_required": "⚠️ You need to subscribe to our channels to use this bot:",
    "subscription_checked": "✅ Subscription checked successfully!",
    "check_subscription": "✅ Check Subscription",
    
    # Admin Panel
    "admin_panel": "Admin Panel",
    "user_management": "👥 User Management",
    "category_management": "📂 Category Management",
    "format_management": "📄 Format Management",
    "subscription_management": "📢 Subscription Management",
    "statistics": "📊 Statistics",
    "backup": "💾 Backup",
    "broadcast": "📣 Broadcast",
    
    # Statistics
    "total_users": "👥 Total Users: {count}",
    "total_files": "📁 Total Files: {count}",
    "total_downloads": "⬇️ Total Downloads: {count}",
    "storage_used": "💾 Storage Used: {size}",
    "active_users": "👥 Active Users (7d): {count}",
}

# Arabic strings
ar_strings = {
    # General
    "welcome": "👋 مرحبًا بك في بوت مشاركة الملفات!\n\nيتيح لك هذا البوت تحميل ومشاركة الملفات مع الآخرين باستخدام روابط فريدة.",
    "not_authorized": "⛔ غير مصرح لك باستخدام هذه الميزة.",
    "operation_cancelled": "❌ تم إلغاء العملية.",
    "no_active_operation": "ℹ️ لا توجد عملية نشطة للإلغاء.",
    "error_occurred": "❌ حدث خطأ. يرجى المحاولة مرة أخرى لاحقًا.",
    "select_option": "يرجى اختيار خيار:",
    
    # Buttons
    "upload_button": "📤 رفع ملف",
    "my_files_button": "📁 ملفاتي",
    "search_button": "🔍 بحث",
    "settings_button": "⚙️ الإعدادات",
    "language_button": "🌐 اللغة",
    "help_button": "❓ مساعدة",
    "admin_button": "🛠️ لوحة الإدارة",
    "back_button": "« رجوع",
    "cancel_button": "❌ إلغاء",
    "skip_button": "⏩ تخطي",
    "yes_button": "✅ نعم",
    "no_button": "❌ لا",
    "try_again": "🔄 حاول مرة أخرى",
    
    # File Upload
    "send_file": "📤 يرجى إرسال الملف الذي تريد رفعه.",
    "invalid_file": "❌ ملف غير صالح. يرجى إرسال ملف صالح.",
    "file_too_large": "❌ الملف كبير جدًا. الحجم الأقصى هو {max_size} ميجابايت.",
    "file_received": "✅ تم استلام الملف!\n\nاسم الملف: {file_name}\nحجم الملف: {file_size}\nنوع الملف: {file_type}",
    "select_category": "📂 يرجى اختيار فئة لملفك:",
    "select_subcategory": "📂 يرجى اختيار فئة فرعية:",
    "select_format": "📄 يرجى اختيار تنسيق لملفك:",
    "enter_source": "🔗 يرجى إدخال رابط المصدر لملفك (اختياري):",
    "enter_filename": "📝 يرجى إدخال اسم لملفك (اختياري):",
    "enter_tags": "🏷️ يرجى إدخال علامات لملفك، مفصولة بفواصل (اختياري):",
    "set_password": "🔒 هل تريد تعيين كلمة مرور لهذا الملف؟",
    "enter_password": "🔑 يرجى إدخال كلمة مرور لملفك:",
    "processing_file": "⏳ جاري معالجة الملف...",
    "file_uploaded": "✅ تم رفع الملف بنجاح!",
    "share_link_created": "🔗 رابط المشاركة: {link}",
    
    # File Download
    "file_not_found": "❌ الملف غير موجود.",
    "enter_password_to_download": "🔑 هذا الملف محمي بكلمة مرور. يرجى إدخال كلمة المرور:",
    "incorrect_password": "❌ كلمة مرور غير صحيحة. يرجى المحاولة مرة أخرى.",
    "downloading_file": "⏳ جاري تنزيل الملف...",
    "file_sent": "✅ تم إرسال الملف!",
    
    # Search
    "search_by_name": "🔍 بحث بالاسم",
    "search_by_tag": "🏷️ بحث بالعلامة",
    "search_by_category": "📂 بحث بالفئة",
    "search_by_format": "📄 بحث بالتنسيق",
    "search_prompt": "🔍 يرجى إدخال استعلام البحث الخاص بك:",
    "no_results": "❌ لم يتم العثور على نتائج.",
    "search_results": "🔍 تم العثور على {count} نتيجة:",
    
    # Settings
    "settings": "الإعدادات",
    "language_changed": "✅ تم تغيير اللغة بنجاح!",
    "my_referral": "🔗 رابط الإحالة الخاص بك: {link}\n\nلقد قمت بإحالة {count} مستخدمين.",
    "referral_button": "🔗 الإحالة الخاصة بي",
    
    # Files
    "no_files": "📂 لم تقم برفع أي ملفات بعد.",
    "my_files": "📂 ملفاتك:",
    
    # Subscription
    "subscription_required": "⚠️ تحتاج إلى الاشتراك في قنواتنا لاستخدام هذا البوت:",
    "subscription_checked": "✅ تم التحقق من الاشتراك بنجاح!",
    "check_subscription": "✅ التحقق من الاشتراك",
    
    # Admin Panel
    "admin_panel": "لوحة الإدارة",
    "user_management": "👥 إدارة المستخدمين",
    "category_management": "📂 إدارة الفئات",
    "format_management": "📄 إدارة التنسيقات",
    "subscription_management": "📢 إدارة الاشتراكات",
    "statistics": "📊 الإحصائيات",
    "backup": "💾 النسخ الاحتياطي",
    "broadcast": "📣 البث",
    
    # Statistics
    "total_users": "👥 إجمالي المستخدمين: {count}",
    "total_files": "📁 إجمالي الملفات: {count}",
    "total_downloads": "⬇️ إجمالي التنزيلات: {count}",
    "storage_used": "💾 المساحة المستخدمة: {size}",
    "active_users": "👥 المستخدمين النشطين (7 أيام): {count}",
}

def get_string(key: str, lang: str = "en") -> str:
    """Get localized string."""
    if lang == "ar":
        return ar_strings.get(key, en_strings.get(key, key))
    else:
        return en_strings.get(key, key)