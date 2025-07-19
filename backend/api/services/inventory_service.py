"""
Inventory Service Layer
Handles business logic for inventory management operations
"""

from typing import List, Dict, Optional
from datetime import datetime
from models import db, InventoryItem, Category, Location, AuditLog, Notification
from utils.helpers import validate_required_fields, validate_numeric_range

class InventoryService:
    """Service class for inventory management operations"""
    
    @staticmethod
    def get_all_items(page: int = 1, per_page: int = 20, search: str = None, 
                     category_id: int = None, location_id: int = None) -> Dict:
        """Get all inventory items with pagination and filtering"""
        try:
            query = InventoryItem.query.filter_by(is_active=True)
            
            # Apply search filter
            if search:
                query = query.filter(
                    db.or_(
                        InventoryItem.name.ilike(f'%{search}%'),
                        InventoryItem.sku.ilike(f'%{search}%'),
                        InventoryItem.description.ilike(f'%{search}%')
                    )
                )
            
            # Apply category filter
            if category_id:
                query = query.filter(InventoryItem.category_id == category_id)
            
            # Apply location filter
            if location_id:
                query = query.filter(InventoryItem.location_id == location_id)
            
            # Paginate results
            pagination = query.order_by(InventoryItem.name).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'items': [item.to_dict_summary() for item in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        
        except Exception as e:
            raise Exception(f"Failed to get inventory items: {str(e)}")
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Dict]:
        """Get inventory item by ID"""
        try:
            item = InventoryItem.query.get(item_id)
            return item.to_dict() if item else None
        except Exception as e:
            raise Exception(f"Failed to get inventory item: {str(e)}")
    
    @staticmethod
    def create_item(data: Dict, user_id: int) -> Dict:
        """Create new inventory item"""
        try:
            # Validate required fields
            required_fields = ['sku', 'name', 'category_id', 'location_id', 'quantity', 'unit_price']
            missing_fields = validate_required_fields(data, required_fields)
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate numeric fields
            quantity_valid, quantity_msg = validate_numeric_range(data['quantity'], min_value=0)
            if not quantity_valid:
                raise ValueError(quantity_msg)
            
            price_valid, price_msg = validate_numeric_range(data['unit_price'], min_value=0)
            if not price_valid:
                raise ValueError(price_msg)
            
            # Check if SKU already exists
            existing_item = InventoryItem.query.filter_by(sku=data['sku']).first()
            if existing_item:
                raise ValueError("SKU already exists")
            
            # Create new item
            new_item = InventoryItem(
                sku=data['sku'],
                name=data['name'],
                description=data.get('description'),
                category_id=data['category_id'],
                location_id=data['location_id'],
                quantity=data['quantity'],
                unit_price=data['unit_price'],
                reorder_level=data.get('reorder_level', 10),
                reorder_quantity=data.get('reorder_quantity', 50),
                supplier_id=data.get('supplier_id'),
                barcode=data.get('barcode'),
                created_by=user_id
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # Log the creation
            AuditLog.log_activity(
                user_id=user_id,
                action='create_inventory_item',
                table_name='inventory_items',
                record_id=new_item.id,
                notes=f"Created inventory item: {new_item.name} (SKU: {new_item.sku})"
            )
            
            return new_item.to_dict()
        
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create inventory item: {str(e)}")
    
    @staticmethod
    def update_item(item_id: int, data: Dict, user_id: int) -> Dict:
        """Update inventory item"""
        try:
            item = InventoryItem.query.get(item_id)
            if not item:
                raise ValueError("Inventory item not found")
            
            # Update fields
            if 'name' in data:
                item.name = data['name']
            if 'description' in data:
                item.description = data['description']
            if 'category_id' in data:
                item.category_id = data['category_id']
            if 'location_id' in data:
                item.location_id = data['location_id']
            if 'unit_price' in data:
                price_valid, price_msg = validate_numeric_range(data['unit_price'], min_value=0)
                if not price_valid:
                    raise ValueError(price_msg)
                item.unit_price = data['unit_price']
            if 'reorder_level' in data:
                level_valid, level_msg = validate_numeric_range(data['reorder_level'], min_value=0)
                if not level_valid:
                    raise ValueError(level_msg)
                item.reorder_level = data['reorder_level']
            if 'reorder_quantity' in data:
                qty_valid, qty_msg = validate_numeric_range(data['reorder_quantity'], min_value=0)
                if not qty_valid:
                    raise ValueError(qty_msg)
                item.reorder_quantity = data['reorder_quantity']
            if 'supplier_id' in data:
                item.supplier_id = data['supplier_id']
            if 'barcode' in data:
                item.barcode = data['barcode']
            
            item.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log the update
            AuditLog.log_activity(
                user_id=user_id,
                action='update_inventory_item',
                table_name='inventory_items',
                record_id=item.id,
                notes=f"Updated inventory item: {item.name} (SKU: {item.sku})"
            )
            
            return item.to_dict()
        
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update inventory item: {str(e)}")
    
    @staticmethod
    def delete_item(item_id: int, user_id: int) -> bool:
        """Delete inventory item (soft delete)"""
        try:
            item = InventoryItem.query.get(item_id)
            if not item:
                raise ValueError("Inventory item not found")
            
            # Soft delete
            item.is_active = False
            item.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log the deletion
            AuditLog.log_activity(
                user_id=user_id,
                action='delete_inventory_item',
                table_name='inventory_items',
                record_id=item.id,
                notes=f"Deleted inventory item: {item.name} (SKU: {item.sku})"
            )
            
            return True
        
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete inventory item: {str(e)}")
    
    @staticmethod
    def add_stock(item_id: int, quantity: int, user_id: int, notes: str = None) -> Dict:
        """Add stock to inventory item"""
        try:
            item = InventoryItem.query.get(item_id)
            if not item:
                raise ValueError("Inventory item not found")
            
            # Validate quantity
            qty_valid, qty_msg = validate_numeric_range(quantity, min_value=1)
            if not qty_valid:
                raise ValueError(qty_msg)
            
            # Add stock
            item.add_stock(quantity, user_id, notes)
            
            # Check if item was previously low stock
            if item.quantity > item.reorder_level and item.quantity - quantity <= item.reorder_level:
                # Create notification that stock is back to normal
                Notification.create_notification(
                    user_id=user_id,
                    title="Stock Restored",
                    message=f"Item '{item.name}' (SKU: {item.sku}) stock has been restored to normal levels.",
                    type="success"
                )
            
            return item.to_dict()
        
        except Exception as e:
            raise Exception(f"Failed to add stock: {str(e)}")
    
    @staticmethod
    def remove_stock(item_id: int, quantity: int, user_id: int, notes: str = None) -> Dict:
        """Remove stock from inventory item"""
        try:
            item = InventoryItem.query.get(item_id)
            if not item:
                raise ValueError("Inventory item not found")
            
            # Validate quantity
            qty_valid, qty_msg = validate_numeric_range(quantity, min_value=1)
            if not qty_valid:
                raise ValueError(qty_msg)
            
            # Remove stock
            item.remove_stock(quantity, user_id, notes)
            
            # Check if item is now low stock
            if item.quantity <= item.reorder_level:
                # Create low stock notification
                Notification.create_low_stock_notification(item)
            
            return item.to_dict()
        
        except Exception as e:
            raise Exception(f"Failed to remove stock: {str(e)}")
    
    @staticmethod
    def get_inventory_summary() -> Dict:
        """Get inventory summary statistics"""
        try:
            return InventoryItem.get_inventory_summary()
        except Exception as e:
            raise Exception(f"Failed to get inventory summary: {str(e)}")
    
    @staticmethod
    def get_low_stock_items() -> List[Dict]:
        """Get items with low stock"""
        try:
            items = InventoryItem.get_low_stock_items()
            return [item.to_dict_summary() for item in items]
        except Exception as e:
            raise Exception(f"Failed to get low stock items: {str(e)}")
    
    @staticmethod
    def get_out_of_stock_items() -> List[Dict]:
        """Get items that are out of stock"""
        try:
            items = InventoryItem.get_out_of_stock_items()
            return [item.to_dict_summary() for item in items]
        except Exception as e:
            raise Exception(f"Failed to get out of stock items: {str(e)}")
    
    @staticmethod
    def search_items(query: str, category_id: int = None, location_id: int = None) -> List[Dict]:
        """Search inventory items"""
        try:
            items = InventoryItem.search_items(query, category_id, location_id)
            return [item.to_dict_summary() for item in items]
        except Exception as e:
            raise Exception(f"Failed to search items: {str(e)}") 