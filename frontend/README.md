# IPMS Frontend

Frontend application for the Inventory & Procurement Management System.

## 📁 Project Structure

```
frontend/
├── index.html              # Landing page
├── login.html              # Login page
├── pages/
│   └── dashboard.html      # Main dashboard
├── assets/
│   ├── css/
│   │   ├── styles.css      # Main styles
│   │   └── dashboard.css   # Dashboard styles
│   ├── js/
│   │   ├── script.js       # Main JavaScript
│   │   └── dashboard.js    # Dashboard functionality
│   └── images/             # Image assets
├── components/             # Reusable components
├── utils/                  # Utility functions
└── package.json           # Frontend dependencies
```

## 🚀 Quick Start

### Prerequisites
- Modern web browser
- Local web server (optional)

### Development
```bash
# Navigate to frontend directory
cd frontend

# Start development server
python -m http.server 8000
# or
npm start

# Open in browser
http://localhost:8000
```

### Production
```bash
# Build for production
npm run build

# Serve static files
npx serve .
```

## 🎨 Design System

### Colors
- Primary: #3b82f6 (Blue)
- Secondary: #64748b (Gray)
- Success: #10b981 (Green)
- Warning: #f59e0b (Yellow)
- Error: #ef4444 (Red)

### Typography
- Font Family: 'Segoe UI', Arial, sans-serif
- Headings: Bold, various sizes
- Body: Regular, 16px

### Components
- Cards: Rounded corners, shadows
- Buttons: Consistent styling with hover effects
- Forms: Clean, accessible design
- Tables: Responsive with sorting

## 📱 Responsive Design

The frontend is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🔧 Customization

### Adding New Pages
1. Create HTML file in `pages/` directory
2. Add corresponding CSS in `assets/css/`
3. Add JavaScript functionality in `assets/js/`
4. Update navigation in dashboard

### Styling
- Main styles: `assets/css/styles.css`
- Component-specific styles: `assets/css/dashboard.css`
- Use CSS custom properties for theming

### JavaScript
- Main functionality: `assets/js/script.js`
- Dashboard functionality: `assets/js/dashboard.js`
- Modular approach for maintainability

## 📦 Dependencies

### External Libraries
- Font Awesome 6.4.2 (Icons)
- Google Fonts (Optional)

### Development Tools
- Live Server (for development)
- Browser DevTools (for debugging)

## 🧪 Testing

### Manual Testing
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Responsive design testing
- Accessibility testing

### Automated Testing
```bash
# Run tests (when implemented)
npm test

# Run linting (when implemented)
npm run lint
```

## 📊 Performance

### Optimization
- Minified CSS and JavaScript for production
- Optimized images
- Lazy loading for large components
- Efficient DOM manipulation

### Metrics
- Page load time: < 2 seconds
- First contentful paint: < 1 second
- Time to interactive: < 3 seconds

## 🔒 Security

### Best Practices
- Input validation on client-side
- XSS prevention
- CSRF protection (when backend integrated)
- Secure file uploads

## 📈 Analytics

### Tracking
- Page views and user interactions
- Performance metrics
- Error tracking (when implemented)

## 🌐 Internationalization

### Multi-language Support
- Ready for i18n implementation
- RTL support for Arabic languages
- Localized date and number formats

## 🔄 Integration

### Backend API
- RESTful API integration ready
- JWT authentication support
- Real-time updates capability

### Third-party Services
- Email service integration
- File storage integration
- Payment gateway integration (future)

## 📝 Documentation

### Code Documentation
- Inline comments for complex functions
- JSDoc comments for JavaScript functions
- CSS comments for complex styles

### User Documentation
- User guides and tutorials
- FAQ section
- Video tutorials (future)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Standards
- Consistent indentation (2 spaces)
- Meaningful variable names
- Comment complex logic
- Follow existing patterns

## 📞 Support

### Contact Information
- Developer: Aman Abraha Kasa
- Organization: African Leadership University
- Email: support@ipms-africa.com

### Resources
- API Documentation: [Backend README](../backend/README.md)
- Design System: [Design Guide](./docs/design-system.md)
- Deployment Guide: [Deployment](./docs/deployment.md)

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production Ready 