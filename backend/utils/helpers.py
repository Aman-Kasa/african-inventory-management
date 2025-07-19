import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import re

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_filename(original_filename):
    """Generate unique filename"""
    # Get file extension
    file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if file_ext:
        return f"{timestamp}_{unique_id}.{file_ext}"
    else:
        return f"{timestamp}_{unique_id}"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def validate_sku(sku):
    """Validate SKU format"""
    # SKU should be alphanumeric and 3-20 characters
    pattern = r'^[A-Za-z0-9]{3,20}$'
    return re.match(pattern, sku) is not None

def format_currency(amount, currency='USD'):
    """Format currency amount"""
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    elif currency == 'GBP':
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_date(date_obj):
    """Format date object to string"""
    if isinstance(date_obj, str):
        return date_obj
    elif date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return None

def format_datetime(datetime_obj):
    """Format datetime object to string"""
    if isinstance(datetime_obj, str):
        return datetime_obj
    elif datetime_obj:
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    return None

def paginate_query(query, page=1, per_page=20):
    """Paginate SQLAlchemy query"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_pagination_info(pagination):
    """Get pagination information"""
    return {
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'next_num': pagination.next_num,
        'prev_num': pagination.prev_num
    }

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = secure_filename(filename)
    
    # Remove any remaining unsafe characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    return filename

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except OSError:
        return 0

def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return True
    return False

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return missing_fields

def validate_numeric_range(value, min_value=None, max_value=None):
    """Validate numeric value is within range"""
    try:
        num_value = float(value)
        if min_value is not None and num_value < min_value:
            return False, f"Value must be at least {min_value}"
        if max_value is not None and num_value > max_value:
            return False, f"Value must be at most {max_value}"
        return True, None
    except (ValueError, TypeError):
        return False, "Value must be a number"

def validate_string_length(value, min_length=None, max_length=None):
    """Validate string length"""
    if not isinstance(value, str):
        return False, "Value must be a string"
    
    length = len(value)
    if min_length is not None and length < min_length:
        return False, f"String must be at least {min_length} characters"
    if max_length is not None and length > max_length:
        return False, f"String must be at most {max_length} characters"
    
    return True, None

def generate_report_filename(report_type, format='json'):
    """Generate filename for reports"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{report_type}_report_{timestamp}.{format}"

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    
    today = datetime.now().date()
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age

def truncate_text(text, max_length=100, suffix='...'):
    """Truncate text to specified length"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def generate_unique_code(prefix='', length=8):
    """Generate unique alphanumeric code"""
    import random
    import string
    
    # Generate random alphanumeric string
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choice(chars) for _ in range(length))
    
    return f"{prefix}{random_part}"

def validate_url(url):
    """Validate URL format"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None

def clean_html_tags(text):
    """Remove HTML tags from text"""
    if not text:
        return text
    
    # Simple HTML tag removal
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}" 