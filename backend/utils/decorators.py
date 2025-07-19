from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from models import User, AuditLog

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if not user.is_active:
                    return jsonify({'error': 'Account is deactivated'}), 401
                
                if user.role not in allowed_roles:
                    # Log unauthorized access attempt
                    AuditLog.log_activity(
                        user_id=current_user_id,
                        action='unauthorized_access',
                        table_name='api',
                        notes=f"Unauthorized access attempt to {request.endpoint}",
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({'error': 'Authorization failed'}), 500
        
        return decorated_function
    return decorator

def permission_required(permission):
    """Decorator to check if user has specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if not user.is_active:
                    return jsonify({'error': 'Account is deactivated'}), 401
                
                if not user.has_permission(permission):
                    # Log unauthorized access attempt
                    AuditLog.log_activity(
                        user_id=current_user_id,
                        action='unauthorized_access',
                        table_name='api',
                        notes=f"Unauthorized access attempt to {request.endpoint} (permission: {permission})",
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({'error': 'Authorization failed'}), 500
        
        return decorated_function
    return decorator

def log_activity(action, table_name=None, record_id=None):
    """Decorator to log user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Log the activity
                current_user_id = get_jwt_identity()
                if current_user_id:
                    AuditLog.log_activity(
                        user_id=current_user_id,
                        action=action,
                        table_name=table_name or 'api',
                        record_id=record_id,
                        notes=f"API call to {request.endpoint}",
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                
                return result
            
            except Exception as e:
                return jsonify({'error': 'Operation failed'}), 500
        
        return decorated_function
    return decorator 