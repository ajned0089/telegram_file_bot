# دليل تخصيص بوت مشاركة الملفات

هذا الدليل يشرح كيفية تخصيص وتعديل بوت مشاركة الملفات ليناسب احتياجاتك الخاصة.

## تخصيص الواجهة

### تغيير النصوص والترجمات

يمكنك تعديل النصوص والترجمات من خلال تحرير ملف `app/localization/strings.py`:

1. **تعديل النصوص الإنجليزية**:
   ```python
   # English strings
   en_strings = {
       "welcome": "👋 Welcome to YOUR File Sharing Bot!",
       # ... تعديل النصوص الأخرى
   }
   ```

2. **تعديل النصوص العربية**:
   ```python
   # Arabic strings
   ar_strings = {
       "welcome": "👋 مرحبًا بك في بوت مشاركة الملفات الخاص بك!",
       # ... تعديل النصوص الأخرى
   }
   ```

3. **إضافة لغة جديدة**:
   ```python
   # French strings
   fr_strings = {
       "welcome": "👋 Bienvenue dans votre Bot de Partage de Fichiers!",
       # ... إضافة ترجمات أخرى
   }
   
   def get_string(key: str, lang: str = "en") -> str:
       """Get localized string."""
       if lang == "ar":
           return ar_strings.get(key, en_strings.get(key, key))
       elif lang == "fr":
           return fr_strings.get(key, en_strings.get(key, key))
       else:
           return en_strings.get(key, key)
   ```

### تخصيص لوحة الويب

1. **تعديل القوالب**:
   يمكنك تعديل قوالب HTML في مجلد `app/web/templates/`:
   - `base.html`: القالب الأساسي الذي تستند إليه جميع الصفحات
   - `index.html`: صفحة لوحة التحكم الرئيسية
   - وغيرها من القوالب

2. **تعديل الأنماط**:
   يمكنك إضافة ملفات CSS مخصصة في مجلد `app/web/static/css/`

3. **تعديل JavaScript**:
   يمكنك إضافة ملفات JavaScript مخصصة في مجلد `app/web/static/js/`

## إضافة ميزات جديدة

### إضافة أوامر جديدة للبوت

1. **إضافة معالج جديد**:
   افتح ملف `app/handlers/user_handlers.py` وأضف دالة جديدة:
   ```python
   async def my_custom_command(message: Message):
       """Handle /mycustom command."""
       # Get database session
       db = next(get_db())
       
       # Get user language
       lang = get_user_language(message.from_user.id, db)
       
       # Send response
       await message.answer("This is my custom command!")
   ```

2. **تسجيل الأمر الجديد**:
   في نفس الملف، أضف الأمر إلى دالة `register_user_handlers`:
   ```python
   def register_user_handlers(dp):
       """Register user handlers."""
       # ... الأوامر الموجودة
       dp.message.register(my_custom_command, Command("mycustom"))
   ```

3. **إضافة الأمر إلى قائمة الأوامر**:
   في ملف `app/bot.py`، أضف الأمر إلى قائمة الأوامر:
   ```python
   commands = [
       # ... الأوامر الموجودة
       BotCommand(command="mycustom", description="My custom command"),
   ]
   ```

### إضافة حالات محادثة جديدة

1. **تعريف حالات جديدة**:
   افتح ملف `app/utils/states.py` وأضف فئة حالات جديدة:
   ```python
   class MyCustomStates(StatesGroup):
       """States for my custom feature."""
       step_one = State()
       step_two = State()
       step_three = State()
   ```

2. **استخدام الحالات في المعالجات**:
   ```python
   async def start_custom_flow(message: Message, state: FSMContext):
       """Start custom flow."""
       await state.set_state(MyCustomStates.step_one)
       await message.answer("Please complete step one:")
   
   async def handle_step_one(message: Message, state: FSMContext):
       """Handle step one."""
       await state.update_data(step_one_data=message.text)
       await state.set_state(MyCustomStates.step_two)
       await message.answer("Now complete step two:")
   
   # ... وهكذا
   ```

3. **تسجيل معالجات الحالات**:
   ```python
   def register_custom_handlers(dp):
       """Register custom handlers."""
       dp.message.register(start_custom_flow, Command("customflow"))
       dp.message.register(handle_step_one, MyCustomStates.step_one)
       # ... تسجيل المعالجات الأخرى
   ```

### إضافة نموذج قاعدة بيانات جديد

1. **تعريف النموذج**:
   افتح ملف `app/database/models.py` وأضف فئة نموذج جديدة:
   ```python
   class MyCustomModel(Base):
       """My custom model."""
       __tablename__ = 'my_custom_table'
       
       id = Column(Integer, primary_key=True)
       name = Column(String(255), nullable=False)
       description = Column(Text, nullable=True)
       created_at = Column(DateTime, default=datetime.utcnow)
       user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
       
       # Relationships
       user = relationship('User', back_populates='custom_items')
   ```

2. **إضافة العلاقة في نموذج المستخدم**:
   في نفس الملف، أضف العلاقة إلى نموذج `User`:
   ```python
   class User(Base):
       # ... الحقول الموجودة
       
       # Relationships
       # ... العلاقات الموجودة
       custom_items = relationship('MyCustomModel', back_populates='user')
   ```

3. **تحديث قاعدة البيانات**:
   قم بتشغيل سكريبت لتحديث قاعدة البيانات:
   ```python
   from app.database.db import engine
   from app.database.models import Base, MyCustomModel
   
   # Create the new table
   Base.metadata.create_all(bind=engine)
   ```

## تخصيص الوظائف الأساسية

### تعديل عملية رفع الملفات

1. **تعديل معالج رفع الملفات**:
   افتح ملف `app/handlers/file_handlers.py` وقم بتعديل دالة `handle_file_upload`:
   ```python
   async def handle_file_upload(message: Message, state: FSMContext):
       """Handle file upload."""
       # ... الكود الموجود
       
       # إضافة منطق مخصص هنا
       
       # ... باقي الكود
   ```

2. **تعديل عملية معالجة الملفات**:
   يمكنك تعديل دالة `upload_file_to_channel` لتغيير كيفية تخزين الملفات:
   ```python
   async def upload_file_to_channel(message: Message, state: FSMContext):
       """Upload file to storage channel."""
       # ... الكود الموجود
       
       # إضافة منطق مخصص لمعالجة الملفات
       # مثلاً: ضغط الملفات، تشفيرها، إلخ
       
       # ... باقي الكود
   ```

### تعديل نظام البحث

1. **تعديل وظائف البحث**:
   افتح ملف `app/utils/helpers.py` وقم بتعديل دوال البحث:
   ```python
   def search_files_by_name(db: Session, query: str) -> List[File]:
       """Search files by name."""
       # تعديل استعلام البحث ليكون أكثر تقدمًا
       return db.query(File).filter(
           or_(
               File.file_name.ilike(f"%{query}%"),
               File.tags.any(Tag.name.ilike(f"%{query}%"))
           )
       ).all()
   ```

2. **إضافة طرق بحث جديدة**:
   ```python
   def search_files_by_content(db: Session, query: str) -> List[File]:
       """Search files by content (for text files)."""
       # هذه مجرد فكرة، تحتاج إلى تنفيذ فعلي
       # يمكن استخدام خدمة خارجية لفهرسة محتوى الملفات
       pass
   ```

### تعديل نظام المصادقة

1. **تعديل التحقق من الاشتراك**:
   افتح ملف `app/utils/helpers.py` وقم بتعديل دالة `check_subscription`:
   ```python
   def check_subscription(telegram_id: int, bot: Bot, db: Session) -> bool:
       """Check if user is subscribed to required channels."""
       # ... الكود الموجود
       
       # إضافة منطق مخصص للتحقق
       # مثلاً: التحقق من اشتراك المستخدم في قنوات إضافية
       
       # ... باقي الكود
   ```

2. **إضافة طرق مصادقة إضافية**:
   ```python
   def verify_user_identity(telegram_id: int, verification_code: str, db: Session) -> bool:
       """Verify user identity with a verification code."""
       # هذه مجرد فكرة، تحتاج إلى تنفيذ فعلي
       pass
   ```

## إضافة واجهات برمجة تطبيقات (APIs) جديدة

1. **إضافة نقطة نهاية جديدة**:
   افتح ملف `app/api/api.py` وأضف مسار جديد:
   ```python
   @api_app.get("/custom-endpoint")
   async def custom_endpoint(
       user: User = Depends(verify_api_key),
       db: Session = Depends(get_db)
   ):
       """Custom API endpoint."""
       # منطق مخصص هنا
       
       await log_api_request(Request, status.HTTP_200_OK, user.id, db)
       
       return {"message": "This is a custom endpoint"}
   ```

2. **إضافة نقطة نهاية POST**:
   ```python
   @api_app.post("/custom-action")
   async def custom_action(
       data: dict,
       user: User = Depends(verify_api_key),
       db: Session = Depends(get_db)
   ):
       """Custom API action."""
       # معالجة البيانات المرسلة
       
       await log_api_request(Request, status.HTTP_201_CREATED, user.id, db)
       
       return {"status": "success", "data": data}
   ```

## تكامل مع خدمات خارجية

### تكامل مع خدمات التخزين السحابي

1. **إضافة دعم Google Drive**:
   أنشئ ملف `app/utils/cloud_storage.py`:
   ```python
   from googleapiclient.discovery import build
   from google.oauth2 import service_account
   
   def upload_to_google_drive(file_path: str, file_name: str) -> str:
       """Upload file to Google Drive."""
       # إعداد مصادقة Google Drive
       credentials = service_account.Credentials.from_service_account_file(
           'credentials.json',
           scopes=['https://www.googleapis.com/auth/drive']
       )
       
       # بناء خدمة Drive
       drive_service = build('drive', 'v3', credentials=credentials)
       
       # تحميل الملف
       # ... منطق التحميل
       
       return "drive_file_id"
   ```

2. **استخدام الوظيفة في معالج رفع الملفات**:
   ```python
   async def upload_file_to_channel(message: Message, state: FSMContext):
       """Upload file to storage channel."""
       # ... الكود الموجود
       
       # تحميل الملف إلى Google Drive
       from ..utils.cloud_storage import upload_to_google_drive
       drive_file_id = upload_to_google_drive(temp_file_path, data['file_name'])
       
       # تخزين معرف الملف في قاعدة البيانات
       new_file.cloud_file_id = drive_file_id
       
       # ... باقي الكود
   ```

### تكامل مع خدمات المدفوعات

1. **إضافة دعم Stripe**:
   أنشئ ملف `app/utils/payments.py`:
   ```python
   import stripe
   from dotenv import load_dotenv
   import os
   
   # تحميل متغيرات البيئة
   load_dotenv()
   
   # إعداد Stripe
   stripe.api_key = os.getenv("STRIPE_API_KEY")
   
   def create_payment_link(amount: float, currency: str = "usd", description: str = "") -> str:
       """Create a payment link."""
       # إنشاء منتج
       product = stripe.Product.create(name=description or "File Bot Subscription")
       
       # إنشاء سعر
       price = stripe.Price.create(
           product=product.id,
           unit_amount=int(amount * 100),  # تحويل إلى سنتات
           currency=currency,
       )
       
       # إنشاء رابط دفع
       payment_link = stripe.PaymentLink.create(
           line_items=[{"price": price.id, "quantity": 1}],
       )
       
       return payment_link.url
   ```

2. **إضافة معالج للمدفوعات**:
   ```python
   async def handle_subscription(message: Message):
       """Handle /subscribe command."""
       # Get database session
       db = next(get_db())
       
       # Get user language
       lang = get_user_language(message.from_user.id, db)
       
       # Create payment link
       from ..utils.payments import create_payment_link
       payment_link = create_payment_link(9.99, description="Monthly Subscription")
       
       # Create keyboard
       builder = InlineKeyboardBuilder()
       builder.button(text="💳 Pay Now", url=payment_link)
       
       # Send payment message
       await message.answer(
           "Subscribe to our premium plan for $9.99/month:",
           reply_markup=builder.as_markup()
       )
   ```

## تحسين الأداء

### تنفيذ التخزين المؤقت (Caching)

1. **إضافة وظائف التخزين المؤقت**:
   أنشئ ملف `app/utils/cache.py`:
   ```python
   import functools
   import time
   from typing import Dict, Any, Callable, Optional
   
   # قاموس بسيط للتخزين المؤقت
   _cache: Dict[str, Dict[str, Any]] = {}
   
   def cached(ttl: int = 300):
       """Cache decorator with time-to-live in seconds."""
       def decorator(func: Callable):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               # إنشاء مفتاح التخزين المؤقت
               cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
               
               # التحقق من وجود النتيجة في التخزين المؤقت
               if cache_key in _cache:
                   entry = _cache[cache_key]
                   if entry["expires"] > time.time():
                       return entry["value"]
               
               # تنفيذ الدالة وتخزين النتيجة
               result = func(*args, **kwargs)
               _cache[cache_key] = {
                   "value": result,
                   "expires": time.time() + ttl
               }
               
               return result
           return wrapper
       return decorator
   ```

2. **استخدام التخزين المؤقت في الوظائف**:
   ```python
   from ..utils.cache import cached
   
   @cached(ttl=60)  # تخزين مؤقت لمدة 60 ثانية
   def get_user_language(telegram_id: int, db: Session) -> str:
       """Get user language."""
       user = db.query(User).filter(User.telegram_id == telegram_id).first()
       
       if not user:
           # Default to English
           return "en"
       
       return user.language_code
   ```

### تحسين استعلامات قاعدة البيانات

1. **إضافة فهارس**:
   قم بتعديل نماذج قاعدة البيانات لإضافة فهارس:
   ```python
   class File(Base):
       """File model."""
       __tablename__ = 'files'
       
       # ... الحقول الموجودة
       
       # إضافة فهارس
       __table_args__ = (
           Index('idx_file_name', 'file_name'),
           Index('idx_upload_date', 'upload_date'),
           Index('idx_owner_id', 'owner_id'),
       )
   ```

2. **استخدام استعلامات أكثر كفاءة**:
   ```python
   def get_user_files(db: Session, telegram_id: int) -> List[File]:
       """Get files uploaded by user."""
       # استخدام join بدلاً من استعلامات متعددة
       return db.query(File).join(User).filter(User.telegram_id == telegram_id).all()
   ```

## تخصيص متقدم

### إضافة نظام إشعارات متقدم

1. **تعديل نموذج الإشعارات**:
   قم بتعديل نموذج `Notification` في `app/database/models.py`:
   ```python
   class Notification(Base):
       """Notification model."""
       __tablename__ = 'notifications'
       
       # ... الحقول الموجودة
       
       # إضافة حقول جديدة
       priority = Column(Integer, default=0)  # 0=normal, 1=important, 2=urgent
       action_url = Column(String(255), nullable=True)
       action_text = Column(String(50), nullable=True)
   ```

2. **إضافة وظائف إشعارات متقدمة**:
   قم بتعديل ملف `app/utils/notifications.py`:
   ```python
   async def send_notification_with_action(bot: Bot, user_id: int, message: str, action_text: str, action_url: str, priority: int = 0) -> bool:
       """Send notification with action button."""
       try:
           # Create keyboard
           from aiogram.utils.keyboard import InlineKeyboardBuilder
           builder = InlineKeyboardBuilder()
           builder.button(text=action_text, url=action_url)
           
           await bot.send_message(
               chat_id=user_id,
               text=message,
               reply_markup=builder.as_markup()
           )
           return True
       except Exception as e:
           logging.error(f"Error sending notification to user {user_id}: {e}")
           return False
   ```

### إضافة نظام تحليلات متقدم

1. **إضافة وظائف تحليلات متقدمة**:
   قم بتعديل ملف `app/utils/analytics.py`:
   ```python
   def get_user_retention(db: Session, days: int = 30) -> Dict[str, float]:
       """Get user retention statistics."""
       # حساب معدل الاحتفاظ بالمستخدمين
       total_users = db.query(User).count()
       
       # المستخدمون النشطون في الأيام الماضية
       retention_data = {}
       
       for day in [1, 7, 14, 30]:
           if day > days:
               continue
               
           cutoff_date = datetime.utcnow() - timedelta(days=day)
           active_users = db.query(User).filter(User.last_activity >= cutoff_date).count()
           
           retention_data[f"{day}_day"] = (active_users / total_users) * 100 if total_users > 0 else 0
       
       return retention_data
   ```

2. **إضافة صفحة تحليلات متقدمة**:
   أنشئ ملف `app/web/templates/advanced_analytics.html`:
   ```html
   {% extends "base.html" %}
   
   {% block title %}Advanced Analytics - Telegram File Bot Admin{% endblock %}
   
   {% block header %}Advanced Analytics{% endblock %}
   
   {% block content %}
   <div class="row">
       <div class="col-md-6 mb-4">
           <div class="card">
               <div class="card-header">
                   <h5 class="card-title">User Retention</h5>
               </div>
               <div class="card-body">
                   <canvas id="retentionChart"></canvas>
               </div>
           </div>
       </div>
       
       <!-- Add more analytics widgets -->
   </div>
   {% endblock %}
   
   {% block scripts %}
   <script>
       // Render retention chart
       const retentionCtx = document.getElementById('retentionChart').getContext('2d');
       const retentionChart = new Chart(retentionCtx, {
           type: 'bar',
           data: {
               labels: ['1 Day', '7 Days', '14 Days', '30 Days'],
               datasets: [{
                   label: 'User Retention (%)',
                   data: [
                       {{ retention_data.get('1_day', 0) | round(1) }},
                       {{ retention_data.get('7_day', 0) | round(1) }},
                       {{ retention_data.get('14_day', 0) | round(1) }},
                       {{ retention_data.get('30_day', 0) | round(1) }}
                   ],
                   backgroundColor: 'rgba(54, 162, 235, 0.5)',
                   borderColor: 'rgba(54, 162, 235, 1)',
                   borderWidth: 1
               }]
           },
           options: {
               scales: {
                   y: {
                       beginAtZero: true,
                       max: 100
                   }
               }
           }
       });
   </script>
   {% endblock %}
   ```

## خاتمة

هذا الدليل يقدم نظرة عامة على كيفية تخصيص وتعديل بوت مشاركة الملفات. يمكنك استخدام هذه الأفكار كنقطة انطلاق لتطوير البوت بما يتناسب مع احتياجاتك الخاصة.

تذكر دائمًا اختبار التغييرات في بيئة تطوير قبل نشرها في بيئة الإنتاج، واحتفظ بنسخ احتياطية منتظمة لقاعدة البيانات والكود.