from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
import redis
from celery import Celery

# Import configuration
from config.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
redis_client = None
celery = None

def create_celery(app):
    """Create Celery instance for background tasks"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name='development'):
    """Application factory pattern with enterprise features"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Initialize Redis
    global redis_client
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()  # Test connection
    except Exception as e:
        app.logger.warning(f"Redis connection failed: {e}")
        redis_client = None
    
    # Initialize Celery
    global celery
    celery = create_celery(app)
    
    # Setup CORS with enterprise configuration
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ipms.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('IPMS startup')
    
    # Register blueprints api routes
    from api.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from api.routes.inventory import inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    
    # Import and register other blueprints when they're ready
    # from api.routes.purchase_orders import purchase_orders_bp
    # from api.routes.suppliers import suppliers_bp
    # from api.routes.reports import reports_bp
    # from api.routes.dashboard import dashboard_bp
    # 
    # app.register_blueprint(purchase_orders_bp, url_prefix='/api/purchase-orders')
    # app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    # app.register_blueprint(reports_bp, url_prefix='/api/reports')
    # app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Health check endpoint with comprehensive status
    @app.route('/api/health')
    def health_check():
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': config_name,
            'services': {
                'database': 'connected' if db.engine.pool.checkedin() > 0 else 'disconnected',
                'redis': 'connected' if redis_client and redis_client.ping() else 'disconnected',
                'celery': 'connected' if celery else 'disconnected'
            },
            'message': 'IPMS Enterprise Backend is running!'
        }
        return jsonify(health_status)
    
    # Root endpoint with API documentation
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Inventory & Procurement Management System - Enterprise Edition',
            'version': '2.0.0',
            'environment': config_name,
            'documentation': '/api/docs',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/*',
                'inventory': '/api/inventory/*',
                'purchase_orders': '/api/purchase-orders/*',
                'suppliers': '/api/suppliers/*',
                'reports': '/api/reports/*',
                'dashboard': '/api/dashboard/*',
                'analytics': '/api/analytics/*'
            },
            'features': [
                'JWT Authentication',
                'Role-based Access Control',
                'Audit Logging',
                'Real-time Notifications',
                'Background Task Processing',
                'Caching Layer',
                'Comprehensive API'
            ]
        })
    
    # API Documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        return jsonify({
            'title': 'IPMS API Documentation',
            'version': '2.0.0',
            'authentication': {
                'type': 'JWT Bearer Token',
                'header': 'Authorization: Bearer <token>'
            },
            'endpoints': {
                'auth': {
                    'POST /api/auth/login': 'User login',
                    'POST /api/auth/logout': 'User logout',
                    'POST /api/auth/refresh': 'Refresh token',
                    'POST /api/auth/register': 'Register new user (admin only)',
                    'GET /api/auth/profile': 'Get user profile',
                    'PUT /api/auth/profile': 'Update user profile',
                    'POST /api/auth/change-password': 'Change password'
                }
            }
        })
    
    # Test endpoint
    @app.route('/api/test')
    def test():
        return jsonify({
            'message': 'Enterprise Backend is working!',
            'timestamp': datetime.utcnow().isoformat(),
            'features': 'JWT, CORS, Redis, Celery, SQLAlchemy'
        })
    
    # Protected test endpoint
    @app.route('/api/protected')
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        return jsonify({
            'message': 'This is a protected endpoint',
            'user_id': current_user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'access_level': 'authenticated'
        })
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Resource not found',
            'message': 'The requested resource does not exist',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'Invalid request data',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401,
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions',
            'status_code': 403,
            'timestamp': datetime.utcnow().isoformat()
        }), 403
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        app.logger.info(f'{request.method} {request.url} - {request.remote_addr}')
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting IPMS Enterprise Backend Server...")
    print("📍 Backend URL: http://localhost:5000")
    print("🔗 Health Check: http://localhost:5000/api/health")
    print("📊 API Root: http://localhost:5000/")
    print("📚 API Docs: http://localhost:5000/api/docs")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 
