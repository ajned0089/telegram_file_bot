# Telegram File Bot Setup Guide

This guide will help you set up and run the Telegram File Bot.

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from BotFather)
- Storage Channel (a private channel to store files)

## Step 1: Create a Telegram Bot

1. Open Telegram and search for @BotFather
2. Send the command `/newbot` to create a new bot
3. Follow the instructions to set a name and username for your bot
4. Once created, BotFather will give you a token. Save this token for later use.
5. Set bot commands by sending `/setcommands` to BotFather, selecting your bot, and pasting:
   ```
   start - Start the bot
   help - Show help
   upload - Upload a file
   myfiles - View your files
   search - Search for files
   settings - Change settings
   language - Change language
   myref - Your referral link
   cancel - Cancel current operation
   ```

## Step 2: Create a Storage Channel

1. Create a new private channel in Telegram
2. Add your bot as an administrator with full permissions:
   - Post Messages
   - Edit Messages
   - Delete Messages
   - Invite Users via Link
3. Send a message to the channel
4. Forward that message to @username_to_id_bot to get the channel ID
5. Note down the channel ID (it should start with -100 for private channels)

## Step 3: Install the Bot

1. Clone the repository or extract the files to a directory
2. Open a terminal/command prompt and navigate to the bot directory
3. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Run the installation script:
   ```
   python install.py
   ```
6. This will install dependencies and create necessary directories

## Step 4: Configure the Bot

1. Edit the `.env` file with your settings:
   - `BOT_TOKEN`: Your Telegram bot token from BotFather
   - `ADMIN_IDS`: Your Telegram user ID (you can get it from @userinfobot)
   - `STORAGE_CHANNEL_ID`: The ID of your storage channel (with -100 prefix)
   - `DATABASE_URL`: Database connection string (default is SQLite)
   - `WEB_HOST`: Host for the web admin panel (default is 0.0.0.0)
   - `WEB_PORT`: Port for the web admin panel (default is 8000)
   - `WEB_ADMIN_USERNAME`: Username for the web admin panel
   - `WEB_ADMIN_PASSWORD`: Password for the web admin panel
   - `BACKUP_DIR`: Directory for backups (default is "backups")
   - `BACKUP_INTERVAL`: Backup interval in hours (default is 24)

## Step 5: Initialize the Database

1. Run the database initialization script:
   ```
   python run.py --init-db
   ```
2. This will create the database and add initial categories, formats, and settings

## Step 6: Run the Bot

1. Run the bot:
   ```
   python run.py
   ```
2. This will start both the Telegram bot and the web admin panel
3. To run only the bot:
   ```
   python run.py --bot-only
   ```
4. To run only the web admin panel:
   ```
   python run.py --web-only
   ```

## Step 7: Access the Web Admin Panel

1. Open a web browser and go to:
   ```
   http://localhost:8000
   ```
   (or the IP address of your server if running remotely)
2. Log in with the username and password you set in the `.env` file

## Step 8: Start Using the Bot

1. Open Telegram and search for your bot
2. Send the `/start` command to start using the bot
3. Use the `/help` command to see available commands

## Advanced Configuration

### Setting Up Required Subscription Channels

1. Log in to the web admin panel
2. Go to the "Subscriptions" section
3. Click "Add Channel"
4. Enter the channel ID, name, and invite link
5. Set "Is Required" to true if users must subscribe to this channel to use the bot

### Customizing Categories and Formats

1. Log in to the web admin panel
2. Go to the "Categories" or "Formats" section
3. Add, edit, or remove categories and formats as needed
4. Categories can have subcategories for better organization

### Setting Up File Password Protection

1. Log in to the web admin panel
2. Go to the "Settings" section
3. Set "password_protection" to "true" to enable password protection for files
4. Users will be able to set passwords when uploading files

### Enabling/Disabling Public Uploads

1. Log in to the web admin panel
2. Go to the "Settings" section
3. Set "allow_public_upload" to "true" to allow all users to upload files
4. Set "allow_public_upload" to "false" to restrict uploads to admins and moderators only

## Troubleshooting

### Bot Doesn't Respond

1. Check that the bot token in the `.env` file is correct
2. Make sure the bot is running (`python run.py`)
3. Check the logs for any errors
4. Restart the bot if necessary

### Files Aren't Being Uploaded

1. Check that the bot has the necessary permissions in the storage channel
2. Verify that the storage channel ID in the `.env` file is correct
3. Check if the user has permission to upload files
4. Check the logs for any errors during the upload process

### Web Admin Panel Doesn't Work

1. Check that the port specified in the `.env` file is not being used by another application
2. Make sure the web server is running (`python run.py` or `python run.py --web-only`)
3. Try accessing the panel using a different browser
4. Check the logs for any errors

### Database Issues

1. Check that the database file exists and is not corrupted
2. Try initializing the database again (`python run.py --init-db`)
3. Restore from a backup if available

## Backup and Restore

### Automatic Backups

- The bot automatically creates backups according to the interval set in the `.env` file
- Backups are stored in the directory specified by `BACKUP_DIR`

### Manual Backups

1. Log in to the web admin panel
2. Go to the "Backups" section
3. Click "Create Backup"
4. The backup will be created and added to the list

### Restoring from Backup

1. Log in to the web admin panel
2. Go to the "Backups" section
3. Find the backup you want to restore
4. Click "Restore"
5. Confirm the restoration

## Security Recommendations

1. Use a strong password for the web admin panel
2. Run the bot behind a reverse proxy with SSL/TLS encryption for the web admin panel
3. Regularly backup your database
4. Keep your Python and dependencies up to date
5. Consider using a more robust database like PostgreSQL for production use

## Additional Resources

- For more detailed information, see the [Documentation](DOCUMENTATION.md)
- For deployment options, see the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- For customization options, see the [Customization Guide](CUSTOMIZATION_GUIDE.md)