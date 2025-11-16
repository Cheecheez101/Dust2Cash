# Dust2Cash

## Overview
Dust2Cash is a fully functional Django web application that allows users to convert small crypto balances (even under 5 USDT) into M-Pesa or Airtel Money. The platform supports multiple cryptocurrency platforms including Binance, Bybit, and Bitget, with USDT and WorldCoin support.

**Current State:** Complete, production-ready application with full transaction workflow, user authentication, agent management, and email notifications.

## Recent Changes
- **November 16, 2025**: Complete implementation of all core features
  - Installed Python 3.11 and Django 4.2.26 with Gunicorn for deployment
  - Configured ALLOWED_HOSTS for Replit's proxy environment
  - Set up Django development server on port 5000
  - Implemented complete database models (ClientProfile, AgentProfile, Transaction, AgentRequest)
  - Built full authentication system with email-based signup/login
  - Created client dashboard with transaction management
  - Implemented agent portal with online/offline status and transaction handling
  - Added role-based access control with custom decorators
  - Integrated email notification system for all transaction events
  - Created 11+ HTML templates with Bootstrap 5 styling
  - Set up Django admin interface for all models
  - Added management command to create agent users
  - Configured deployment settings for production use

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

**Client Features:**
- Email-based authentication (signup/login)
- Complete profile management with required fields validation
- Dashboard showing agent online status and transaction history
- Transaction creation with real-time exchange rate calculation (1 USDT = KSH 100)
- Support for Binance, Bybit, and Bitget platforms
- Support for USDT and WorldCoin currencies
- M-Pesa and Airtel Money payout options
- Agent request system with 15-minute timeout
- Email notifications at each transaction step
- Transfer address display and copy functionality

**Agent Features:**
- Dedicated agent portal with authentication
- Online/offline status toggle
- Pending request management with expiry tracking
- Active transaction dashboard
- Provide transfer addresses to clients
- Confirm crypto receipt
- Process and confirm payments
- Completed transaction history
- Auto-refresh for real-time updates

**System Features:**
- Role-based access control (client vs agent separation)
- Comprehensive email notifications with transaction details
- Automated status transitions through transaction lifecycle
- Exchange rate and fee calculations
- Transaction timeout management
- Django admin interface for system management

### Configuration
- **Development Server**: Runs on 0.0.0.0:5000
- **Allowed Hosts**: Configured for all hosts (Replit proxy compatibility)
- **Time Zone**: Africa/Nairobi
- **Email**: Console backend (logs to terminal)

## User Preferences
None specified yet.

## Development Notes
- The application uses SQLite for development
- Email backend is set to console in development (emails print to terminal)
- Static files are served from the /static/ directory
- Production deployment configured with Gunicorn on autoscale
- Agent users can be created using: `python manage.py create_agent`
- Default agent credentials: username=agent, password=agent123

## Transaction Workflow
1. **Client Signup** → Complete profile with required details
2. **Check Agent Status** → View if agent is online on dashboard
3. **Create Transaction** → Select platform, currency, amount, payment method
4. **Agent Assignment** → If online: immediate; If offline: request with 15-min timeout
5. **Receive Address** → Agent provides crypto transfer address
6. **Transfer Crypto** → Client sends funds to provided address
7. **Confirmation** → Agent confirms receipt of crypto
8. **Payment** → Agent sends M-Pesa/Airtel Money to client
9. **Completion** → Transaction marked as completed, email sent

## API & Integration Notes
- Exchange Rate: Fixed at 1 USDT = KSH 100 (configurable in models)
- Transaction Fee: Included in exchange calculation
- Minimum Amount: 5 USDT (adjustable)
- Supported Platforms: Binance, Bybit, Bitget
- Supported Currencies: USDT, WorldCoin
- Payment Methods: M-Pesa, Airtel Money

## Security & Access Control
- Role-based decorators prevent unauthorized access
- Clients cannot access agent endpoints
- Agents cannot access client-only features
- All forms use CSRF protection
- User authentication required for all transactions
