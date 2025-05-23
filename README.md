# Distributed Order Fulfillment Backend

This project simulates a distributed, production-grade backend system for handling product inventory, asynchronous order lifecycle processing, stale order detection, and concurrent bulk order handling.

---

## 🚀 Features

- ✅ Product and Category Management
- ✅ REST APIs for Products, Orders, and Categories
- ✅ Async Order Lifecycle via Celery (Pending → Delivered)
- ✅ Order History Tracking
- ✅ Stale Order Detection (auto-flagging stuck orders)
- ✅ Bulk Order Submission with Validation
- ✅ Celery + Redis based async processing

---

## 🧱 Tech Stack

- **Django**: Provides a robust ORM and admin for rapid backend development.
- **Django REST Framework (DRF)**: Enables fast, flexible API development with browsable interfaces and easy serialization.
- **Celery**: Manages asynchronous tasks like order lifecycle transitions and stale detection, decoupling business logic from the request cycle.
- **Redis**: Used as a high-speed message broker for Celery tasks.
- **Python 3.11+**: Offers improved performance and async capabilities.

---

## ⚙️ Setup Instructions

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/order-fulfillment-backend.git
cd order-fulfillment-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Start Redis (in WSL Ubuntu)

```bash
sudo service redis-server start
redis-cli ping  # Should return 'PONG'
```

### 3. Apply Migrations & Seed Initial Data

```bash
python manage.py migrate
python manage.py shell
```

Paste this in the shell to add some data:

```python
from inventory.models import Category, Product
cat = Category.objects.create(name="Electronics")
Product.objects.create(name="Phone", description="Smartphone", price=299.99, stock=10, category=cat)
Product.objects.create(name="Laptop", description="Gaming Laptop", price=999.99, stock=5, category=cat)
exit()
```

### 4. Start Django + Celery

```bash
python manage.py runserver
# In another terminal:
celery -A backend worker --loglevel=info --pool=solo
```

---

## 📡 API Endpoints
You can also check out the postman API documentation [here](https://documenter.getpostman.com/view/15226010/2sB2qajgyj)

### 🔍 Category API

- `GET /api/inventory/categories/` → List categories

### 🛒 Product API

- `GET /api/inventory/products/` → List products

### 📦 Order API

- `GET /api/inventory/orders/` → List orders
- `GET /api/inventory/orders/<id>/history/` → Retrieve order by ID

---

### 🚚 Order Lifecycle API

- `POST /api/inventory/orders/` → Create a single order
```json
{
  "customer_name": "Alice",
  "customer_email": "alice@example.com",
  "customer_phone": "1234567890",
  "delivery_address": "123 Main St",
  "items": [
    { "product_id": 1, "quantity": 2 }
  ]
}
```

- `POST /api/inventory/orders/bulk/` → Create multiple orders
```json
[
  {
    "customer_name": "Bob",
    "customer_email": "bob@example.com",
    "customer_phone": "9876543210",
    "delivery_address": "456 Elm St",
    "items": [{ "product_id": 1, "quantity": 1 }]
  }
]
```

---

### ⏳ Delayed + History APIs

- `GET /api/inventory/orders/delayed/` → View orders stuck in `processing` or `shipped` beyond 1 hour
- `GET /api/inventory/orders/<order_id>/history/` → See all status transitions for an order

---

## 🧪 Postman Testing Notes

- Always set header: `Content-Type: application/json`
- You can simulate stuck orders by manually editing `last_transition_time`
- Lifecycle runs automatically after creation via Celery

---

## 🧠 Design Highlights

- Celery enables scalable async workflows decoupled from user API calls.
- Redis acts as a fast and reliable message broker.
- The system safely handles bulk inserts with stock validation.
- Custom model-based transition logging tracks order status for auditability.
- Easily extendable to use ElasticSearch, GraphQL, or containerization.
- The application is configured to use the Asia/Dhaka timezone for all timestamp-related fields and displays. To change this edit TIME_ZONE variable in backend/settings.py

---

## 👤 Admin Access

```bash
python manage.py createsuperuser
```

Access: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 📬 License

MIT
