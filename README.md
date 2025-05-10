# 💸 Payapp

**Payapp** is a secure, modern digital payment application built with a Django backend and a React frontend. It allows users to send and request money, view transaction history, manage wallets, and receive notifications — all in a smooth and intuitive interface.

---

## 🚀 Features

- User authentication (login/register)
- Send and request payments
- Real-time transaction tracking
- Currency conversion support
- Admin dashboard for superusers
- Responsive, animated frontend (React + Tailwind CSS)

---

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework
- **Frontend:** React, Tailwind CSS
- **Database:** SQLite (default), but easily swappable with PostgreSQL
- **API:** RESTful architecture

---

## 📦 Installation

### 1. Clone the repository

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
