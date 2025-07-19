# 🏢 IPMS Enterprise - Inventory & Procurement Management System

A professional, enterprise-grade web application for comprehensive inventory and procurement management. Built with modern technologies and designed for scalability, security, and performance.

![IPMS Enterprise](https://img.shields.io/badge/Version-2.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![Frontend](https://img.shields.io/badge/Frontend-HTML5/CSS3/JS-orange)

## 🚀 Features

### 🔐 Authentication & Security
- **JWT-based Authentication** with refresh tokens
- **Role-based Access Control** (Admin, Manager, Staff)
- **Password Hashing** with bcrypt
- **Session Management** with secure cookies
- **CORS Protection** for cross-origin requests
- **Input Validation** and sanitization

### 📊 Dashboard & Analytics
- **Real-time Dashboard** with live statistics
- **Interactive Charts** using Chart.js
- **Inventory Trends** visualization
- **Category Distribution** analysis
- **Performance Metrics** tracking
- **Responsive Design** for all devices

### 📦 Inventory Management
- **Item Tracking** with SKU management
- **Stock Level Monitoring** with alerts
- **Category Organization** system
- **Location Management** for warehouses
- **Price Tracking** and history
- **Barcode Support** (planned)

### 🛒 Purchase Order Management
- **Order Creation** and approval workflow
- **Supplier Integration** for seamless ordering
- **Status Tracking** (Draft, Pending, Approved, Delivered)
- **Cost Analysis** and reporting
- **Automated Notifications** for status changes

### 👥 Supplier Management
- **Supplier Profiles** with contact information
- **Performance Tracking** and ratings
- **Contract Management** system
- **Communication History** logging
- **Supplier Analytics** and insights

### 📈 Reporting & Analytics
- **Custom Report Generation** in multiple formats
- **Data Export** (PDF, Excel, CSV)
- **Trend Analysis** and forecasting
- **Performance Dashboards** for KPIs
- **Audit Logging** for compliance

### 🔔 Notifications & Alerts
- **Real-time Notifications** for important events
- **Email Notifications** for critical alerts
- **Low Stock Alerts** with configurable thresholds
- **Order Status Updates** automatic notifications
- **System Health Monitoring**

### 🛠️ System Features
- **Background Task Processing** with Celery
- **Caching Layer** with Redis
- **File Upload** support for documents
- **Search Functionality** across all modules
- **Keyboard Shortcuts** for power users
- **Dark/Light Theme** support (planned)

## 🏗️ Architecture

### Backend (Python/Flask)
```
backend/
├── app.py                 # Main Flask application
├── config/
│   └── config.py         # Configuration management
├── api/
│   ├── models/           # Database models
│   ├── routes/           # API endpoints
│   └── services/         # Business logic
├── utils/                # Utility functions
├── static/               # Static files
├── templates/            # HTML templates
└── tests/                # Unit tests
```

### Frontend (HTML5/CSS3/JavaScript)
```
frontend/
├── index.html            # Login page
├── dashboard.html        # Main dashboard
├── signup.html           # Registration page
├── assets/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Images and icons
└── components/          # Reusable components
```

## 🛠️ Technology Stack

### Backend
- **Python 3.10+** - Core programming language
- **Flask 2.3.3** - Web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Celery** - Background task processing
- **JWT** - Authentication tokens
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid/Flexbox
- **JavaScript (ES6+)** - Interactive functionality
- **Chart.js** - Data visualization
- **Font Awesome** - Icon library
- **Google Fonts** - Typography

### DevOps & Tools
- **Git** - Version control
- **Docker** - Containerization (planned)
- **Nginx** - Web server (production)
- **Gunicorn** - WSGI server
- **Supervisor** - Process management

## 📋 Prerequisites

Before running the application, ensure you have:

- **Python 3.10 or higher**
- **PostgreSQL 12 or higher**
- **Redis 6 or higher**
- **Node.js 16 or higher** (for development tools)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ipms-enterprise.git
cd ipms-enterprise
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment
```bash
cp env.example .env
# Edit .env with your database and Redis credentials
```

#### Database Setup
```bash
# Create PostgreSQL database
createdb ipms_db

# Run database migrations
python setup_database.py
```

#### Start Backend Server
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### 3. Frontend Setup

#### Start Frontend Server
```bash
cd frontend
python3 -m http.server 8000
```

The frontend will be available at `http://localhost:8000`

### 4. Access the Application

1. Open your browser and navigate to `http://localhost:8000`
2. Use the default credentials:
   - **Email:** admin@ipms.com
   - **Password:** admin123

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ipms_db

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# CORS Origins
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Database Configuration

The application uses PostgreSQL as the primary database. Configure your database connection in the `.env` file.

### Redis Configuration

Redis is used for caching and session storage. Ensure Redis is running and accessible.

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

### Dashboard Endpoints

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/activities` - Get recent activities
- `GET /api/dashboard/notifications` - Get user notifications

### Health Check

- `GET /api/health` - System health status
- `GET /` - API root with documentation

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
# Add frontend testing framework (Jest, etc.)
```

## 📦 Deployment

### Production Deployment

1. **Set up a production server** (Ubuntu 20.04+ recommended)
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip postgresql redis-server nginx
   ```

3. **Configure PostgreSQL:**
   ```bash
   sudo -u postgres createdb ipms_production
   sudo -u postgres createuser ipms_user
   ```

4. **Set up the application:**
   ```bash
   git clone <repository>
   cd ipms-enterprise/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure environment variables** for production

6. **Set up Gunicorn:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

7. **Configure Nginx** as a reverse proxy

8. **Set up SSL** with Let's Encrypt

### Docker Deployment (Planned)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🔒 Security Features

- **JWT Authentication** with secure token handling
- **Password Hashing** using bcrypt
- **CORS Protection** for cross-origin requests
- **Input Validation** and sanitization
- **SQL Injection Prevention** through ORM
- **XSS Protection** with proper output encoding
- **CSRF Protection** for form submissions
- **Rate Limiting** for API endpoints
- **Audit Logging** for security events

## 📊 Performance Optimization

- **Database Indexing** for fast queries
- **Redis Caching** for frequently accessed data
- **Background Task Processing** with Celery
- **Static File Compression** and caching
- **Lazy Loading** for large datasets
- **Pagination** for list views
- **CDN Integration** for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Write tests for new features
- Update documentation as needed
- Ensure code passes linting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation:** Check this README and inline code comments
- **Issues:** Create an issue on GitHub for bugs or feature requests
- **Discussions:** Use GitHub Discussions for questions and ideas

### Common Issues

#### Backend Connection Issues
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check Redis connection: `redis-cli ping`
- Verify environment variables in `.env`

#### Frontend Issues
- Clear browser cache and cookies
- Check browser console for JavaScript errors
- Ensure backend is running on port 5000

#### Database Issues
- Run database migrations: `python setup_database.py`
- Check database connection settings
- Verify PostgreSQL service is running

## 🗺️ Roadmap

### Version 2.1 (Q2 2024)
- [ ] Mobile app development
- [ ] Advanced reporting features
- [ ] Barcode scanning integration
- [ ] Multi-language support

### Version 2.2 (Q3 2024)
- [ ] AI-powered demand forecasting
- [ ] Advanced analytics dashboard
- [ ] Integration with ERP systems
- [ ] Advanced workflow automation

### Version 3.0 (Q4 2024)
- [ ] Microservices architecture
- [ ] Real-time collaboration features
- [ ] Advanced security features
- [ ] Cloud-native deployment

## 🙏 Acknowledgments

- **Flask Community** for the excellent web framework
- **Chart.js** for beautiful data visualization
- **Font Awesome** for the comprehensive icon library
- **Open Source Community** for inspiration and tools

---

**Built with ❤️ for enterprise inventory management**

*For questions, support, or contributions, please reach out to the development team.* 