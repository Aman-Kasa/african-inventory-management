// Smooth scroll for navigation links
const navLinks = document.querySelectorAll('.nav-links a');
navLinks.forEach(link => {
    link.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href');
        if (targetId.startsWith('#')) {
            e.preventDefault();
            document.querySelector(targetId).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Contact form submission
function handleFormSubmit(event) {
    event.preventDefault();
    alert('Thank you for your interest! We will contact you soon.');
    event.target.reset();
    return false;
}

// Modern Login Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initPasswordToggle();
    initFormValidation();
    initSocialButtons();
    initAnimations();
    initFloatingShapes();
});

// Password Toggle Functionality
function initPasswordToggle() {
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.querySelector('.password-toggle');
    
    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = passwordToggle.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
}

// Form Validation and Submission
function initFormValidation() {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.querySelector('.login-btn');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (validateForm()) {
                // Show loading state
                setLoadingState(true);
                
                // Simulate API call (replace with actual API call)
                setTimeout(() => {
                    handleLogin();
                }, 2000);
            }
        });
    }
    
    // Real-time validation
    if (emailInput) {
        emailInput.addEventListener('blur', validateEmail);
        emailInput.addEventListener('input', clearEmailError);
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('blur', validatePassword);
        passwordInput.addEventListener('input', clearPasswordError);
    }
}

// Form Validation Functions
function validateForm() {
    const emailValid = validateEmail();
    const passwordValid = validatePassword();
    return emailValid && passwordValid;
}

function validateEmail() {
    const emailInput = document.getElementById('email');
    const email = emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email) {
        showError(emailInput, 'Email is required');
        return false;
    } else if (!emailRegex.test(email)) {
        showError(emailInput, 'Please enter a valid email');
        return false;
    }
    
    clearError(emailInput);
    return true;
}

function validatePassword() {
    const passwordInput = document.getElementById('password');
    const password = passwordInput.value;
    
    if (!password) {
        showError(passwordInput, 'Password is required');
        return false;
    } else if (password.length < 6) {
        showError(passwordInput, 'Password must be at least 6 characters');
        return false;
    }
    
    clearError(passwordInput);
    return true;
}

// Error Handling Functions
function showError(input, message) {
    const wrapper = input.closest('.input-wrapper');
    let errorElement = wrapper.querySelector('.error-message');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        wrapper.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    wrapper.classList.add('error');
}

function clearError(input) {
    const wrapper = input.closest('.input-wrapper');
    const errorElement = wrapper.querySelector('.error-message');
    
    if (errorElement) {
        errorElement.remove();
    }
    wrapper.classList.remove('error');
}

function clearEmailError() {
    const emailInput = document.getElementById('email');
    if (emailInput.value.trim()) {
        clearError(emailInput);
    }
}

function clearPasswordError() {
    const passwordInput = document.getElementById('password');
    if (passwordInput.value) {
        clearError(passwordInput);
    }
}

// Loading State Management
function setLoadingState(loading) {
    const loginBtn = document.querySelector('.login-btn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnIcon = loginBtn.querySelector('.btn-icon');
    const btnLoading = loginBtn.querySelector('.btn-loading');
    
    if (loading) {
        loginBtn.classList.add('loading');
        loginBtn.disabled = true;
    } else {
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;
    }
}

// Login Handler
async function handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        // Make actual API call to backend
        const response = await fetch('http://localhost:5000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token if provided
            if (data.token) {
                localStorage.setItem('authToken', data.token);
            }
            
            showSuccessMessage('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            // Handle different error cases
            const errorMessage = data.message || data.error || 'Login failed. Please try again.';
            showErrorMessage(errorMessage);
            setLoadingState(false);
        }
        
    } catch (error) {
        console.error('Login error:', error);
        
        // Check if backend is not running
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showErrorMessage('Cannot connect to server. Please make sure the backend is running.');
        } else {
            showErrorMessage('Network error. Please check your connection and try again.');
        }
        
        setLoadingState(false);
    }
}

// Message Display Functions
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessage = document.querySelector('.message-popup');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `message-popup ${type}`;
    messageElement.innerHTML = `
        <div class="message-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(messageElement);
    
    // Animate in
    setTimeout(() => {
        messageElement.classList.add('show');
    }, 100);
    
    // Remove after delay
    setTimeout(() => {
        messageElement.classList.remove('show');
        setTimeout(() => {
            messageElement.remove();
        }, 300);
    }, type === 'success' ? 3000 : 5000);
}

// Social Login Buttons
function initSocialButtons() {
    const socialButtons = document.querySelectorAll('.social-btn');
    
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const provider = this.classList.contains('google-btn') ? 'Google' : 'Microsoft';
            showMessage(`Signing in with ${provider}...`, 'info');
            
            // Here you would implement actual OAuth flow
            console.log(`Signing in with ${provider}`);
        });
    });
}

// Animation Initialization
function initAnimations() {
    // Add entrance animations to elements
    const animatedElements = document.querySelectorAll('.highlight-item, .stat-card, .login-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Floating Shapes Animation
function initFloatingShapes() {
    const shapes = document.querySelectorAll('.shape');
    
    shapes.forEach((shape, index) => {
        // Add random movement
        setInterval(() => {
            const x = Math.random() * 20 - 10;
            const y = Math.random() * 20 - 10;
            shape.style.transform = `translate(${x}px, ${y}px) rotate(${Math.random() * 360}deg)`;
        }, 3000 + index * 500);
    });
}

// Add CSS for error states and messages
const style = document.createElement('style');
style.textContent = `
    .input-wrapper.error input {
        border-color: #e53e3e;
        box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1);
    }
    
    .error-message {
        color: #e53e3e;
        font-size: 0.8rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-message::before {
        content: '⚠';
        font-size: 0.9rem;
    }
    
    .message-popup {
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border-left: 4px solid;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 1000;
        max-width: 300px;
    }
    
    .message-popup.show {
        transform: translateX(0);
    }
    
    .message-popup.success {
        border-left-color: #48bb78;
    }
    
    .message-popup.error {
        border-left-color: #e53e3e;
    }
    
    .message-popup.info {
        border-left-color: #4299e1;
    }
    
    .message-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .message-content i {
        font-size: 1.2rem;
    }
    
    .message-popup.success .message-content i {
        color: #48bb78;
    }
    
    .message-popup.error .message-content i {
        color: #e53e3e;
    }
    
    .message-popup.info .message-content i {
        color: #4299e1;
    }
    
    .highlight-item,
    .stat-card,
    .login-card {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.6s ease;
    }
    
    .highlight-item.animate-in,
    .stat-card.animate-in,
    .login-card.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .highlight-item:nth-child(1) { transition-delay: 0.1s; }
    .highlight-item:nth-child(2) { transition-delay: 0.2s; }
    .highlight-item:nth-child(3) { transition-delay: 0.3s; }
    
    .stat-card:nth-child(1) { transition-delay: 0.1s; }
    .stat-card:nth-child(2) { transition-delay: 0.2s; }
    .stat-card:nth-child(3) { transition-delay: 0.3s; }
`;

document.head.appendChild(style);