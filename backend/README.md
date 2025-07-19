# Inventory & Procurement Management System - Backend

A comprehensive Flask-based backend API for the Inventory & Procurement Management System, designed specifically for African industries and factories.

## 🏗️ Architecture

### Technology Stack
- **Framework**: Flask 2.3.3
- **Database**: PostgreSQL 12+
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **API**: RESTful API with JSON responses
- **Security**: Role-based access control (RBAC)
- **Validation**: Input validation and sanitization
- **Logging**: Comprehensive audit logging

### Database Schema
- **Users**: Authentication and user management
- **Inventory Items**: Stock tracking and management
- **Categories**: Product categorization
- **Locations**: Warehouse and storage locations
- **Purchase Orders**: Procurement workflow
- **Suppliers**: Vendor management
- **Audit Logs**: System activity tracking
- **Notifications**: User alerts and notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python setup_database.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## 📋 API Documentation

### Authentication Endpoints

#### POST /api/auth/login
Login with email and password
```json
{
  "email": "admin@ipms.com",
  "password": "admin123"
}
```

#### POST /api/auth/logout
Logout (requires JWT token)

#### POST /api/auth/refresh
Refresh JWT token

#### GET /api/auth/me
Get current user information

#### PUT /api/auth/profile
Update user profile

#### POST /api/auth/change-password
Change user password

### Inventory Management

#### GET /api/inventory/items
Get all inventory items with pagination

#### POST /api/inventory/items
Create new inventory item

#### GET /api/inventory/items/{id}
Get specific inventory item

#### PUT /api/inventory/items/{id}
Update inventory item

#### DELETE /api/inventory/items/{id}
Delete inventory item

#### POST /api/inventory/items/{id}/add-stock
Add stock to inventory item

#### POST /api/inventory/items/{id}/remove-stock
Remove stock from inventory item

### Purchase Orders

#### GET /api/purchase-orders
Get all purchase orders

#### POST /api/purchase-orders
Create new purchase order

#### GET /api/purchase-orders/{id}
Get specific purchase order

#### PUT /api/purchase-orders/{id}
Update purchase order

#### POST /api/purchase-orders/{id}/approve
Approve purchase order

#### POST /api/purchase-orders/{id}/reject
Reject purchase order

#### POST /api/purchase-orders/{id}/deliver
Mark purchase order as delivered

### Suppliers

#### GET /api/suppliers
Get all suppliers

#### POST /api/suppliers
Create new supplier

#### GET /api/suppliers/{id}
Get specific supplier

#### PUT /api/suppliers/{id}
Update supplier

#### DELETE /api/suppliers/{id}
Delete supplier

### Reports

#### GET /api/reports/inventory
Get inventory reports

#### GET /api/reports/purchase-orders
Get purchase order reports

#### GET /api/reports/suppliers
Get supplier reports

#### GET /api/reports/analytics
Get analytics data

### Dashboard

#### GET /api/dashboard/summary
Get dashboard summary data

#### GET /api/dashboard/metrics
Get key performance metrics

### User Management (Admin Only)

#### GET /api/auth/users
Get all users

#### POST /api/auth/register
Create new user

#### PUT /api/auth/users/{id}
Update user

#### DELETE /api/auth/users/{id}
Deactivate user

## 🔐 Security Features

### Authentication
- JWT-based authentication
- Token refresh mechanism
- Password hashing with bcrypt
- Session management

### Authorization
- Role-based access control (RBAC)
- Permission-based access control
- Admin, Manager, Staff roles
- API endpoint protection

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Audit Logging
- All system activities logged
- User action tracking
- IP address logging
- User agent tracking

## 📊 Database Models

### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20))  # admin, manager, staff
    is_active = db.Column(db.Boolean, default=True)
    # ... other fields
```

### Inventory Item Model
```python
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Numeric(10, 2))
    reorder_level = db.Column(db.Integer, default=10)
    # ... other fields
```

### Purchase Order Model
```python
class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    status = db.Column(db.String(20))  # pending, approved, rejected, delivered
    total_amount = db.Column(db.Numeric(12, 2))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    # ... other fields
```

## 🔧 Configuration

### Environment Variables
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database Configuration
DATABASE_URL=postgresql://ipms_user:ipms_password@localhost:5432/ipms_db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📈 Performance

### Optimization Features
- Database connection pooling
- Query optimization
- Caching with Redis
- Pagination for large datasets
- Efficient indexing

### Monitoring
- Application logging
- Database query logging
- Performance metrics
- Error tracking

## 🔄 Background Tasks

### Celery Integration
- Email notifications
- Report generation
- Data backup
- Scheduled tasks

### Task Examples
```python
@celery.task
def send_low_stock_notification(item_id):
    # Send email notification for low stock items
    pass

@celery.task
def generate_monthly_report():
    # Generate monthly inventory report
    pass
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Test Structure
```
tests/
├── test_auth.py
├── test_inventory.py
├── test_purchase_orders.py
├── test_suppliers.py
└── test_reports.py
```

## 📝 API Response Format

### Success Response
```json
{
  "message": "Operation successful",
  "data": {
    // Response data
  },
  "timestamp": "2025-01-30T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-30T10:30:00Z"
}
```

### Paginated Response
```json
{
  "data": [
    // Array of items
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 100,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🔍 Search and Filtering

### Search Parameters
- `q`: Search query
- `category`: Filter by category
- `location`: Filter by location
- `status`: Filter by status
- `date_from`: Start date
- `date_to`: End date

### Example
```
GET /api/inventory/items?q=steel&category=raw-materials&status=in-stock
```

## 📊 Export Functionality

### Export Formats
- JSON
- CSV
- Excel (XLSX)
- PDF (reports)

### Export Endpoints
```
GET /api/export/inventory
GET /api/export/purchase-orders
GET /api/export/suppliers
```

## 🔐 Security Best Practices

### Implemented Security Measures
1. **Input Validation**: All inputs validated and sanitized
2. **SQL Injection Prevention**: Parameterized queries
3. **XSS Protection**: Output encoding
4. **CSRF Protection**: Token-based protection
5. **Rate Limiting**: API rate limiting
6. **Secure Headers**: Security headers implementation
7. **Password Security**: Strong password requirements
8. **Session Security**: Secure session management

## 📞 Support

### Contact Information
- **Developer**: Aman Abraha Kasa
- **Organization**: African Leadership University (ALU)
- **Project**: Inventory & Procurement Management System

### Documentation
- API documentation available at `/api/docs` (when implemented)
- Database schema documentation
- Deployment guides
- Troubleshooting guides

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production Ready 