# IPMS Project Structure

This document provides a comprehensive overview of the organized project structure for the Inventory & Procurement Management System.

## 📁 Root Directory Structure

```
ipms-project/
├── frontend/                 # Frontend application
├── backend/                  # Backend API server
├── docs/                     # Project documentation
├── scripts/                  # Utility scripts
├── README.md                 # Main project README
├── PROJECT_STRUCTURE.md      # This file
└── start_backend.sh          # Backend startup script
```

## 🎨 Frontend Structure

```
frontend/
├── index.html               # Landing page
├── login.html               # Login page
├── package.json             # Frontend dependencies
├── README.md                # Frontend documentation
├── pages/
│   └── dashboard.html       # Main dashboard
├── assets/
│   ├── css/
│   │   ├── styles.css       # Main styles
│   │   └── dashboard.css    # Dashboard styles
│   ├── js/
│   │   ├── script.js        # Main JavaScript
│   │   └── dashboard.js     # Dashboard functionality
│   └── images/              # Image assets
├── components/              # Reusable components
└── utils/                   # Utility functions
```

### Frontend Files Description

#### HTML Files
- **`index.html`**: Landing page with features, about, and contact sections
- **`login.html`**: User authentication page
- **`pages/dashboard.html`**: Main application dashboard

#### CSS Files
- **`assets/css/styles.css`**: Global styles, landing page, and login styles
- **`assets/css/dashboard.css`**: Dashboard-specific styles and components

#### JavaScript Files
- **`assets/js/script.js`**: Main functionality, login handling, and utilities
- **`assets/js/dashboard.js`**: Dashboard functionality, charts, and data management

## 🔧 Backend Structure

```
backend/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── env.example              # Environment variables template
├── setup_database.py        # Database setup script
├── README.md                # Backend documentation
├── api/
│   ├── __init__.py          # API package
│   ├── routes/
│   │   └── auth.py          # Authentication routes
│   ├── models/
│   │   ├── __init__.py      # Models package
│   │   ├── user.py          # User model
│   │   ├── inventory.py     # Inventory models
│   │   ├── purchase_order.py # Purchase order models
│   │   ├── supplier.py      # Supplier model
│   │   ├── audit_log.py     # Audit log model
│   │   └── notification.py  # Notification model
│   └── services/
│       ├── __init__.py      # Services package
│       └── inventory_service.py # Inventory business logic
├── config/
│   └── config.py            # Application configuration
├── utils/
│   ├── __init__.py          # Utils package
│   ├── decorators.py        # Custom decorators
│   └── helpers.py           # Helper functions
├── tests/                   # Test files
├── scripts/                 # Utility scripts
└── docs/                    # Backend documentation
```

### Backend Files Description

#### Core Application
- **`app.py`**: Main Flask application with routes and configuration
- **`requirements.txt`**: Python package dependencies
- **`setup_database.py`**: Database initialization script

#### API Layer
- **`api/routes/`**: RESTful API endpoints
- **`api/models/`**: Database models and ORM definitions
- **`api/services/`**: Business logic layer

#### Configuration
- **`config/config.py`**: Application settings and environment configuration
- **`env.example`**: Template for environment variables

#### Utilities
- **`utils/decorators.py`**: Custom decorators for authentication and authorization
- **`utils/helpers.py`**: Helper functions for validation, formatting, etc.

## 📊 Database Models

### Core Models
1. **User**: Authentication, roles, and user management
2. **InventoryItem**: Stock items with SKU, quantities, locations
3. **Category**: Product categorization
4. **Location**: Warehouse and storage locations
5. **PurchaseOrder**: Procurement workflow management
6. **Supplier**: Vendor information and relationships
7. **AuditLog**: System activity tracking
8. **Notification**: User alerts and system notifications

## 🔄 Data Flow

### Frontend to Backend
1. **Authentication**: Login → JWT token → API calls
2. **Inventory Management**: CRUD operations via REST API
3. **Purchase Orders**: Workflow management through API
4. **Reports**: Data retrieval and analytics

### Backend Processing
1. **Routes**: Handle HTTP requests
2. **Services**: Business logic and validation
3. **Models**: Database operations
4. **Utils**: Helper functions and utilities

## 🚀 Development Workflow

### Frontend Development
```bash
cd frontend
python -m http.server 8000
# Access at http://localhost:8000
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# API available at http://localhost:5000
```

### Full Stack Development
```bash
# Start backend
./start_backend.sh

# Start frontend (in another terminal)
cd frontend
python -m http.server 8000
```

## 📝 File Naming Conventions

### Frontend
- **HTML**: lowercase with hyphens (e.g., `dashboard.html`)
- **CSS**: lowercase with hyphens (e.g., `dashboard.css`)
- **JavaScript**: lowercase with hyphens (e.g., `dashboard.js`)
- **Images**: descriptive names with hyphens

### Backend
- **Python files**: snake_case (e.g., `inventory_service.py`)
- **Classes**: PascalCase (e.g., `InventoryService`)
- **Functions**: snake_case (e.g., `get_inventory_items`)
- **Variables**: snake_case (e.g., `inventory_items`)

## 🔍 Key Features by Directory

### Frontend Features
- **Landing Page**: Marketing and information
- **Login System**: User authentication
- **Dashboard**: Main application interface
- **Responsive Design**: Mobile-friendly layout
- **Interactive Charts**: Data visualization

### Backend Features
- **RESTful API**: Complete CRUD operations
- **Authentication**: JWT-based security
- **Database Management**: PostgreSQL with SQLAlchemy
- **Business Logic**: Service layer architecture
- **Audit Logging**: Complete activity tracking
- **Notifications**: Real-time alerts

## 🛠️ Development Tools

### Frontend Tools
- **HTML5/CSS3/JavaScript**: Core technologies
- **Font Awesome**: Icons
- **Live Server**: Development server

### Backend Tools
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **PostgreSQL**: Database
- **JWT**: Authentication
- **Redis**: Caching (optional)

## 📈 Scalability Considerations

### Frontend Scalability
- Modular component structure
- Lazy loading for large datasets
- Optimized assets and caching
- Progressive enhancement

### Backend Scalability
- Service layer architecture
- Database connection pooling
- API rate limiting
- Caching strategies
- Background task processing

## 🔒 Security Implementation

### Frontend Security
- Input validation
- XSS prevention
- Secure file uploads
- HTTPS enforcement

### Backend Security
- JWT authentication
- Role-based access control
- Input sanitization
- SQL injection prevention
- Audit logging

## 📚 Documentation Structure

### Project Documentation
- **README.md**: Main project overview
- **PROJECT_STRUCTURE.md**: This file
- **frontend/README.md**: Frontend-specific docs
- **backend/README.md**: Backend-specific docs

### API Documentation
- **Backend README**: Complete API reference
- **Code Comments**: Inline documentation
- **Examples**: Usage examples

## 🎯 Next Steps for Organization

### Immediate Improvements
1. Add more service layer files for other modules
2. Create comprehensive test suite
3. Add API documentation with Swagger
4. Implement CI/CD pipeline

### Future Enhancements
1. Microservices architecture
2. Docker containerization
3. Kubernetes deployment
4. Monitoring and logging
5. Performance optimization

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready 