# Dust2Cash

**Dust2Cash** is a web platform that enables users to convert cryptocurrency ("dust") into local currency (Kenyan Shillings) with secure, fast payouts via mobile money services like M-Pesa.

## 🌍 SDG Alignment

This project supports the following United Nations Sustainable Development Goals:

- **SDG 8: Decent Work and Economic Growth** – Provides economic opportunity through digital finance.
- **SDG 9: Industry, Innovation and Infrastructure** – Leverages fintech innovation to build resilient infrastructure.
- **SDG 10: Reduced Inequalities** – Enables financial inclusion for underserved populations.

## 🛠️ Tech Stack

| Component       | Technology                      |
|-----------------|---------------------------------|
| Backend         | Django 4.2+                     |
| Database        | PostgreSQL (SQLite for dev)     |
| Payments        | Daraja API (M-Pesa)             |
| Static Files    | WhiteNoise                      |
| Frontend        | HTML/CSS/JavaScript             |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL (optional for production)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Cheecheez101/Dust2Cash.git
   cd Dust2Cash
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env  # TODO: Create .env.example with required variables
   ```
   
   Required environment variables:
   - `SECRET_KEY` – Django secret key
   - `DEBUG` – Set to `False` in production
   - `ALLOWED_HOSTS` – Comma-separated list of allowed hosts
   - `DATABASE_URL` – PostgreSQL connection string (for production)
   - `DARAJA_CONSUMER_KEY` – M-Pesa API consumer key (TODO: integrate)
   - `DARAJA_CONSUMER_SECRET` – M-Pesa API consumer secret (TODO: integrate)

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Open your browser:**
   Navigate to `http://localhost:8000` to see the landing page.

## 📁 Project Structure

```
Dust2Cash/
├── core/                # Main application (auth, transactions, agents)
├── landing/             # Landing page app
├── dust2cash/           # Django project settings
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── requirements.txt     # Python dependencies
└── manage.py            # Django management script
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

> **TODO:** 
> - Integrate Daraja API for M-Pesa payouts
> - Add real authentication with email verification
> - Set up PostgreSQL for production
> - Add comprehensive test coverage
