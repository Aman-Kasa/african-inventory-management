// Dashboard JavaScript
class InventoryManagementSystem {
    constructor() {
        this.currentUser = {
            name: 'John Doe',
            role: 'Manager',
            permissions: ['inventory', 'purchase_orders', 'suppliers', 'reports']
        };
        
        this.inventoryData = [
            {
                sku: 'SKU001',
                name: 'Steel Pipes',
                category: 'Raw Materials',
                quantity: 150,
                location: 'Warehouse A',
                unitPrice: 25.50,
                status: 'In Stock'
            },
            {
                sku: 'SKU002',
                name: 'Aluminum Sheets',
                category: 'Raw Materials',
                quantity: 5,
                location: 'Warehouse B',
                unitPrice: 45.75,
                status: 'Low Stock'
            },
            {
                sku: 'SKU003',
                name: 'Finished Product A',
                category: 'Finished Goods',
                quantity: 75,
                location: 'Warehouse A',
                unitPrice: 120.00,
                status: 'In Stock'
            }
        ];
        
        this.purchaseOrders = [
            {
                id: 'PO-2025-001',
                supplier: 'ABC Suppliers',
                items: 'Steel Pipes, Aluminum Sheets',
                totalAmount: 2500.00,
                status: 'Approved',
                createdDate: '2025-01-15'
            },
            {
                id: 'PO-2025-002',
                supplier: 'XYZ Manufacturing',
                items: 'Electronic Components',
                totalAmount: 1800.00,
                status: 'Pending',
                createdDate: '2025-01-20'
            }
        ];
        
        this.suppliers = [
            {
                id: 'SUP001',
                companyName: 'ABC Suppliers',
                contactPerson: 'John Smith',
                email: 'john@abcsuppliers.com',
                phone: '+1234567890',
                category: 'Raw Materials'
            },
            {
                id: 'SUP002',
                companyName: 'XYZ Manufacturing',
                contactPerson: 'Jane Doe',
                email: 'jane@xyzmanufacturing.com',
                phone: '+0987654321',
                category: 'Equipment'
            }
        ];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.setupRoleBasedAccess();
        this.initializeCharts();
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.navigateToPage(e.currentTarget.dataset.page);
            });
        });
        
        // Search functionality
        document.querySelectorAll('.search-input').forEach(input => {
            input.addEventListener('input', (e) => {
                this.handleSearch(e.target.value, e.target.closest('.page-content').id);
            });
        });
        
        // Filter functionality
        document.querySelectorAll('.filter-select').forEach(select => {
            select.addEventListener('change', (e) => {
                this.handleFilter(e.target.value, e.target.closest('.page-content').id);
            });
        });
        
        // Modal forms
        const addItemForm = document.getElementById('addItemForm');
        if (addItemForm) {
            addItemForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addInventoryItem(e.target);
            });
        }
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });
    }
    
    setupRoleBasedAccess() {
        const adminOnlyElements = document.querySelectorAll('.admin-only');
        adminOnlyElements.forEach(element => {
            if (!this.currentUser.permissions.includes('admin')) {
                element.style.display = 'none';
            }
        });
    }
    
    navigateToPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.page-content, .dashboard-content').forEach(page => {
            page.style.display = 'none';
        });
        
        // Show selected page
        const targetPage = document.getElementById(pageName + '-page') || document.getElementById('dashboard-page');
        if (targetPage) {
            targetPage.style.display = 'block';
        }
        
        // Update active menu item
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
        
        // Update page title
        const pageTitle = document.querySelector('.page-title');
        if (pageTitle) {
            pageTitle.textContent = this.getPageTitle(pageName);
        }
        
        // Load page-specific data
        this.loadPageData(pageName);
    }
    
    getPageTitle(pageName) {
        const titles = {
            dashboard: 'Dashboard',
            inventory: 'Inventory Management',
            'purchase-orders': 'Purchase Orders',
            suppliers: 'Supplier Management',
            reports: 'Reports & Analytics',
            users: 'User Management',
            settings: 'Settings'
        };
        return titles[pageName] || 'Dashboard';
    }
    
    loadPageData(pageName) {
        switch (pageName) {
            case 'inventory':
                this.loadInventoryTable();
                break;
            case 'purchase-orders':
                this.loadPurchaseOrdersTable();
                break;
            case 'suppliers':
                this.loadSuppliersTable();
                break;
            case 'reports':
                this.loadReports();
                break;
        }
    }
    
    loadDashboardData() {
        // Update metrics
        this.updateMetrics();
        
        // Load recent activity
        this.loadRecentActivity();
    }
    
    updateMetrics() {
        const totalItems = this.inventoryData.length;
        const lowStockItems = this.inventoryData.filter(item => item.quantity < 10).length;
        const pendingOrders = this.purchaseOrders.filter(order => order.status === 'Pending').length;
        const monthlySpend = this.purchaseOrders
            .filter(order => order.status === 'Approved')
            .reduce((sum, order) => sum + order.totalAmount, 0);
        
        // Update metric values (in a real app, these would be updated via DOM manipulation)
        console.log('Metrics updated:', { totalItems, lowStockItems, pendingOrders, monthlySpend });
    }
    
    loadRecentActivity() {
        // This would typically load from a backend API
        console.log('Recent activity loaded');
    }
    
    loadInventoryTable() {
        const tbody = document.getElementById('inventory-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = this.inventoryData.map(item => `
            <tr>
                <td>${item.sku}</td>
                <td>${item.name}</td>
                <td>${item.category}</td>
                <td>${item.quantity}</td>
                <td>${item.location}</td>
                <td>$${item.unitPrice.toFixed(2)}</td>
                <td><span class="status-badge ${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span></td>
                <td>
                    <button class="action-btn edit" onclick="ims.editItem('${item.sku}')">
                        <i class="fa-solid fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="ims.deleteItem('${item.sku}')">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    loadPurchaseOrdersTable() {
        const tbody = document.getElementById('orders-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = this.purchaseOrders.map(order => `
            <tr>
                <td>${order.id}</td>
                <td>${order.supplier}</td>
                <td>${order.items}</td>
                <td>$${order.totalAmount.toFixed(2)}</td>
                <td><span class="status-badge ${order.status.toLowerCase()}">${order.status}</span></td>
                <td>${order.createdDate}</td>
                <td>
                    <button class="action-btn view" onclick="ims.viewOrder('${order.id}')">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    ${order.status === 'Pending' ? `
                        <button class="action-btn edit" onclick="ims.approveOrder('${order.id}')">
                            <i class="fa-solid fa-check"></i>
                        </button>
                        <button class="action-btn delete" onclick="ims.rejectOrder('${order.id}')">
                            <i class="fa-solid fa-times"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
    }
    
    loadSuppliersTable() {
        const tbody = document.getElementById('suppliers-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = this.suppliers.map(supplier => `
            <tr>
                <td>${supplier.id}</td>
                <td>${supplier.companyName}</td>
                <td>${supplier.contactPerson}</td>
                <td>${supplier.email}</td>
                <td>${supplier.phone}</td>
                <td>${supplier.category}</td>
                <td>
                    <button class="action-btn edit" onclick="ims.editSupplier('${supplier.id}')">
                        <i class="fa-solid fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="ims.deleteSupplier('${supplier.id}')">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    loadReports() {
        // Initialize report charts
        this.initializeReportCharts();
    }
    
    handleSearch(query, pageId) {
        console.log('Searching for:', query, 'on page:', pageId);
        // Implement search logic based on page
    }
    
    handleFilter(filterValue, pageId) {
        console.log('Filtering by:', filterValue, 'on page:', pageId);
        // Implement filter logic based on page
    }
    
    // Modal Functions
    openAddItemModal() {
        document.getElementById('addItemModal').style.display = 'block';
    }
    
    openAddOrderModal() {
        // Implementation for purchase order modal
        alert('Purchase Order modal would open here');
    }
    
    openAddSupplierModal() {
        // Implementation for supplier modal
        alert('Supplier modal would open here');
    }
    
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
    
    // CRUD Operations
    addInventoryItem(form) {
        const formData = new FormData(form);
        const newItem = {
            sku: formData.get('sku'),
            name: formData.get('name'),
            category: formData.get('category'),
            quantity: parseInt(formData.get('quantity')),
            location: formData.get('location'),
            unitPrice: parseFloat(formData.get('price')),
            status: 'In Stock'
        };
        
        this.inventoryData.push(newItem);
        this.loadInventoryTable();
        this.closeModal('addItemModal');
        form.reset();
        
        // Show success message
        this.showNotification('Item added successfully!', 'success');
    }
    
    editItem(sku) {
        const item = this.inventoryData.find(item => item.sku === sku);
        if (item) {
            alert(`Edit item: ${item.name}`);
            // Implementation for edit modal
        }
    }
    
    deleteItem(sku) {
        if (confirm('Are you sure you want to delete this item?')) {
            this.inventoryData = this.inventoryData.filter(item => item.sku !== sku);
            this.loadInventoryTable();
            this.showNotification('Item deleted successfully!', 'success');
        }
    }
    
    viewOrder(orderId) {
        const order = this.purchaseOrders.find(order => order.id === orderId);
        if (order) {
            alert(`View order details: ${order.id}`);
            // Implementation for order details modal
        }
    }
    
    approveOrder(orderId) {
        const order = this.purchaseOrders.find(order => order.id === orderId);
        if (order) {
            order.status = 'Approved';
            this.loadPurchaseOrdersTable();
            this.showNotification('Order approved successfully!', 'success');
        }
    }
    
    rejectOrder(orderId) {
        const order = this.purchaseOrders.find(order => order.id === orderId);
        if (order) {
            order.status = 'Rejected';
            this.loadPurchaseOrdersTable();
            this.showNotification('Order rejected!', 'warning');
        }
    }
    
    editSupplier(supplierId) {
        const supplier = this.suppliers.find(supplier => supplier.id === supplierId);
        if (supplier) {
            alert(`Edit supplier: ${supplier.companyName}`);
            // Implementation for edit supplier modal
        }
    }
    
    deleteSupplier(supplierId) {
        if (confirm('Are you sure you want to delete this supplier?')) {
            this.suppliers = this.suppliers.filter(supplier => supplier.id !== supplierId);
            this.loadSuppliersTable();
            this.showNotification('Supplier deleted successfully!', 'success');
        }
    }
    
    // Chart Functions
    initializeCharts() {
        // Simple chart implementation using canvas
        this.drawInventoryChart();
        this.drawOrdersChart();
    }
    
    initializeReportCharts() {
        // Initialize report-specific charts
        console.log('Report charts initialized');
    }
    
    drawInventoryChart() {
        const canvas = document.getElementById('inventoryChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const data = [150, 5, 75, 45, 30]; // Sample data
        const labels = ['Steel Pipes', 'Aluminum', 'Finished A', 'Spare Parts', 'Others'];
        
        this.drawBarChart(ctx, data, labels, '#3b82f6');
    }
    
    drawOrdersChart() {
        const canvas = document.getElementById('ordersChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const data = [8, 12, 3, 5]; // Sample data
        const labels = ['Pending', 'Approved', 'Rejected', 'Delivered'];
        
        this.drawPieChart(ctx, data, labels);
    }
    
    drawBarChart(ctx, data, labels, color) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const barWidth = width / data.length * 0.8;
        const barSpacing = width / data.length * 0.2;
        const maxValue = Math.max(...data);
        
        ctx.clearRect(0, 0, width, height);
        
        data.forEach((value, index) => {
            const barHeight = (value / maxValue) * (height - 40);
            const x = index * (barWidth + barSpacing) + barSpacing / 2;
            const y = height - barHeight - 20;
            
            ctx.fillStyle = color;
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw label
            ctx.fillStyle = '#475569';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(labels[index], x + barWidth / 2, height - 5);
        });
    }
    
    drawPieChart(ctx, data, labels) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;
        
        const colors = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b'];
        const total = data.reduce((sum, value) => sum + value, 0);
        
        ctx.clearRect(0, 0, width, height);
        
        let currentAngle = 0;
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            
            ctx.fillStyle = colors[index];
            ctx.fill();
            
            currentAngle += sliceAngle;
        });
    }
    
    // Utility Functions
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 3000;
            animation: slideIn 0.3s ease;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            info: '#3b82f6'
        };
        notification.style.background = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    exportReport(type) {
        let data, filename;
        
        switch (type) {
            case 'inventory':
                data = this.inventoryData;
                filename = 'inventory_report.csv';
                break;
            case 'orders':
                data = this.purchaseOrders;
                filename = 'purchase_orders_report.csv';
                break;
            default:
                return;
        }
        
        // Convert to CSV
        const csv = this.convertToCSV(data);
        
        // Download file
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.showNotification(`${type} report exported successfully!`, 'success');
    }
    
    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];
        
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header];
                return typeof value === 'string' ? `"${value}"` : value;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    }
}

// Global functions for HTML onclick handlers
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = 'login.html';
    }
}

function openAddItemModal() {
    ims.openAddItemModal();
}

function openAddOrderModal() {
    ims.openAddOrderModal();
}

function openAddSupplierModal() {
    ims.openAddSupplierModal();
}

function closeModal(modalId) {
    ims.closeModal(modalId);
}

function exportReport(type) {
    ims.exportReport(type);
}

// Initialize the system when DOM is loaded
let ims;
document.addEventListener('DOMContentLoaded', () => {
    ims = new InventoryManagementSystem();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style); 