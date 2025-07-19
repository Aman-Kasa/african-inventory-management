from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import logging

from api.models.user import User
from api.models.audit_log import AuditLog
# db will be accessed via current_app.extensions['sqlalchemy'].db when needed
from utils.decorators import role_required

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.get_by_email(email)
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.update_last_login()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Log the login
        AuditLog.log_activity(
            user_id=user.id,
            action='login',
            table_name='users',
            record_id=user.id,
            notes=f"User logged in successfully",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'expires_in': 3600  # 1 hour
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            # Log the logout
            AuditLog.log_activity(
                user_id=current_user_id,
                action='logout',
                table_name='users',
                record_id=current_user_id,
                notes=f"User logged out",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
        
        return jsonify({'message': 'Logout successful'}), 200
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh JWT token endpoint"""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token,
            'expires_in': 3600
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def register():
    """User registration endpoint (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username already exists
        if User.get_by_username(data['username']):
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email already exists
        if User.get_by_email(data['email']):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Validate role
        if data['role'] not in ['admin', 'manager', 'staff']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            is_verified=data.get('is_verified', False)
        )
        new_user.set_password(data['password'])
        
        db = current_app.extensions['sqlalchemy'].db
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user creation
        current_user_id = get_jwt_identity()
        AuditLog.log_activity(
            user_id=current_user_id,
            action='create_user',
            table_name='users',
            record_id=new_user.id,
            notes=f"Created new user: {new_user.username}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"User registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'User creation failed'}), 500

@auth_bp.route('/signup', methods=['POST'])
def public_signup():
    """Public employee signup endpoint (role=staff only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if username already exists
        if User.get_by_username(data['username']):
            return jsonify({'error': 'Username already exists'}), 400

        # Check if email already exists
        if User.get_by_email(data['email']):
            return jsonify({'error': 'Email already exists'}), 400

        # Only allow role=staff for public signup
        role = 'staff'

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            is_verified=False
        )
        new_user.set_password(data['password'])

        db = current_app.extensions['sqlalchemy'].db
        db.session.add(new_user)
        db.session.commit()

        # Log the user creation (optional, if AuditLog is available)
        # AuditLog.log_activity(
        #     user_id=new_user.id,
        #     action='public_signup',
        #     table_name='users',
        #     record_id=new_user.id,
        #     notes=f"User self-registered: {new_user.username}",
        #     ip_address=request.remote_addr,
        #     user_agent=request.headers.get('User-Agent')
        # )

        return jsonify({
            'message': 'Signup successful. Please wait for admin verification (if required).',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        current_app.logger.error(f"Public signup error: {str(e)}")
        return jsonify({'error': 'Signup failed'}), 500

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    """Get or update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'user': user.to_dict()
            }), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                # Check if email is already taken
                existing_user = User.get_by_email(data['email'])
                if existing_user and existing_user.id != current_user_id:
                    return jsonify({'error': 'Email already exists'}), 400
                user.email = data['email']
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log the profile update
            AuditLog.log_activity(
                user_id=current_user_id,
                action='update_profile',
                table_name='users',
                record_id=current_user_id,
                notes=f"Updated profile information",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }), 200
    
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'error': 'Profile operation failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the password change
        AuditLog.log_activity(
            user_id=current_user_id,
            action='change_password',
            table_name='users',
            record_id=current_user_id,
            notes=f"Password changed successfully",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_users():
    """Get all users (admin only)"""
    try:
        users = User.get_active_users()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@role_required(['admin'])
def manage_user(user_id):
    """Manage specific user (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'user': user.to_dict()
            }), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                existing_user = User.get_by_email(data['email'])
                if existing_user and existing_user.id != user_id:
                    return jsonify({'error': 'Email already exists'}), 400
                user.email = data['email']
            if 'role' in data:
                if data['role'] not in ['admin', 'manager', 'staff']:
                    return jsonify({'error': 'Invalid role'}), 400
                user.role = data['role']
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log the user update
            current_user_id = get_jwt_identity()
            AuditLog.log_activity(
                user_id=current_user_id,
                action='update_user',
                table_name='users',
                record_id=user_id,
                notes=f"Updated user: {user.username}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'message': 'User updated successfully',
                'user': user.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            # Soft delete - deactivate user
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log the user deactivation
            current_user_id = get_jwt_identity()
            AuditLog.log_activity(
                user_id=current_user_id,
                action='deactivate_user',
                table_name='users',
                record_id=user_id,
                notes=f"Deactivated user: {user.username}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({'message': 'User deactivated successfully'}), 200
    
    except Exception as e:
        logger.error(f"User management error: {str(e)}")
        return jsonify({'error': 'User management failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500 