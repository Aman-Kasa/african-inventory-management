from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

db = SQLAlchemy()

class PurchaseOrder(db.Model):
    """Purchase Order model for managing procurement"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected, delivered, cancelled
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    delivery_date = db.Column(db.Date)
    delivery_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='purchase_orders')
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='created_purchase_orders')
    approved_by_user = db.relationship('User', foreign_keys=[approved_by], backref='approved_purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='purchase_order', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(PurchaseOrder, self).__init__(**kwargs)
        if not self.po_number:
            self.po_number = self.generate_po_number()
    
    @staticmethod
    def generate_po_number():
        """Generate unique PO number"""
        from datetime import datetime
        year = datetime.now().year
        month = datetime.now().month
        
        # Get count of POs for this year/month
        count = PurchaseOrder.query.filter(
            db.extract('year', PurchaseOrder.created_at) == year,
            db.extract('month', PurchaseOrder.created_at) == month
        ).count()
        
        return f"PO-{year}{month:02d}-{count+1:03d}"
    
    @hybrid_property
    def item_count(self):
        """Get total number of items in PO"""
        return self.items.count()
    
    @hybrid_property
    def can_approve(self):
        """Check if PO can be approved"""
        return self.status == 'pending'
    
    @hybrid_property
    def can_reject(self):
        """Check if PO can be rejected"""
        return self.status == 'pending'
    
    @hybrid_property
    def can_cancel(self):
        """Check if PO can be cancelled"""
        return self.status in ['pending', 'approved']
    
    def calculate_total(self):
        """Calculate total amount from items"""
        total = sum(item.total_price for item in self.items)
        self.total_amount = total
        return total
    
    def add_item(self, inventory_item_id, quantity, unit_price, notes=None):
        """Add item to purchase order"""
        from .inventory import InventoryItem
        
        # Check if item already exists
        existing_item = self.items.filter_by(inventory_item_id=inventory_item_id).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.unit_price = unit_price
            if notes:
                existing_item.notes = notes
        else:
            item = PurchaseOrderItem(
                purchase_order_id=self.id,
                inventory_item_id=inventory_item_id,
                quantity=quantity,
                unit_price=unit_price,
                notes=notes
            )
            db.session.add(item)
        
        self.calculate_total()
        db.session.commit()
    
    def remove_item(self, item_id):
        """Remove item from purchase order"""
        item = self.items.filter_by(id=item_id).first()
        if item:
            db.session.delete(item)
            self.calculate_total()
            db.session.commit()
    
    def approve(self, approved_by_user_id, notes=None):
        """Approve purchase order"""
        if not self.can_approve:
            raise ValueError("Purchase order cannot be approved")
        
        self.status = 'approved'
        self.approved_by = approved_by_user_id
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Create audit log
        from .audit_log import AuditLog
        audit_log = AuditLog(
            user_id=approved_by_user_id,
            action='approve_po',
            table_name='purchase_orders',
            record_id=self.id,
            old_value='pending',
            new_value='approved',
            notes=notes or f"Purchase order {self.po_number} approved"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Create notification for supplier
        from .notification import Notification
        notification = Notification(
            user_id=self.created_by,
            title="Purchase Order Approved",
            message=f"Purchase order {self.po_number} has been approved",
            type="info"
        )
        db.session.add(notification)
        db.session.commit()
    
    def reject(self, rejected_by_user_id, notes=None):
        """Reject purchase order"""
        if not self.can_reject:
            raise ValueError("Purchase order cannot be rejected")
        
        self.status = 'rejected'
        self.updated_at = datetime.utcnow()
        
        # Create audit log
        from .audit_log import AuditLog
        audit_log = AuditLog(
            user_id=rejected_by_user_id,
            action='reject_po',
            table_name='purchase_orders',
            record_id=self.id,
            old_value='pending',
            new_value='rejected',
            notes=notes or f"Purchase order {self.po_number} rejected"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Create notification
        from .notification import Notification
        notification = Notification(
            user_id=self.created_by,
            title="Purchase Order Rejected",
            message=f"Purchase order {self.po_number} has been rejected",
            type="warning"
        )
        db.session.add(notification)
        db.session.commit()
    
    def mark_delivered(self, delivered_by_user_id, notes=None):
        """Mark purchase order as delivered"""
        if self.status != 'approved':
            raise ValueError("Only approved purchase orders can be marked as delivered")
        
        self.status = 'delivered'
        self.updated_at = datetime.utcnow()
        
        # Add items to inventory
        for item in self.items:
            inventory_item = item.inventory_item
            if inventory_item:
                inventory_item.add_stock(
                    quantity=item.quantity,
                    user_id=delivered_by_user_id,
                    notes=f"Delivery from PO {self.po_number}"
                )
        
        # Create audit log
        from .audit_log import AuditLog
        audit_log = AuditLog(
            user_id=delivered_by_user_id,
            action='deliver_po',
            table_name='purchase_orders',
            record_id=self.id,
            old_value='approved',
            new_value='delivered',
            notes=notes or f"Purchase order {self.po_number} delivered"
        )
        db.session.add(audit_log)
        db.session.commit()
    
    def to_dict(self):
        """Convert purchase order to dictionary"""
        return {
            'id': self.id,
            'po_number': self.po_number,
            'supplier': self.supplier.to_dict() if self.supplier else None,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_address': self.delivery_address,
            'notes': self.notes,
            'item_count': self.item_count,
            'can_approve': self.can_approve,
            'can_reject': self.can_reject,
            'can_cancel': self.can_cancel,
            'created_by': self.created_by_user.to_dict_public() if self.created_by_user else None,
            'approved_by': self.approved_by_user.to_dict_public() if self.approved_by_user else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict_summary(self):
        """Convert to summary dictionary for lists"""
        return {
            'id': self.id,
            'po_number': self.po_number,
            'supplier_name': self.supplier.company_name if self.supplier else None,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'item_count': self.item_count,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'created_by': self.created_by_user.full_name if self.created_by_user else None,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def get_pending_orders():
        """Get all pending purchase orders"""
        return PurchaseOrder.query.filter_by(status='pending').order_by(PurchaseOrder.created_at.desc()).all()
    
    @staticmethod
    def get_orders_by_status(status):
        """Get purchase orders by status"""
        return PurchaseOrder.query.filter_by(status=status).order_by(PurchaseOrder.created_at.desc()).all()
    
    @staticmethod
    def get_orders_by_supplier(supplier_id):
        """Get purchase orders by supplier"""
        return PurchaseOrder.query.filter_by(supplier_id=supplier_id).order_by(PurchaseOrder.created_at.desc()).all()
    
    @staticmethod
    def search_orders(query, status=None, supplier_id=None):
        """Search purchase orders"""
        search = PurchaseOrder.query
        
        if query:
            search = search.filter(
                db.or_(
                    PurchaseOrder.po_number.ilike(f'%{query}%'),
                    PurchaseOrder.notes.ilike(f'%{query}%')
                )
            )
        
        if status:
            search = search.filter(PurchaseOrder.status == status)
        
        if supplier_id:
            search = search.filter(PurchaseOrder.supplier_id == supplier_id)
        
        return search.order_by(PurchaseOrder.created_at.desc()).all()
    
    @staticmethod
    def get_po_summary():
        """Get purchase order summary statistics"""
        total_orders = PurchaseOrder.query.count()
        pending_orders = PurchaseOrder.query.filter_by(status='pending').count()
        approved_orders = PurchaseOrder.query.filter_by(status='approved').count()
        delivered_orders = PurchaseOrder.query.filter_by(status='delivered').count()
        total_value = db.session.query(func.sum(PurchaseOrder.total_amount)).scalar() or 0
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'approved_orders': approved_orders,
            'delivered_orders': delivered_orders,
            'total_value': float(total_value)
        }
    
    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'

class PurchaseOrderItem(db.Model):
    """Purchase Order Item model for individual items in PO"""
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory_item = db.relationship('InventoryItem', backref='purchase_order_items')
    
    @hybrid_property
    def total_price(self):
        """Calculate total price for this item"""
        return float(self.quantity * self.unit_price)
    
    def to_dict(self):
        """Convert purchase order item to dictionary"""
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'inventory_item': self.inventory_item.to_dict_summary() if self.inventory_item else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': self.total_price,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PurchaseOrderItem {self.inventory_item.name if self.inventory_item else "Unknown"}: {self.quantity}>' 