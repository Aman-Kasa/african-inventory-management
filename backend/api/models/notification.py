from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Notification(db.Model):
    """Notification model for system alerts and user notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    action_url = db.Column(db.String(500))  # URL to navigate to when clicked
    expires_at = db.Column(db.DateTime)  # Optional expiration date
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __init__(self, **kwargs):
        super(Notification, self).__init__(**kwargs)
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None
        db.session.commit()
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'action_url': self.action_url,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def create_notification(user_id, title, message, type='info', action_url=None, expires_at=None):
        """Static method to create a notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            action_url=action_url,
            expires_at=expires_at
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def get_user_notifications(user_id, limit=50, unread_only=False):
        """Get notifications for a specific user"""
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user"""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.mark_as_read()
        
        return len(notifications)
    
    @staticmethod
    def delete_expired_notifications():
        """Delete expired notifications"""
        expired = Notification.query.filter(
            Notification.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired)
        for notification in expired:
            db.session.delete(notification)
        
        db.session.commit()
        return count
    
    @staticmethod
    def create_low_stock_notification(inventory_item):
        """Create low stock notification"""
        # Find users with inventory management permissions
        from .user import User
        users = User.query.filter(
            User.role.in_(['admin', 'manager'])
        ).all()
        
        notifications = []
        for user in users:
            notification = Notification.create_notification(
                user_id=user.id,
                title="Low Stock Alert",
                message=f"Item '{inventory_item.name}' (SKU: {inventory_item.sku}) is running low on stock. Current quantity: {inventory_item.quantity}",
                type="warning",
                action_url=f"/inventory/{inventory_item.id}"
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def create_purchase_order_notification(purchase_order, action):
        """Create purchase order notification"""
        if action == 'created':
            title = "New Purchase Order Created"
            message = f"Purchase order {purchase_order.po_number} has been created and is pending approval."
            notification_type = "info"
        elif action == 'approved':
            title = "Purchase Order Approved"
            message = f"Purchase order {purchase_order.po_number} has been approved."
            notification_type = "success"
        elif action == 'rejected':
            title = "Purchase Order Rejected"
            message = f"Purchase order {purchase_order.po_number} has been rejected."
            notification_type = "warning"
        elif action == 'delivered':
            title = "Purchase Order Delivered"
            message = f"Purchase order {purchase_order.po_number} has been delivered and items added to inventory."
            notification_type = "success"
        else:
            return None
        
        notification = Notification.create_notification(
            user_id=purchase_order.created_by,
            title=title,
            message=message,
            type=notification_type,
            action_url=f"/purchase-orders/{purchase_order.id}"
        )
        
        return notification
    
    @staticmethod
    def create_system_notification(title, message, user_ids=None, type='info'):
        """Create system-wide notification"""
        if user_ids is None:
            # Send to all active users
            from .user import User
            users = User.query.filter_by(is_active=True).all()
            user_ids = [user.id for user in users]
        
        notifications = []
        for user_id in user_ids:
            notification = Notification.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type
            )
            notifications.append(notification)
        
        return notifications
    
    def __repr__(self):
        return f'<Notification {self.title} for user {self.user_id}>' 