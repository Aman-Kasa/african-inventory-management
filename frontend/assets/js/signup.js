// Modern Signup Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            setLoadingState(true);
            const formData = getSignupFormData();
            if (!formData) {
                setLoadingState(false);
                return;
            }
            try {
                const response = await fetch('http://localhost:5000/api/auth/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const data = await response.json();
                if (response.ok) {
                    showSuccessMessage('Signup successful! You can now log in.');
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1500);
                } else {
                    showErrorMessage(data.error || data.message || 'Signup failed.');
                }
            } catch (error) {
                showErrorMessage('Cannot connect to server. Please try again later.');
            }
            setLoadingState(false);
        });
    }
});

function getSignupFormData() {
    const username = document.getElementById('username')?.value.trim();
    const email = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;
    const firstName = document.getElementById('first_name')?.value.trim();
    const lastName = document.getElementById('last_name')?.value.trim();

    if (!username || !email || !password || !firstName || !lastName) {
        showErrorMessage('All fields are required.');
        return null;
    }
    if (password.length < 6) {
        showErrorMessage('Password must be at least 6 characters.');
        return null;
    }
    return {
        username,
        email,
        password,
        first_name: firstName,
        last_name: lastName
        // role is always staff for public signup
    };
}

function setLoadingState(loading) {
    const signupBtn = document.querySelector('.signup-btn');
    if (signupBtn) {
        signupBtn.disabled = loading;
        signupBtn.classList.toggle('loading', loading);
    }
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    const existing = document.querySelector('.message-popup');
    if (existing) existing.remove();
    const msg = document.createElement('div');
    msg.className = `message-popup ${type}`;
    msg.textContent = message;
    document.body.appendChild(msg);
    setTimeout(() => msg.remove(), 4000);
} 