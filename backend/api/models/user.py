from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and role-based access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # admin, manager, staff
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    created_purchase_orders = db.relationship('PurchaseOrder', backref='created_by_user', 
                                            foreign_keys='PurchaseOrder.created_by', lazy='dynamic')
    approved_purchase_orders = db.relationship('PurchaseOrder', backref='approved_by_user',
                                             foreign_keys='PurchaseOrder.approved_by', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role not in ['admin', 'manager', 'staff']:
            self.role = 'staff'
    
    @hybrid_property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_property
    def permissions(self):
        """Get user permissions based on role"""
        permissions = {
            'admin': [
                'user_management', 'inventory_management', 'purchase_order_management',
                'supplier_management', 'reports', 'system_settings', 'audit_logs'
            ],
            'manager': [
                'inventory_management', 'purchase_order_management', 'supplier_management',
                'reports', 'approve_orders'
            ],
            'staff': [
                'view_inventory', 'create_purchase_orders', 'view_suppliers',
                'basic_reports'
            ]
        }
        return permissions.get(self.role, [])
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict_public(self):
        """Convert user to public dictionary (without sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active
        }
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_active_users():
        """Get all active users"""
        return User.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_users_by_role(role):
        """Get users by role"""
        return User.query.filter_by(role=role, is_active=True).all()
    
    def __repr__(self):
        return f'<User {self.username}>' 

# Import AuditLog at the end to avoid circular import
from .audit_log import AuditLog

# Now, if you want to add the relationship, do it after both classes are defined:
User.audit_logs = relationship("AuditLog", back_populates="user") 