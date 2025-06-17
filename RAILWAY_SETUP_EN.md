# Railway Deployment Guide for Telegram File Bot

This guide provides detailed instructions for deploying the Telegram File Bot on Railway platform.

## What is Railway?

Railway is a modern cloud hosting platform that allows you to deploy your applications easily and quickly. Railway provides a suitable environment for running Python applications and other applications with support for databases and environment variable management.

## Prerequisites

- A [Railway](https://railway.app/) account
- A [GitHub](https://github.com/) account
- Telegram Bot Token (from BotFather)
- Storage Channel (a private channel to store files)

## Step 1: Set Up Railway Account

1. Visit the [Railway website](https://railway.app/) and click "Login".
2. Sign in using your GitHub account.
3. Complete the registration process and verify your account if required.

## Step 2: Prepare GitHub Repository

1. Fork the bot repository to your GitHub account or upload the code to a new repository.
2. Make sure the repository contains the following files:
   - `requirements.txt`: Contains all required libraries
   - `Procfile`: Tells Railway how to run the application

3. If the `Procfile` doesn't exist, create it in the project's root directory with the following content:
   ```
   web: python run.py --web-only
   worker: python run.py --bot-only
   ```

4. Ensure that the `requirements.txt` file contains all the required libraries. You can create it using the following command (after installing the libraries locally):
   ```
   pip freeze > requirements.txt
   ```

## Step 3: Create a New Project on Railway

1. After logging into Railway, go to the dashboard.
2. Click the "New Project" button in the top right corner.
3. Choose "Deploy from GitHub repo".
4. Select the repository containing the bot code.
5. Click "Deploy Now" and wait for the project to be imported.

## Step 4: Add PostgreSQL Database

1. In your project dashboard on Railway, click the "New" button in the top right corner.
2. Choose "Database".
3. Select "PostgreSQL".
4. Wait for the database to be created.

## Step 5: Configure Environment Variables

1. In your project dashboard on Railway, click on the application service (not the database).
2. Go to the "Variables" tab.
3. Add the following variables:

   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_IDS=123456789
   STORAGE_CHANNEL_ID=-100123456789
   DATABASE_URL=${DATABASE_URL}
   WEB_HOST=0.0.0.0
   WEB_PORT=${PORT}
   WEB_ADMIN_USERNAME=admin
   WEB_ADMIN_PASSWORD=your_secure_password_here
   BACKUP_DIR=backups
   BACKUP_INTERVAL=24
   ```

   Notes:
   - Replace `your_bot_token_here` with your bot token from BotFather.
   - Replace `123456789` with your Telegram ID.
   - Replace `-100123456789` with your storage channel ID.
   - Replace `your_secure_password_here` with a strong password for the admin panel.
   - `${DATABASE_URL}` and `${PORT}` are automatic variables provided by Railway, don't change them.

## Step 6: Initialize the Database

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Deployments" tab.
3. Wait for the initial deployment to complete.
4. Click on the latest deployment.
5. Click the "Shell" button in the top right corner.
6. In the terminal window that appears, run the following command:
   ```
   python init_db.py
   ```
7. Wait for the database initialization process to complete.

## Step 7: Check Bot Status

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Logs" tab.
3. Check the logs to ensure that the bot is running correctly.
4. You should see messages indicating that the bot and web server have started.

## Step 8: Access the Admin Panel

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Settings" tab.
3. In the "Domains" section, you'll find the URL for your application.
4. Click on this link to access the admin panel.
5. Log in using the username and password you specified in the environment variables.

## Step 9: Test the Bot

1. Open Telegram and search for your bot.
2. Send the `/start` command to start using the bot.
3. Make sure the bot responds and works correctly.
4. Test various bot functions such as file uploading and searching.

## Advanced Settings

### Custom Domain Configuration

If you want to use a custom domain for the admin panel:

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Settings" tab.
3. In the "Domains" section, click on "Generate Domain" or "Custom Domain".
4. Follow the instructions to set up the custom domain.

### Automatic Backup Setup

The bot supports automatic backups, but on Railway, you may need to configure external storage for backups:

1. Set up an account on a cloud storage service such as AWS S3 or Google Cloud Storage.
2. Add the necessary environment variables to connect to the storage service.
3. Modify the backup code to save backups in cloud storage.

### Performance Monitoring

Railway provides tools to monitor your application's performance:

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Metrics" tab.
3. Monitor CPU, memory, and network usage.

## Troubleshooting

### Bot Not Responding

1. Check the application logs in the "Logs" tab.
2. Make sure the bot token is correct in the environment variables.
3. Make sure the bot hasn't been blocked by Telegram.
4. Restart the application by clicking "Restart" in the "Settings" tab.

### Database Error

1. Check the application logs in the "Logs" tab.
2. Make sure the `DATABASE_URL` variable is set correctly.
3. Make sure the database is running (check the status of the database service).
4. Try initializing the database again using `python init_db.py` in the terminal.

### Admin Panel Not Working

1. Check the application logs in the "Logs" tab.
2. Make sure the `WEB_HOST` and `WEB_PORT` variables are set correctly.
3. Make sure the web server is running (you should see startup messages in the logs).
4. Check the URL in the "Domains" section and make sure it's correct.

## Updating the Bot

To update the bot on Railway:

1. Update the code in your GitHub repository.
2. Railway will automatically detect the changes and redeploy the application.
3. You can also manually trigger a redeployment by clicking "Redeploy" in the "Deployments" tab.

## Performance Optimization Tips

1. **Memory Usage Optimization**: Monitor memory usage and optimize the code if necessary.
2. **Database Query Optimization**: Make sure database queries are efficient and use appropriate indexes.
3. **Caching**: Use caching to reduce the number of requests to the database.
4. **Worker Adjustment**: You can adjust the number of workers in Gunicorn to optimize performance.

## Scaling Your Bot

As your bot grows in popularity, you may need to scale your application:

1. **Vertical Scaling**: Increase the resources (CPU, memory) allocated to your application.
   - In your project dashboard on Railway, click on the application service.
   - Go to the "Settings" tab.
   - In the "Resources" section, adjust the CPU and memory limits.

2. **Horizontal Scaling**: Run multiple instances of your application.
   - This requires additional configuration and load balancing.
   - Consider using a message queue system like RabbitMQ or Redis for distributing tasks.

## Security Best Practices

1. **Regular Updates**: Keep your bot code and dependencies up to date.
2. **Secure Passwords**: Use strong, unique passwords for the admin panel.
3. **API Key Rotation**: Regularly rotate API keys and tokens.
4. **Access Control**: Implement proper access control in your bot.
5. **Data Encryption**: Encrypt sensitive data stored in the database.

## Backup and Recovery

### Creating Manual Backups

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Deployments" tab.
3. Click on the latest deployment.
4. Click the "Shell" button in the top right corner.
5. Run the following command:
   ```
   python -c "from app.utils.helpers import create_backup; print(create_backup('app/database/bot_database.db', 'backups'))"
   ```

### Restoring from Backup

1. In your project dashboard on Railway, click on the application service.
2. Go to the "Deployments" tab.
3. Click on the latest deployment.
4. Click the "Shell" button in the top right corner.
5. Run the following command:
   ```
   python -c "from app.utils.helpers import restore_backup; restore_backup('backups/your_backup_file.db', 'app/database/bot_database.db')"
   ```
   Replace `your_backup_file.db` with the actual backup file name.

## Monitoring and Logging

Railway provides built-in monitoring and logging capabilities:

1. **Logs**: Access application logs in the "Logs" tab.
2. **Metrics**: Monitor resource usage in the "Metrics" tab.
3. **Alerts**: Set up alerts for important events.

For more advanced monitoring, consider integrating with external services like:
- Sentry for error tracking
- Datadog for comprehensive monitoring
- Grafana for visualization

## Conclusion

You now have a Telegram File Bot running on the Railway platform. You can access the admin panel from anywhere and use the bot on Telegram. Make sure to monitor the bot's performance and update it regularly to ensure the best experience for users.

If you encounter any issues or have questions, refer to the [Railway documentation](https://docs.railway.app/) or open an issue in the bot's GitHub repository.

Happy hosting!