from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

db = SQLAlchemy()

class Supplier(db.Model):
    """Supplier model for managing vendor relationships"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Nigeria')
    postal_code = db.Column(db.String(20))
    website = db.Column(db.String(200))
    category = db.Column(db.String(100))  # Raw Materials, Equipment, Services, etc.
    payment_terms = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    bank_details = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Integer, default=5)  # 1-5 rating
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = db.relationship('User', backref='created_suppliers')
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')
    inventory_items = db.relationship('InventoryItem', backref='supplier', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='supplier', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Supplier, self).__init__(**kwargs)
        if not self.supplier_code:
            self.supplier_code = self.generate_supplier_code()
    
    @staticmethod
    def generate_supplier_code():
        """Generate unique supplier code"""
        from datetime import datetime
        year = datetime.now().year
        
        # Get count of suppliers for this year
        count = Supplier.query.filter(
            db.extract('year', Supplier.created_at) == year
        ).count()
        
        return f"SUP{year}{count+1:03d}"
    
    @hybrid_property
    def full_address(self):
        """Get complete address"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.postal_code:
            address_parts.append(self.postal_code)
        if self.country:
            address_parts.append(self.country)
        
        return ', '.join(address_parts) if address_parts else None
    
    @hybrid_property
    def order_count(self):
        """Get total number of purchase orders"""
        return self.purchase_orders.count()
    
    @hybrid_property
    def total_spent(self):
        """Calculate total amount spent with this supplier"""
        total = db.session.query(func.sum(PurchaseOrder.total_amount)).filter(
            PurchaseOrder.supplier_id == self.id,
            PurchaseOrder.status.in_(['approved', 'delivered'])
        ).scalar()
        return float(total) if total else 0.0
    
    @hybrid_property
    def average_order_value(self):
        """Calculate average order value"""
        if self.order_count == 0:
            return 0.0
        return self.total_spent / self.order_count
    
    @hybrid_property
    def performance_rating(self):
        """Calculate performance rating based on various factors"""
        # This is a simplified rating calculation
        # In a real system, this would be more complex
        base_rating = self.rating or 5
        
        # Adjust based on order count and total spent
        if self.order_count > 10:
            base_rating += 0.5
        if self.total_spent > 10000:
            base_rating += 0.5
        
        return min(5.0, max(1.0, base_rating))
    
    def update_rating(self, new_rating):
        """Update supplier rating"""
        if 1 <= new_rating <= 5:
            self.rating = new_rating
            self.updated_at = datetime.utcnow()
            db.session.commit()
        else:
            raise ValueError("Rating must be between 1 and 5")
    
    def get_recent_orders(self, limit=5):
        """Get recent purchase orders"""
        return self.purchase_orders.order_by(PurchaseOrder.created_at.desc()).limit(limit).all()
    
    def get_order_summary(self):
        """Get order summary by status"""
        summary = {}
        for status in ['pending', 'approved', 'delivered', 'rejected']:
            count = self.purchase_orders.filter_by(status=status).count()
            summary[status] = count
        return summary
    
    def to_dict(self):
        """Convert supplier to dictionary"""
        return {
            'id': self.id,
            'supplier_code': self.supplier_code,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'full_address': self.full_address,
            'website': self.website,
            'category': self.category,
            'payment_terms': self.payment_terms,
            'tax_id': self.tax_id,
            'bank_details': self.bank_details,
            'notes': self.notes,
            'is_active': self.is_active,
            'rating': self.rating,
            'performance_rating': self.performance_rating,
            'order_count': self.order_count,
            'total_spent': self.total_spent,
            'average_order_value': self.average_order_value,
            'created_by': self.created_by_user.to_dict_public() if self.created_by_user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict_summary(self):
        """Convert to summary dictionary for lists"""
        return {
            'id': self.id,
            'supplier_code': self.supplier_code,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'category': self.category,
            'is_active': self.is_active,
            'rating': self.rating,
            'performance_rating': self.performance_rating,
            'order_count': self.order_count,
            'total_spent': self.total_spent
        }
    
    @staticmethod
    def get_active_suppliers():
        """Get all active suppliers"""
        return Supplier.query.filter_by(is_active=True).order_by(Supplier.company_name).all()
    
    @staticmethod
    def get_suppliers_by_category(category):
        """Get suppliers by category"""
        return Supplier.query.filter_by(category=category, is_active=True).order_by(Supplier.company_name).all()
    
    @staticmethod
    def search_suppliers(query, category=None):
        """Search suppliers"""
        search = Supplier.query.filter_by(is_active=True)
        
        if query:
            search = search.filter(
                db.or_(
                    Supplier.company_name.ilike(f'%{query}%'),
                    Supplier.contact_person.ilike(f'%{query}%'),
                    Supplier.email.ilike(f'%{query}%'),
                    Supplier.supplier_code.ilike(f'%{query}%')
                )
            )
        
        if category:
            search = search.filter(Supplier.category == category)
        
        return search.order_by(Supplier.company_name).all()
    
    @staticmethod
    def get_top_suppliers(limit=10):
        """Get top suppliers by total spent"""
        return Supplier.query.filter_by(is_active=True).order_by(
            db.desc(Supplier.total_spent)
        ).limit(limit).all()
    
    @staticmethod
    def get_supplier_summary():
        """Get supplier summary statistics"""
        total_suppliers = Supplier.query.count()
        active_suppliers = Supplier.query.filter_by(is_active=True).count()
        total_spent = db.session.query(func.sum(PurchaseOrder.total_amount)).filter(
            PurchaseOrder.status.in_(['approved', 'delivered'])
        ).scalar() or 0
        
        # Get category distribution
        categories = db.session.query(
            Supplier.category,
            func.count(Supplier.id)
        ).filter_by(is_active=True).group_by(Supplier.category).all()
        
        category_distribution = {cat: count for cat, count in categories}
        
        return {
            'total_suppliers': total_suppliers,
            'active_suppliers': active_suppliers,
            'total_spent': float(total_spent),
            'category_distribution': category_distribution
        }
    
    def __repr__(self):
        return f'<Supplier {self.supplier_code}: {self.company_name}>' 