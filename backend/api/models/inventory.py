from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import qrcode
import io
import base64

db = SQLAlchemy()

class Category(db.Model):
    """Category model for organizing inventory items"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InventoryItem', backref='category', lazy='dynamic')
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'item_count': self.items.count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_active_categories():
        """Get all active categories"""
        return Category.query.filter_by(is_active=True).all()
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Location(db.Model):
    """Location model for warehouse and storage locations"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InventoryItem', backref='location', lazy='dynamic')
    
    def to_dict(self):
        """Convert location to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'is_active': self.is_active,
            'item_count': self.items.count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_active_locations():
        """Get all active locations"""
        return Location.query.filter_by(is_active=True).all()
    
    def __repr__(self):
        return f'<Location {self.name}>'

class InventoryItem(db.Model):
    """Inventory item model for tracking stock"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    reorder_level = db.Column(db.Integer, default=10)
    reorder_quantity = db.Column(db.Integer, default=50)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    barcode = db.Column(db.String(100), unique=True)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = db.relationship('User', backref='created_items')
    supplier = db.relationship('Supplier', backref='items')
    audit_logs = db.relationship('AuditLog', backref='inventory_item', lazy='dynamic')
    
    @hybrid_property
    def total_value(self):
        """Calculate total value of inventory item"""
        return float(self.quantity * self.unit_price)
    
    @hybrid_property
    def status(self):
        """Get inventory status based on quantity"""
        if self.quantity <= 0:
            return 'out_of_stock'
        elif self.quantity <= self.reorder_level:
            return 'low_stock'
        else:
            return 'in_stock'
    
    @hybrid_property
    def needs_reorder(self):
        """Check if item needs reordering"""
        return self.quantity <= self.reorder_level
    
    def add_stock(self, quantity, user_id, notes=None):
        """Add stock to inventory"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.quantity += quantity
        self.updated_at = datetime.utcnow()
        
        # Create audit log
        from .audit_log import AuditLog
        audit_log = AuditLog(
            user_id=user_id,
            action='add_stock',
            table_name='inventory_items',
            record_id=self.id,
            old_value=str(self.quantity - quantity),
            new_value=str(self.quantity),
            notes=notes or f"Added {quantity} units"
        )
        db.session.add(audit_log)
        db.session.commit()
    
    def remove_stock(self, quantity, user_id, notes=None):
        """Remove stock from inventory"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantity < quantity:
            raise ValueError("Insufficient stock")
        
        self.quantity -= quantity
        self.updated_at = datetime.utcnow()
        
        # Create audit log
        from .audit_log import AuditLog
        audit_log = AuditLog(
            user_id=user_id,
            action='remove_stock',
            table_name='inventory_items',
            record_id=self.id,
            old_value=str(self.quantity + quantity),
            new_value=str(self.quantity),
            notes=notes or f"Removed {quantity} units"
        )
        db.session.add(audit_log)
        db.session.commit()
    
    def to_dict(self, include_qr=False):
        """Convert inventory item to dictionary"""
        data = {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category': self.category.to_dict() if self.category else None,
            'location': self.location.to_dict() if self.location else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_value': self.total_value,
            'reorder_level': self.reorder_level,
            'reorder_quantity': self.reorder_quantity,
            'supplier': self.supplier.to_dict() if self.supplier else None,
            'barcode': self.barcode,
            'image_url': self.image_url,
            'status': self.status,
            'needs_reorder': self.needs_reorder,
            'is_active': self.is_active,
            'created_by': self.created_by_user.to_dict_public() if self.created_by_user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_qr:
            data['qr_code'] = self.get_qr_code_base64()
        return data
    
    def to_dict_summary(self):
        """Convert to summary dictionary for lists"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category_name': self.category.name if self.category else None,
            'location_name': self.location.name if self.location else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_value': self.total_value,
            'status': self.status,
            'needs_reorder': self.needs_reorder
        }
    
    @staticmethod
    def get_low_stock_items():
        """Get items with low stock"""
        return InventoryItem.query.filter(
            InventoryItem.quantity <= InventoryItem.reorder_level,
            InventoryItem.is_active == True
        ).all()
    
    @staticmethod
    def get_out_of_stock_items():
        """Get items that are out of stock"""
        return InventoryItem.query.filter(
            InventoryItem.quantity == 0,
            InventoryItem.is_active == True
        ).all()
    
    @staticmethod
    def search_items(query, category_id=None, location_id=None):
        """Search inventory items"""
        search = InventoryItem.query.filter(InventoryItem.is_active == True)
        
        if query:
            search = search.filter(
                db.or_(
                    InventoryItem.name.ilike(f'%{query}%'),
                    InventoryItem.sku.ilike(f'%{query}%'),
                    InventoryItem.description.ilike(f'%{query}%')
                )
            )
        
        if category_id:
            search = search.filter(InventoryItem.category_id == category_id)
        
        if location_id:
            search = search.filter(InventoryItem.location_id == location_id)
        
        return search.order_by(InventoryItem.name).all()
    
    @staticmethod
    def get_inventory_summary():
        """Get inventory summary statistics"""
        total_items = InventoryItem.query.filter_by(is_active=True).count()
        total_value = db.session.query(func.sum(InventoryItem.quantity * InventoryItem.unit_price)).filter_by(is_active=True).scalar() or 0
        low_stock_count = InventoryItem.query.filter(
            InventoryItem.quantity <= InventoryItem.reorder_level,
            InventoryItem.is_active == True
        ).count()
        out_of_stock_count = InventoryItem.query.filter(
            InventoryItem.quantity == 0,
            InventoryItem.is_active == True
        ).count()
        
        return {
            'total_items': total_items,
            'total_value': float(total_value),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count
        }
    
    def get_qr_code_base64(self):
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(f'INVENTORY:{self.sku}')
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        img_bytes = buf.read()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        return f'data:image/png;base64,{base64_str}'
    
    def __repr__(self):
        return f'<InventoryItem {self.sku}: {self.name}>' 