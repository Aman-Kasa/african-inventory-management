from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AuditLog(db.Model):
    """Audit Log model for tracking all system activities"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # login, logout, create, update, delete, etc.
    table_name = db.Column(db.String(100), nullable=False)  # users, inventory_items, purchase_orders, etc.
    record_id = db.Column(db.Integer)  # ID of the affected record
    old_value = db.Column(db.Text)  # Previous value (for updates)
    new_value = db.Column(db.Text)  # New value (for updates)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6 address
    user_agent = db.Column(db.Text)  # Browser/device information
    notes = db.Column(db.Text)  # Additional notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __init__(self, **kwargs):
        super(AuditLog, self).__init__(**kwargs)
        # Set default values if not provided
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user': self.user.to_dict_public() if self.user else None,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def log_activity(user_id, action, table_name, record_id=None, old_value=None, new_value=None, 
                    ip_address=None, user_agent=None, notes=None):
        """Static method to log activity"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            notes=notes
        )
        db.session.add(audit_log)
        db.session.commit()
        return audit_log
    
    @staticmethod
    def get_user_activity(user_id, limit=50):
        """Get activity for a specific user"""
        return AuditLog.query.filter_by(user_id=user_id).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_table_activity(table_name, record_id=None, limit=50):
        """Get activity for a specific table or record"""
        query = AuditLog.query.filter_by(table_name=table_name)
        if record_id:
            query = query.filter_by(record_id=record_id)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_activity(limit=100):
        """Get recent activity across all tables"""
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_activity_by_action(action, limit=50):
        """Get activity by specific action"""
        return AuditLog.query.filter_by(action=action).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_activity_summary(days=30):
        """Get activity summary for the last N days"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get activity counts by action
        action_counts = db.session.query(
            AuditLog.action,
            db.func.count(AuditLog.id)
        ).filter(AuditLog.created_at >= start_date).group_by(AuditLog.action).all()
        
        # Get activity counts by table
        table_counts = db.session.query(
            AuditLog.table_name,
            db.func.count(AuditLog.id)
        ).filter(AuditLog.created_at >= start_date).group_by(AuditLog.table_name).all()
        
        # Get user activity counts
        user_counts = db.session.query(
            AuditLog.user_id,
            db.func.count(AuditLog.id)
        ).filter(AuditLog.created_at >= start_date).group_by(AuditLog.user_id).all()
        
        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'action_counts': dict(action_counts),
            'table_counts': dict(table_counts),
            'user_counts': dict(user_counts)
        }
    
    @staticmethod
    def search_activity(query, start_date=None, end_date=None, user_id=None, action=None, table_name=None):
        """Search audit logs with filters"""
        search = AuditLog.query
        
        if query:
            search = search.filter(
                db.or_(
                    AuditLog.notes.ilike(f'%{query}%'),
                    AuditLog.old_value.ilike(f'%{query}%'),
                    AuditLog.new_value.ilike(f'%{query}%')
                )
            )
        
        if start_date:
            search = search.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            search = search.filter(AuditLog.created_at <= end_date)
        
        if user_id:
            search = search.filter(AuditLog.user_id == user_id)
        
        if action:
            search = search.filter(AuditLog.action == action)
        
        if table_name:
            search = search.filter(AuditLog.table_name == table_name)
        
        return search.order_by(AuditLog.created_at.desc()).all()
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.table_name} by user {self.user_id}>' 