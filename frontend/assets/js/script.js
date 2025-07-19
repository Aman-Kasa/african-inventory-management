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

// Login form logic
const loginForm = document.querySelector('.login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const email = loginForm.querySelector('input[type="email"]').value.trim();
        const password = loginForm.querySelector('input[type="password"]').value.trim();
        if (email && password) {
            window.location.href = 'dashboard.html';
        } else {
            alert('Please enter both email and password.');
        }
    });
}