# دليل نشر بوت مشاركة الملفات

هذا الدليل يشرح كيفية نشر بوت مشاركة الملفات على مختلف البيئات.

## النشر على VPS (خادم افتراضي خاص)

### متطلبات النظام

- نظام تشغيل Linux (Ubuntu 20.04 أو أحدث موصى به)
- Python 3.8 أو أحدث
- 1GB RAM على الأقل (2GB موصى به)
- 10GB مساحة تخزين على الأقل

### خطوات النشر

1. **الاتصال بالخادم**:
   ```bash
   ssh username@your_server_ip
   ```

2. **تثبيت المتطلبات الأساسية**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git nginx supervisor
   ```

3. **تنزيل المشروع**:
   ```bash
   git clone https://github.com/yourusername/telegram_file_bot.git
   cd telegram_file_bot
   ```

4. **إنشاء بيئة افتراضية**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **تثبيت المتطلبات**:
   ```bash
   pip install -r requirements.txt
   ```

6. **إعداد ملف الإعدادات**:
   ```bash
   cp .env.example .env
   nano .env  # قم بتعديل الإعدادات
   ```

7. **تهيئة قاعدة البيانات**:
   ```bash
   python init_db.py
   ```

8. **إعداد Supervisor للتشغيل في الخلفية**:
   ```bash
   sudo nano /etc/supervisor/conf.d/telegramfilebot.conf
   ```
   
   أضف المحتوى التالي:
   ```
   [program:telegramfilebot]
   command=/home/username/telegram_file_bot/venv/bin/python run.py
   directory=/home/username/telegram_file_bot
   user=username
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/telegramfilebot.err.log
   stdout_logfile=/var/log/telegramfilebot.out.log
   ```

9. **تحديث Supervisor وتشغيل البوت**:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start telegramfilebot
   ```

10. **إعداد Nginx للوصول إلى لوحة الويب**:
    ```bash
    sudo nano /etc/nginx/sites-available/telegramfilebot
    ```
    
    أضف المحتوى التالي:
    ```
    server {
        listen 80;
        server_name your_domain.com;

        location / {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

11. **تفعيل الموقع وإعادة تشغيل Nginx**:
    ```bash
    sudo ln -s /etc/nginx/sites-available/telegramfilebot /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

12. **إعداد SSL (اختياري ولكن موصى به)**:
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your_domain.com
    ```

## النشر على Heroku

### متطلبات

- حساب على Heroku
- Heroku CLI مثبت على جهازك
- Git مثبت على جهازك

### خطوات النشر

1. **تسجيل الدخول إلى Heroku**:
   ```bash
   heroku login
   ```

2. **إنشاء تطبيق Heroku**:
   ```bash
   heroku create your-app-name
   ```

3. **إضافة ملف Procfile**:
   أنشئ ملف `Procfile` في مجلد المشروع بالمحتوى التالي:
   ```
   web: uvicorn app.web.app:app --host=0.0.0.0 --port=$PORT
   worker: python run.py --bot-only
   ```

4. **إضافة ملف runtime.txt**:
   أنشئ ملف `runtime.txt` في مجلد المشروع بالمحتوى التالي:
   ```
   python-3.9.13
   ```

5. **إعداد متغيرات البيئة**:
   ```bash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set ADMIN_IDS=123456789
   heroku config:set STORAGE_CHANNEL_ID=-100123456789
   heroku config:set DATABASE_URL=postgres://user:password@host:port/dbname
   heroku config:set WEB_ADMIN_USERNAME=admin
   heroku config:set WEB_ADMIN_PASSWORD=your_secure_password
   ```

6. **إضافة قاعدة بيانات PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

7. **نشر التطبيق**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push heroku main
   ```

8. **تشغيل مهام التهيئة**:
   ```bash
   heroku run python init_db.py
   ```

9. **تشغيل العمال**:
   ```bash
   heroku ps:scale web=1 worker=1
   ```

10. **فتح التطبيق**:
    ```bash
    heroku open
    ```

## النشر على Docker

### متطلبات

- Docker مثبت على جهازك
- Docker Compose مثبت على جهازك (اختياري)

### خطوات النشر

1. **إنشاء ملف Dockerfile**:
   أنشئ ملف `Dockerfile` في مجلد المشروع بالمحتوى التالي:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "run.py"]
   ```

2. **إنشاء ملف docker-compose.yml**:
   أنشئ ملف `docker-compose.yml` في مجلد المشروع بالمحتوى التالي:
   ```yaml
   version: '3'

   services:
     bot:
       build: .
       restart: always
       env_file:
         - .env
       volumes:
         - ./app/database:/app/app/database
         - ./backups:/app/backups
       ports:
         - "8000:8000"
   ```

3. **بناء وتشغيل الحاوية**:
   ```bash
   docker-compose up -d
   ```

4. **تهيئة قاعدة البيانات**:
   ```bash
   docker-compose exec bot python init_db.py
   ```

5. **مراقبة السجلات**:
   ```bash
   docker-compose logs -f
   ```

## النشر على PythonAnywhere

### متطلبات

- حساب على PythonAnywhere (الحساب المجاني يكفي للبداية)

### خطوات النشر

1. **إنشاء حساب على PythonAnywhere**:
   قم بالتسجيل على [PythonAnywhere](https://www.pythonanywhere.com/)

2. **فتح وحدة تحكم Bash**:
   من لوحة التحكم، انقر على "Bash" لفتح وحدة تحكم

3. **تنزيل المشروع**:
   ```bash
   git clone https://github.com/yourusername/telegram_file_bot.git
   cd telegram_file_bot
   ```

4. **إنشاء بيئة افتراضية**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **تثبيت المتطلبات**:
   ```bash
   pip install -r requirements.txt
   ```

6. **إعداد ملف الإعدادات**:
   ```bash
   cp .env.example .env
   nano .env  # قم بتعديل الإعدادات
   ```

7. **تهيئة قاعدة البيانات**:
   ```bash
   python init_db.py
   ```

8. **إعداد تطبيق الويب**:
   - انتقل إلى قسم "Web" في لوحة التحكم
   - انقر على "Add a new web app"
   - اختر "Manual configuration"
   - اختر إصدار Python المناسب
   - أدخل المسار إلى ملف WSGI: `/home/yourusername/telegram_file_bot/wsgi.py`

9. **إنشاء ملف WSGI**:
   أنشئ ملف `wsgi.py` في مجلد المشروع بالمحتوى التالي:
   ```python
   import sys
   import os

   # Add the project directory to the path
   path = '/home/yourusername/telegram_file_bot'
   if path not in sys.path:
       sys.path.append(path)

   # Set environment variables
   os.environ['DATABASE_URL'] = 'sqlite:///app/database/bot_database.db'
   # Add other environment variables as needed

   # Import the FastAPI app
   from app.web.app import app as application
   ```

10. **إعداد مهمة مجدولة لتشغيل البوت**:
    - انتقل إلى قسم "Tasks" في لوحة التحكم
    - أضف مهمة جديدة تعمل كل ساعة:
      ```
      cd /home/yourusername/telegram_file_bot && source venv/bin/activate && python run.py --bot-only
      ```

11. **إعادة تحميل التطبيق**:
    انقر على زر "Reload" في قسم "Web"

## نصائح للنشر

### الأمان

1. **استخدم كلمات مرور قوية**:
   - لحساب المشرف على الويب
   - لقاعدة البيانات إذا كنت تستخدم قاعدة بيانات خارجية

2. **قم بتفعيل SSL**:
   استخدم Let's Encrypt للحصول على شهادة SSL مجانية لتأمين اتصالات لوحة الويب.

3. **قم بتقييد الوصول إلى لوحة الويب**:
   يمكنك استخدام قواعد جدار الحماية لتقييد الوصول إلى لوحة الويب من عناوين IP محددة.

### النسخ الاحتياطي

1. **قم بإعداد نسخ احتياطية منتظمة**:
   تأكد من تكوين النسخ الاحتياطية التلقائية في ملف `.env`.

2. **قم بتخزين النسخ الاحتياطية خارج الخادم**:
   يمكنك استخدام خدمات مثل Amazon S3 أو Google Drive لتخزين النسخ الاحتياطية.

### المراقبة

1. **قم بإعداد مراقبة للخادم**:
   استخدم أدوات مثل Prometheus و Grafana لمراقبة أداء الخادم.

2. **قم بإعداد تنبيهات**:
   إعداد تنبيهات للإشعار في حالة توقف البوت أو حدوث أخطاء.

### التحسين

1. **استخدم خدمة CDN**:
   يمكنك استخدام Cloudflare أو أي خدمة CDN أخرى لتسريع لوحة الويب.

2. **قم بتحسين قاعدة البيانات**:
   إذا كان لديك عدد كبير من المستخدمين، فكر في الترقية إلى قاعدة بيانات أكثر قوة مثل PostgreSQL.

## استكشاف الأخطاء وإصلاحها

### البوت لا يستجيب

1. **تحقق من سجلات البوت**:
   ```bash
   tail -f /var/log/telegramfilebot.out.log
   ```

2. **تحقق من حالة Supervisor**:
   ```bash
   sudo supervisorctl status telegramfilebot
   ```

3. **تحقق من توكن البوت**:
   تأكد من أن توكن البوت صحيح في ملف `.env`.

### لوحة الويب لا تعمل

1. **تحقق من سجلات Nginx**:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. **تحقق من حالة Nginx**:
   ```bash
   sudo systemctl status nginx
   ```

3. **تحقق من إعدادات جدار الحماية**:
   ```bash
   sudo ufw status
   ```

### مشاكل قاعدة البيانات

1. **تحقق من حقوق الوصول**:
   ```bash
   ls -la app/database/
   ```

2. **قم بإنشاء نسخة احتياطية يدوية**:
   ```bash
   python -c "from app.utils.helpers import create_backup; create_backup('app/database/bot_database.db')"
   ```

3. **استعادة من نسخة احتياطية**:
   ```bash
   python -c "from app.utils.helpers import restore_backup; restore_backup('backups/backup_filename.db', 'app/database/bot_database.db')"
   ```