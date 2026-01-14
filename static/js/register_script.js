document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.getElementById('registrationForm');
    const otpVerificationForm = document.getElementById('otpVerificationForm');
    const registerBtn = document.getElementById('registerBtn');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');
    const resendOtpBtn = document.getElementById('resendOtpBtn');
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordInput = document.getElementById('password');
    
    let registrationData = {};
    
    // Password Toggle
    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            
            const icon = passwordToggle.querySelector('i');
            if (type === 'password') {
                icon.className = 'bi bi-eye';
            } else {
                icon.className = 'bi bi-eye-slash';
            }
        });
    }
    
    // Phone number validation - only numbers
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
    
    // Register User
    registrationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = phoneInput.value.trim();
        const password = passwordInput.value;
        
        // Validation
        if (!name || !email || !phone || !password) {
            showError('registerError', 'registerErrorText', 'Please fill all fields');
            return;
        }
        
        if (phone.length !== 10) {
            showError('registerError', 'registerErrorText', 'Phone number must be 10 digits');
            return;
        }
        
        if (password.length < 6) {
            showError('registerError', 'registerErrorText', 'Password must be at least 6 characters');
            return;
        }
        
        // Store data for later
        registrationData = { name, email, phone, password };
        
        registerBtn.disabled = true;
        registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating Account...';
        
        const formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);
        formData.append('phone', phone);
        formData.append('password', password);
        
        fetch('/register-user/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide registration form, show OTP form
                registrationForm.style.display = 'none';
                otpVerificationForm.style.display = 'block';
                document.querySelector('.login-subtitle').textContent = 'Verify your email: ' + email;
            } else {
                showError('registerError', 'registerErrorText', data.message);
                registerBtn.disabled = false;
                registerBtn.innerHTML = '<span>Create Account</span><i class="bi bi-arrow-right-circle"></i>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('registerError', 'registerErrorText', 'Something went wrong. Please try again.');
            registerBtn.disabled = false;
            registerBtn.innerHTML = '<span>Create Account</span><i class="bi bi-arrow-right-circle"></i>';
        });
    });
    
    // Verify OTP
    otpVerificationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const otp = document.getElementById('otp').value.trim();
        
        if (!otp || otp.length !== 6) {
            showError('otpError', 'otpErrorText', 'Please enter valid 6-digit OTP');
            return;
        }
        
        verifyOtpBtn.disabled = true;
        verifyOtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Verifying...';
        
        const formData = new FormData();
        formData.append('otp', otp);
        
        fetch('/verify-registration-otp/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                alert('✅ Registration successful! Welcome to Manovastra!');
                // Redirect to home
                window.location.href = data.redirect_url;
            } else {
                showError('otpError', 'otpErrorText', data.message);
                verifyOtpBtn.disabled = false;
                verifyOtpBtn.innerHTML = '<span>Verify & Complete Registration</span><i class="bi bi-check-circle"></i>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('otpError', 'otpErrorText', 'Something went wrong. Please try again.');
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.innerHTML = '<span>Verify & Complete Registration</span><i class="bi bi-check-circle"></i>';
        });
    });
    
    // Resend OTP
    resendOtpBtn.addEventListener('click', function() {
        resendOtpBtn.disabled = true;
        resendOtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sending...';
        
        const formData = new FormData();
        formData.append('name', registrationData.name);
        formData.append('email', registrationData.email);
        formData.append('phone', registrationData.phone);
        formData.append('password', registrationData.password);
        
        fetch('/register-user/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ New OTP sent to your email!');
                document.getElementById('otp').value = '';
            } else {
                showError('otpError', 'otpErrorText', data.message);
            }
            resendOtpBtn.disabled = false;
            resendOtpBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Resend OTP';
        });
    });
    
    function showError(errorId, errorTextId, message) {
        const errorDiv = document.getElementById(errorId);
        const errorText = document.getElementById(errorTextId);
        errorText.textContent = message;
        errorDiv.style.display = 'block';
        
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
