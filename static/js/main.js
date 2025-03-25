/**
 * Main JavaScript file for Northeast India Wiki
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    initializeMobileMenu();
    
    // Dropdown menu functionality
    initializeDropdowns();
    
    // Message auto-dismissal
    initializeMessageDismissal();
    
    // Form validation
    initializeFormValidation();
});

/**
 * Initializes mobile menu functionality
 */
function initializeMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    if (!menuToggle) return;
    
    const mainNav = document.querySelector('.main-nav');
    
    menuToggle.addEventListener('click', function() {
        mainNav.classList.toggle('active');
        menuToggle.classList.toggle('active');
        
        // Toggle aria-expanded attribute for accessibility
        const expanded = menuToggle.getAttribute('aria-expanded') === 'true' || false;
        menuToggle.setAttribute('aria-expanded', !expanded);
    });
}

/**
 * Initializes dropdown menu functionality for mobile devices
 */
function initializeDropdowns() {
    // For mobile: make dropdowns toggleable
    if (window.innerWidth <= 768) {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const parent = this.parentNode;
                parent.classList.toggle('active');
                
                // Close other open dropdowns
                document.querySelectorAll('.dropdown.active').forEach(dropdown => {
                    if (dropdown !== parent) {
                        dropdown.classList.remove('active');
                    }
                });
            });
        });
    }
}

/**
 * Initializes automatic dismissal of notification messages
 */
function initializeMessageDismissal() {
    const messages = document.querySelectorAll('.message:not(.error)');
    
    messages.forEach(message => {
        // Auto dismiss success and info messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
        
        // Add dismiss button
        const dismissBtn = document.createElement('button');
        dismissBtn.className = 'message-dismiss';
        dismissBtn.innerHTML = '&times;';
        dismissBtn.setAttribute('aria-label', 'Dismiss message');
        
        dismissBtn.addEventListener('click', () => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        });
        
        message.appendChild(dismissBtn);
    });
}

/**
 * Initializes basic form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate required fields
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Add error message if it doesn't exist
                    let errorElement = field.nextElementSibling;
                    if (!errorElement || !errorElement.classList.contains('form-error')) {
                        errorElement = document.createElement('div');
                        errorElement.className = 'form-error';
                        errorElement.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorElement, field.nextSibling);
                    }
                } else {
                    field.classList.remove('is-invalid');
                    
                    // Remove error message if it exists
                    const errorElement = field.nextElementSibling;
                    if (errorElement && errorElement.classList.contains('form-error')) {
                        errorElement.remove();
                    }
                }
            });
            
            // Validate email fields
            const emailFields = form.querySelectorAll('input[type="email"]');
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            emailFields.forEach(field => {
                if (field.value.trim() && !emailPattern.test(field.value)) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Add error message if it doesn't exist
                    let errorElement = field.nextElementSibling;
                    if (!errorElement || !errorElement.classList.contains('form-error')) {
                        errorElement = document.createElement('div');
                        errorElement.className = 'form-error';
                        errorElement.textContent = 'Please enter a valid email address';
                        field.parentNode.insertBefore(errorElement, field.nextSibling);
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Live validation as user types
        const formFields = form.querySelectorAll('input, textarea, select');
        formFields.forEach(field => {
            field.addEventListener('blur', function() {
                // Validate required fields
                if (field.hasAttribute('required') && !field.value.trim()) {
                    field.classList.add('is-invalid');
                    
                    // Add error message if it doesn't exist
                    let errorElement = field.nextElementSibling;
                    if (!errorElement || !errorElement.classList.contains('form-error')) {
                        errorElement = document.createElement('div');
                        errorElement.className = 'form-error';
                        errorElement.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorElement, field.nextSibling);
                    }
                } else {
                    field.classList.remove('is-invalid');
                    
                    // Remove error message if it exists
                    const errorElement = field.nextElementSibling;
                    if (errorElement && errorElement.classList.contains('form-error')) {
                        errorElement.remove();
                    }
                }
                
                // Validate email fields
                if (field.type === 'email' && field.value.trim()) {
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailPattern.test(field.value)) {
                        field.classList.add('is-invalid');
                        
                        // Add error message if it doesn't exist
                        let errorElement = field.nextElementSibling;
                        if (!errorElement || !errorElement.classList.contains('form-error')) {
                            errorElement = document.createElement('div');
                            errorElement.className = 'form-error';
                            errorElement.textContent = 'Please enter a valid email address';
                            field.parentNode.insertBefore(errorElement, field.nextSibling);
                        }
                    }
                }
            });
        });
    });
} 