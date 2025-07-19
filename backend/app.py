from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import os

# Import configuration
from config.config import config

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt = JWTManager(app)
    
    # Setup CORS
    CORS(app, origins=['http://localhost:8000', 'http://127.0.0.1:8000'])
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'message': 'IPMS Backend is running!'
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Inventory & Procurement Management System API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/*',
                'inventory': '/api/inventory/*',
                'purchase_orders': '/api/purchase-orders/*',
                'suppliers': '/api/suppliers/*',
                'reports': '/api/reports/*',
                'dashboard': '/api/dashboard/*'
            }
        })
    
    # Test endpoint
    @app.route('/api/test')
    def test():
        return jsonify({
            'message': 'Backend is working!',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Protected test endpoint
    @app.route('/api/protected')
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        return jsonify({
            'message': 'This is a protected endpoint',
            'user_id': current_user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting IPMS Backend Server...")
    print("📍 Backend URL: http://localhost:5000")
    print("🔗 Health Check: http://localhost:5000/api/health")
    print("📊 API Root: http://localhost:5000/")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 