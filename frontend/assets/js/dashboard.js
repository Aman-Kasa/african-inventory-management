// ===== ENTERPRISE DASHBOARD JAVASCRIPT =====

class IPMSDashboard {
    constructor() {
        this.currentUser = null;
        this.charts = {};
        this.notifications = [];
        this.activities = [];
        this.isLoading = true;
        this.apiBaseUrl = 'http://localhost:5000/api';
        
        this.init();
    }

    async init() {
        try {
            // Check authentication
            await this.checkAuth();
            
            // Initialize components
            this.initializeComponents();
            this.setupEventListeners();
            this.loadDashboardData();
            this.initializeCharts();
            this.startRealTimeUpdates();
            
            // Hide loading screen
            setTimeout(() => {
                this.hideLoadingScreen();
            }, 1500);
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard');
        }
    }

    async checkAuth() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = 'index.html';
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Authentication failed');
            }

            const data = await response.json();
            this.currentUser = data.user;
            this.updateUserInfo();
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('access_token');
            window.location.href = 'index.html';
        }
    }

    initializeComponents() {
        // Initialize date/time display
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);

        // Initialize sidebar
        this.initializeSidebar();

        // Initialize modals
        this.initializeModals();

        // Initialize search functionality
        this.initializeSearch();
    }

    setupEventListeners() {
        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.target.closest('.nav-link').getAttribute('href'));
            });
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Notifications
        document.getElementById('notificationsBtn').addEventListener('click', () => {
            this.showNotificationsModal();
        });

        document.getElementById('markAllRead').addEventListener('click', () => {
            this.markAllNotificationsRead();
        });

        // Search
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.showSearchModal();
        });

        // Fullscreen
        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Quick actions
        document.getElementById('addItemBtn').addEventListener('click', () => {
            this.showAddItemModal();
        });

        document.getElementById('createOrderBtn').addEventListener('click', () => {
            this.showCreateOrderModal();
        });

        document.getElementById('addSupplierBtn').addEventListener('click', () => {
            this.showAddSupplierModal();
        });

        document.getElementById('generateReportBtn').addEventListener('click', () => {
            this.generateReport();
        });

        // Chart period change
        document.getElementById('chartPeriod').addEventListener('change', (e) => {
            this.updateInventoryChart(e.target.value);
        });

        // Modal close events
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        // Close modals on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    async loadDashboardData() {
        try {
            // Load stats
            await this.loadStats();
            
            // Load recent activities
            await this.loadRecentActivities();
            
            // Load notifications
            await this.loadNotifications();
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadStats() {
        try {
            const response = await this.apiCall('/dashboard/stats');
            if (response.success) {
                this.updateStats(response.data);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
            // Use mock data for demo
            this.updateStats({
                totalItems: 12847,
                totalValue: 2400000,
                pendingOrders: 23,
                activeSuppliers: 156
            });
        }
    }

    async loadRecentActivities() {
        try {
            const response = await this.apiCall('/dashboard/activities');
            if (response.success) {
                this.activities = response.data;
                this.renderActivities();
            }
        } catch (error) {
            console.error('Failed to load activities:', error);
            // Use mock data for demo
            this.activities = this.getMockActivities();
            this.renderActivities();
        }
    }

    async loadNotifications() {
        try {
            const response = await this.apiCall('/dashboard/notifications');
            if (response.success) {
                this.notifications = response.data;
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
            // Use mock data for demo
            this.notifications = this.getMockNotifications();
            this.renderNotifications();
        }
    }

    updateStats(stats) {
        document.getElementById('totalItems').textContent = this.formatNumber(stats.totalItems);
        document.getElementById('totalValue').textContent = this.formatCurrency(stats.totalValue);
        document.getElementById('pendingOrders').textContent = stats.pendingOrders;
        document.getElementById('activeSuppliers').textContent = stats.activeSuppliers;
    }

    renderActivities() {
        const container = document.getElementById('activityList');
        container.innerHTML = '';

        this.activities.slice(0, 5).forEach(activity => {
            const activityElement = this.createActivityElement(activity);
            container.appendChild(activityElement);
        });
    }

    renderNotifications() {
        const container = document.getElementById('notificationsList');
        const modalContainer = document.getElementById('modalNotificationsList');
        
        container.innerHTML = '';
        modalContainer.innerHTML = '';

        this.notifications.slice(0, 3).forEach(notification => {
            const notificationElement = this.createNotificationElement(notification);
            container.appendChild(notificationElement);
        });

        this.notifications.forEach(notification => {
            const notificationElement = this.createNotificationElement(notification, true);
            modalContainer.appendChild(notificationElement);
        });

        // Update notification badge
        const unreadCount = this.notifications.filter(n => !n.read).length;
        const badge = document.querySelector('.notification-badge');
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }

    createActivityElement(activity) {
        const div = document.createElement('div');
        div.className = 'activity-item slide-up';
        div.innerHTML = `
            <div class="activity-icon" style="background: ${this.getActivityColor(activity.type)}">
                <i class="${this.getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <p>${activity.description}</p>
                <span class="activity-time">${this.formatTimeAgo(activity.timestamp)}</span>
            </div>
        `;
        return div;
    }

    createNotificationElement(notification, isModal = false) {
        const div = document.createElement('div');
        div.className = `notification-item ${!notification.read ? 'unread' : ''} slide-up`;
        div.innerHTML = `
            <div class="notification-icon">
                <i class="${this.getNotificationIcon(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <h4>${notification.title}</h4>
                <p>${notification.message}</p>
                <span class="notification-time">${this.formatTimeAgo(notification.timestamp)}</span>
            </div>
            ${!notification.read ? '<div class="notification-dot"></div>' : ''}
        `;
        
        if (!notification.read) {
            div.addEventListener('click', () => this.markNotificationRead(notification.id));
        }
        
        return div;
    }

    initializeCharts() {
        this.createInventoryChart();
        this.createCategoryChart();
    }

    createInventoryChart() {
        const ctx = document.getElementById('inventoryChart').getContext('2d');
        
        this.charts.inventory = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.getLast30Days(),
                datasets: [{
                    label: 'Inventory Value',
                    data: this.generateMockInventoryData(),
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    createCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Electronics', 'Clothing', 'Food', 'Books', 'Other'],
                datasets: [{
                    data: [30, 25, 20, 15, 10],
                    backgroundColor: [
                        '#2563eb',
                        '#10b981',
                        '#f59e0b',
                        '#8b5cf6',
                        '#64748b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    updateInventoryChart(days) {
        if (this.charts.inventory) {
            this.charts.inventory.data.labels = this.getLastDays(days);
            this.charts.inventory.data.datasets[0].data = this.generateMockInventoryData(days);
            this.charts.inventory.update();
        }
    }

    initializeSidebar() {
        // Add active class to current nav item
        const currentPath = window.location.hash || '#dashboard';
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.parentElement.classList.add('active');
            }
        });
    }

    initializeModals() {
        // Modal functionality is handled in event listeners
    }

    initializeSearch() {
        const searchInput = document.getElementById('searchInput');
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });
    }

    async performSearch(query) {
        if (!query.trim()) {
            document.getElementById('searchResults').innerHTML = '';
            return;
        }

        try {
            const response = await this.apiCall(`/search?q=${encodeURIComponent(query)}`);
            if (response.success) {
                this.renderSearchResults(response.data);
            }
        } catch (error) {
            console.error('Search failed:', error);
            // Show mock results for demo
            this.renderSearchResults(this.getMockSearchResults(query));
        }
    }

    renderSearchResults(results) {
        const container = document.getElementById('searchResults');
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<p class="no-results">No results found</p>';
            return;
        }

        results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'search-result-item';
            div.innerHTML = `
                <div class="result-icon">
                    <i class="${this.getSearchResultIcon(result.type)}"></i>
                </div>
                <div class="result-content">
                    <h4>${result.title}</h4>
                    <p>${result.description}</p>
                </div>
            `;
            div.addEventListener('click', () => this.handleSearchResultClick(result));
            container.appendChild(div);
        });
    }

    startRealTimeUpdates() {
        // Update stats every 30 seconds
        setInterval(() => {
            this.loadStats();
        }, 30000);

        // Update activities every 2 minutes
        setInterval(() => {
            this.loadRecentActivities();
        }, 120000);

        // Update notifications every minute
        setInterval(() => {
            this.loadNotifications();
        }, 60000);
    }

    updateDateTime() {
        const now = new Date();
        const dateElement = document.getElementById('currentDate');
        const timeElement = document.getElementById('currentTime');

        dateElement.textContent = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        timeElement.textContent = now.toLocaleTimeString('en-US', {
            hour12: true,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    updateUserInfo() {
        if (this.currentUser) {
            document.getElementById('userName').textContent = `${this.currentUser.first_name} ${this.currentUser.last_name}`;
            document.getElementById('userRole').textContent = this.currentUser.role;
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('collapsed');
    }

    showNotificationsModal() {
        document.getElementById('notificationsModal').classList.add('active');
    }

    showSearchModal() {
        document.getElementById('searchModal').classList.add('active');
        document.getElementById('searchInput').focus();
    }

    closeModal(modal) {
        modal.classList.remove('active');
    }

    async logout() {
        try {
            const token = localStorage.getItem('access_token');
            if (token) {
                await fetch(`${this.apiBaseUrl}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('access_token');
            window.location.href = 'index.html';
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    handleNavigation(hash) {
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to clicked item
        const navItem = document.querySelector(`[href="${hash}"]`).parentElement;
        navItem.classList.add('active');

        // Handle navigation (in a real app, this would load different content)
        console.log(`Navigating to: ${hash}`);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.showSearchModal();
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                this.closeModal(activeModal);
            }
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        loadingScreen.classList.add('hidden');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }

    showError(message) {
        // Create and show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(errorDiv);

        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        };

        const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
            ...defaultOptions,
            ...options
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
        }

        return await response.json();
    }

    // Utility methods
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    getLast30Days() {
        const dates = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        return dates;
    }

    getLastDays(days) {
        const dates = [];
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        return dates;
    }

    generateMockInventoryData(days = 30) {
        const data = [];
        let baseValue = 2000000;
        
        for (let i = 0; i < days; i++) {
            baseValue += (Math.random() - 0.5) * 100000;
            data.push(Math.max(0, baseValue));
        }
        
        return data;
    }

    getActivityColor(type) {
        const colors = {
            'inventory': '#10b981',
            'order': '#3b82f6',
            'supplier': '#f59e0b',
            'user': '#8b5cf6',
            'system': '#64748b'
        };
        return colors[type] || '#64748b';
    }

    getActivityIcon(type) {
        const icons = {
            'inventory': 'fas fa-boxes',
            'order': 'fas fa-shopping-cart',
            'supplier': 'fas fa-truck',
            'user': 'fas fa-user',
            'system': 'fas fa-cog'
        };
        return icons[type] || 'fas fa-info-circle';
    }

    getNotificationIcon(type) {
        const icons = {
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'error': 'fas fa-times-circle'
        };
        return icons[type] || 'fas fa-bell';
    }

    getSearchResultIcon(type) {
        const icons = {
            'inventory': 'fas fa-boxes',
            'order': 'fas fa-shopping-cart',
            'supplier': 'fas fa-truck',
            'user': 'fas fa-user'
        };
        return icons[type] || 'fas fa-search';
    }

    // Mock data methods
    getMockActivities() {
        return [
            {
                id: 1,
                type: 'inventory',
                description: 'New item "Laptop Dell XPS 13" added to inventory',
                timestamp: new Date(Date.now() - 5 * 60 * 1000)
            },
            {
                id: 2,
                type: 'order',
                description: 'Purchase order #PO-2024-001 approved',
                timestamp: new Date(Date.now() - 15 * 60 * 1000)
            },
            {
                id: 3,
                type: 'supplier',
                description: 'Supplier "Tech Solutions Inc." updated',
                timestamp: new Date(Date.now() - 30 * 60 * 1000)
            },
            {
                id: 4,
                type: 'user',
                description: 'New user "Sarah Johnson" registered',
                timestamp: new Date(Date.now() - 60 * 60 * 1000)
            },
            {
                id: 5,
                type: 'system',
                description: 'System backup completed successfully',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
            }
        ];
    }

    getMockNotifications() {
        return [
            {
                id: 1,
                type: 'warning',
                title: 'Low Stock Alert',
                message: 'Item "Wireless Mouse" is running low on stock (5 units remaining)',
                timestamp: new Date(Date.now() - 10 * 60 * 1000),
                read: false
            },
            {
                id: 2,
                type: 'info',
                title: 'New Order Received',
                message: 'Purchase order #PO-2024-002 has been submitted for approval',
                timestamp: new Date(Date.now() - 25 * 60 * 1000),
                read: false
            },
            {
                id: 3,
                type: 'success',
                title: 'Backup Complete',
                message: 'Daily system backup completed successfully at 2:00 AM',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                read: true
            }
        ];
    }

    getMockSearchResults(query) {
        return [
            {
                id: 1,
                type: 'inventory',
                title: 'Laptop Dell XPS 13',
                description: 'High-performance laptop with 16GB RAM, 512GB SSD'
            },
            {
                id: 2,
                type: 'order',
                title: 'Purchase Order #PO-2024-001',
                description: 'Order for office supplies - Status: Approved'
            },
            {
                id: 3,
                type: 'supplier',
                title: 'Tech Solutions Inc.',
                description: 'Electronics supplier - Contact: John Smith'
            }
        ].filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) ||
            item.description.toLowerCase().includes(query.toLowerCase())
        );
    }

    // Placeholder methods for future implementation
    showAddItemModal() {
        console.log('Show add item modal');
        // Implementation for adding new inventory item
    }

    showCreateOrderModal() {
        console.log('Show create order modal');
        // Implementation for creating new purchase order
    }

    showAddSupplierModal() {
        console.log('Show add supplier modal');
        // Implementation for adding new supplier
    }

    generateReport() {
        console.log('Generate report');
        // Implementation for generating reports
    }

    async markNotificationRead(notificationId) {
        try {
            await this.apiCall(`/notifications/${notificationId}/read`, {
                method: 'PUT'
            });
            this.loadNotifications();
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }

    async markAllNotificationsRead() {
        try {
            await this.apiCall('/notifications/mark-all-read', {
                method: 'PUT'
            });
            this.loadNotifications();
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    }

    handleSearchResultClick(result) {
        console.log('Search result clicked:', result);
        this.closeModal(document.getElementById('searchModal'));
        // Implementation for handling search result clicks
    }
}

// === Inventory Section Integration ===

document.addEventListener('DOMContentLoaded', () => {
    loadAndRenderInventory();
    setupExportButtons();
});

async function loadAndRenderInventory() {
    try {
        const response = await fetch('http://localhost:5000/api/inventory');
        const data = await response.json();
        if (Array.isArray(data.items)) {
            renderInventoryTable(data.items);
        }
    } catch (error) {
        renderInventoryTable([]);
    }
}

function renderInventoryTable(items) {
    const tbody = document.getElementById('inventoryTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.id}</td>
            <td>${item.sku}</td>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>${item.location || ''}</td>
            <td><img src="${item.qr_code || ''}" alt="QR" style="width:48px;height:48px;"></td>
        `;
        tbody.appendChild(tr);
    });
}

function setupExportButtons() {
    const csvBtn = document.getElementById('exportCsvBtn');
    const pdfBtn = document.getElementById('exportPdfBtn');
    if (csvBtn) {
        csvBtn.addEventListener('click', () => {
            window.open('http://localhost:5000/api/inventory/export/csv', '_blank');
        });
    }
    if (pdfBtn) {
        pdfBtn.addEventListener('click', () => {
            window.open('http://localhost:5000/api/inventory/export/pdf', '_blank');
        });
    }
}

// Add CSS for error notifications
const style = document.createElement('style');
style.textContent = `
    .error-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: slideInRight 0.3s ease-out;
    }

    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .activity-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        background: #f8fafc;
        transition: background 0.2s ease;
        margin-bottom: 0.5rem;
    }

    .activity-item:hover {
        background: #f1f5f9;
    }

    .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.9rem;
        flex-shrink: 0;
    }

    .activity-content p {
        margin-bottom: 0.25rem;
        color: #1e293b;
        font-weight: 500;
    }

    .activity-time {
        font-size: 0.8rem;
        color: #64748b;
    }

    .notification-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        transition: background 0.2s ease;
        margin-bottom: 0.5rem;
        cursor: pointer;
        position: relative;
    }

    .notification-item:hover {
        background: #f8fafc;
    }

    .notification-item.unread {
        background: #eff6ff;
    }

    .notification-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.9rem;
        flex-shrink: 0;
    }

    .notification-item.unread .notification-icon {
        background: #3b82f6;
    }

    .notification-content h4 {
        margin-bottom: 0.25rem;
        color: #1e293b;
        font-weight: 600;
    }

    .notification-content p {
        margin-bottom: 0.25rem;
        color: #475569;
        font-size: 0.9rem;
    }

    .notification-time {
        font-size: 0.8rem;
        color: #64748b;
    }

    .notification-dot {
        width: 8px;
        height: 8px;
        background: #3b82f6;
        border-radius: 50%;
        position: absolute;
        top: 1rem;
        right: 1rem;
    }

    .search-result-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s ease;
        margin-bottom: 0.5rem;
    }

    .search-result-item:hover {
        background: #f8fafc;
    }

    .result-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748b;
        font-size: 0.9rem;
        flex-shrink: 0;
    }

    .result-content h4 {
        margin-bottom: 0.25rem;
        color: #1e293b;
        font-weight: 600;
    }

    .result-content p {
        color: #64748b;
        font-size: 0.9rem;
    }

    .no-results {
        text-align: center;
        color: #64748b;
        padding: 2rem;
    }
`;
document.head.appendChild(style); 