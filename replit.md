# Dust2Cash

## Overview
Dust2Cash is a Django web application that allows users to convert small crypto balances (under 5 USDT) into M-Pesa or Airtel Money. The platform supports multiple cryptocurrency platforms including Binance, Bybit, and Bitget, with USDT and WorldCoin support.

**Current State:** Application successfully imported and configured for Replit environment. All core functionality is operational.

## Recent Changes
- **November 16, 2025**: Initial GitHub import and Replit environment setup
  - Installed Python 3.11 and Django 4.2.26
  - Configured ALLOWED_HOSTS for Replit's proxy environment
  - Set up Django development server on port 5000
  - Fixed import issues in core/views.py
  - Updated .gitignore for Python/Django best practices

## Project Architecture

### Technology Stack
- **Framework**: Django 4.2.26
- **Language**: Python 3.11
- **Database**: SQLite3 (development)
- **Frontend**: HTML templates with static CSS/JS
- **Email**: Console backend (development mode)

### Project Structure
```
dust2cash/
├── core/                    # Main application
│   ├── templates/           # HTML templates
│   │   ├── auth/            # Authentication pages
│   │   ├── client/          # Client dashboard
│   │   ├── agent/           # Agent portal
│   │   └── landing.html     # Landing page
│   ├── forms.py             # Form definitions
│   ├── views.py             # View logic
│   └── urls.py              # URL routing
├── dust2cash/               # Project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration
├── static/                  # Static assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript
│   └── img/                 # Images
└── manage.py                # Django management script
```

### Key Features
- User authentication (login/signup)
- Landing page with platform information
- Support for multiple crypto platforms (Binance, Bybit, Bitget)
- Support for USDT and WorldCoin
- M-Pesa and Airtel Money payout options
- Transaction fee included in conversion

### Configuration
- **Development Server**: Runs on 0.0.0.0:5000
- **Allowed Hosts**: Configured for all hosts (Replit proxy compatibility)
- **Time Zone**: Africa/Nairobi
- **Email**: Console backend (logs to terminal)

## User Preferences
None specified yet.

## Development Notes
- The application uses SQLite for development
- Email backend is set to console (emails print to terminal)
- Static files are served from the /static/ directory
- All authentication is placeholder - production should integrate Django's full auth system
