document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('emailForm');
    const otpForm = document.getElementById('otpForm');
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');
    const resendOtpBtn = document.getElementById('resendOtpBtn');
    const emailInput = document.getElementById('email');
    const otpInput = document.getElementById('otp');
    
    let userEmail = '';
    
    // Send OTP
    emailForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        userEmail = emailInput.value.trim();
        
        if (!userEmail) {
            showError('emailError', 'emailErrorText', 'Please enter your email');
            return;
        }
        
        sendOtpBtn.disabled = true;
        sendOtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sending...';
        
        fetch('/send-login-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'email=' + encodeURIComponent(userEmail)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide email form, show OTP form
                emailForm.style.display = 'none';
                otpForm.style.display = 'block';
                document.querySelector('.login-subtitle').textContent = 'OTP sent to ' + userEmail;
            } else {
                showError('emailError', 'emailErrorText', data.message);
                sendOtpBtn.disabled = false;
                sendOtpBtn.innerHTML = '<span>Send OTP</span><i class="bi bi-arrow-right-circle"></i>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('emailError', 'emailErrorText', 'Something went wrong. Please try again.');
            sendOtpBtn.disabled = false;
            sendOtpBtn.innerHTML = '<span>Send OTP</span><i class="bi bi-arrow-right-circle"></i>';
        });
    });
    
    // Verify OTP
    otpForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const otp = otpInput.value.trim();
        
        if (!otp || otp.length !== 6) {
            showError('otpError', 'otpErrorText', 'Please enter valid 6-digit OTP');
            return;
        }
        
        verifyOtpBtn.disabled = true;
        verifyOtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Verifying...';
        
        const formData = new FormData();
        formData.append('email', userEmail);
        formData.append('otp', otp);
        
        fetch('/verify-login-otp/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to home
                window.location.href = data.redirect_url;
            } else {
                showError('otpError', 'otpErrorText', data.message);
                verifyOtpBtn.disabled = false;
                verifyOtpBtn.innerHTML = '<span>Verify & Login</span><i class="bi bi-check-circle"></i>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('otpError', 'otpErrorText', 'Something went wrong. Please try again.');
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.innerHTML = '<span>Verify & Login</span><i class="bi bi-check-circle"></i>';
        });
    });
    
    // Resend OTP
    resendOtpBtn.addEventListener('click', function() {
        resendOtpBtn.disabled = true;
        resendOtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sending...';
        
        fetch('/send-login-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'email=' + encodeURIComponent(userEmail)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('otpTimer').textContent = 'New OTP sent successfully!';
                otpInput.value = '';
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
