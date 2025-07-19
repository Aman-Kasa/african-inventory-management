from flask import Blueprint, request, jsonify, send_file, make_response, current_app
from api.models.inventory import InventoryItem
from io import BytesIO
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
def get_all_inventory():
    """Return all inventory items with QR codes for frontend display."""
    items = InventoryItem.query.all()
    return jsonify({'items': [item.to_dict(include_qr=True) for item in items]})

@inventory_bp.route('/<int:item_id>/qr', methods=['GET'])
def get_inventory_item_qr(item_id):
    """Return QR code image (base64) for a specific inventory item."""
    item = InventoryItem.query.get_or_404(item_id)
    qr_base64 = item.get_qr_code_base64()
    return jsonify({'qr_code': qr_base64, 'sku': item.sku, 'name': item.name})

@inventory_bp.route('/export/csv', methods=['GET'])
def export_inventory_csv():
    """Export all inventory items as CSV."""
    items = InventoryItem.query.all()
    output = BytesIO()
    writer = csv.writer(output)
    # Write header
    writer.writerow(['ID', 'SKU', 'Name', 'Description', 'Quantity', 'Location'])
    # Write data
    for item in items:
        writer.writerow([
            item.id,
            item.sku,
            item.name,
            item.description or '',
            item.quantity,
            item.location or ''
        ])
    output.seek(0)
    response = make_response(output.read())
    response.headers['Content-Disposition'] = 'attachment; filename=inventory_export.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@inventory_bp.route('/export/pdf', methods=['GET'])
def export_inventory_pdf():
    """Export all inventory items as PDF."""
    items = InventoryItem.query.all()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont('Helvetica-Bold', 16)
    p.drawString(40, y, 'Inventory Export')
    y -= 30
    p.setFont('Helvetica', 10)
    p.drawString(40, y, 'ID')
    p.drawString(80, y, 'SKU')
    p.drawString(180, y, 'Name')
    p.drawString(320, y, 'Quantity')
    p.drawString(400, y, 'Location')
    y -= 20
    p.setFont('Helvetica', 9)
    for item in items:
        if y < 60:
            p.showPage()
            y = height - 40
        p.drawString(40, y, str(item.id))
        p.drawString(80, y, item.sku)
        p.drawString(180, y, item.name)
        p.drawString(320, y, str(item.quantity))
        p.drawString(400, y, item.location or '')
        y -= 16
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='inventory_export.pdf', mimetype='application/pdf') 