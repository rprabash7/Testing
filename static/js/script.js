// ========================================
// MANOVASTRA E-COMMERCE - MAIN SCRIPT
// Business-Ready Version 2026
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Manovastra initialized');
    
    // Initialize all functions
    initializeApp();
    initializeWishlist();
    initializeCart();
    initializeBackToTop();
    initializeNewsletterForm();
});

// ========================================
// INITIALIZATION
// ========================================

function initializeApp() {
    updateCartCount();
    updateWishlistUI();
    
    // Mobile menu toggle (if needed)
    const mobileMenu = document.querySelector('.mobile-menu-toggle');
    if (mobileMenu) {
        mobileMenu.addEventListener('click', toggleMobileMenu);
    }
    
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
}

// ========================================
// WISHLIST FUNCTIONALITY
// ========================================

function initializeWishlist() {
    const wishlistButtons = document.querySelectorAll('.btn-wishlist-toggle');
    
    wishlistButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const isActive = this.classList.contains('active');
            
            if (isActive) {
                removeFromWishlist(productId, this);
            } else {
                addToWishlist(productId, this);
            }
        });
    });
}

function addToWishlist(productId, btn) {
    // Add loading state
    btn.classList.add('loading');
    btn.disabled = true;
    
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/add-to-wishlist/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => {
        if (response.status === 302 || response.redirected) {
            showToast('Login Required', 'Please login to add items to wishlist', 'warning');
            setTimeout(() => window.location.href = '/login/', 1500);
            return null;
        }
        return response.json();
    })
    .then(data => {
        btn.classList.remove('loading');
        btn.disabled = false;
        
        if (data && data.success) {
            btn.classList.add('active');
            btn.querySelector('i').classList.replace('bi-heart', 'bi-heart-fill');
            showToast('Added to Wishlist', 'Item added successfully!', 'success');
            updateWishlistCount(data.count);
            
            // Animate button
            btn.style.transform = 'scale(1.2)';
            setTimeout(() => btn.style.transform = 'scale(1)', 300);
        } else if (data) {
            showToast('Info', data.message, 'info');
        }
    })
    .catch(error => {
        console.error('Wishlist Error:', error);
        btn.classList.remove('loading');
        btn.disabled = false;
        showToast('Error', 'Please login to continue', 'error');
        setTimeout(() => window.location.href = '/login/', 1500);
    });
}

function removeFromWishlist(productId, btn) {
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/remove-from-wishlist/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btn.classList.remove('active');
            btn.querySelector('i').classList.replace('bi-heart-fill', 'bi-heart');
            showToast('Removed', 'Item removed from wishlist', 'success');
            updateWishlistCount(data.count);
            
            // If on wishlist page, remove the card
            const card = btn.closest('.product-card');
            if (card && window.location.pathname.includes('wishlist')) {
                card.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => card.remove(), 300);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error', 'Something went wrong!', 'error');
    });
}

function updateWishlistUI() {
    fetch('/get-wishlist-items/')
        .then(response => response.json())
        .then(data => {
            updateWishlistCount(data.count);
            
            // Mark items as in wishlist
            data.items.forEach(productId => {
                const btn = document.querySelector(`.btn-wishlist-toggle[data-product-id="${productId}"]`);
                if (btn) {
                    btn.classList.add('active');
                    const icon = btn.querySelector('i');
                    if (icon && icon.classList.contains('bi-heart')) {
                        icon.classList.replace('bi-heart', 'bi-heart-fill');
                    }
                }
            });
        })
        .catch(error => console.error('Wishlist UI Error:', error));
}

function updateWishlistCount(count) {
    const badge = document.getElementById('wishlistCount');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'block';
            badge.classList.add('pulse');
        } else {
            badge.style.display = 'none';
        }
    }
}

// ========================================
// CART FUNCTIONALITY
// ========================================

function initializeCart() {
    const cartButtons = document.querySelectorAll('.btn-add-to-cart-quick');
    
    cartButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const productColor = this.dataset.productColor || 'Default';
            
            addToCartQuick(productId, productName, productColor, this);
        });
    });
}

function addToCartQuick(productId, productName, productColor, btn) {
    // Show loading state
    const originalHTML = btn.innerHTML;
    btn.classList.add('loading');
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';
    btn.disabled = true;
    
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', 1);
    formData.append('color', productColor);
    
    fetch('/add-to-cart/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => {
        if (response.status === 302 || response.redirected) {
            showToast('Login Required', 'Please login to add items to cart', 'warning');
            setTimeout(() => window.location.href = '/login/', 1500);
            return null;
        }
        return response.json();
    })
    .then(data => {
        btn.classList.remove('loading');
        btn.disabled = false;
        
        if (data && data.success) {
            // Success animation
            btn.classList.add('success');
            btn.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Added!';
            
            showToast('Added to Cart', `${productName} added successfully`, 'success');
            updateCartCount(data.count);
            
            // Reset button after 2 seconds
            setTimeout(() => {
                btn.classList.remove('success');
                btn.innerHTML = originalHTML;
            }, 2000);
        } else if (data) {
            btn.innerHTML = originalHTML;
            showToast('Error', data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Cart Error:', error);
        btn.classList.remove('loading');
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        showToast('Error', 'Please login to continue', 'error');
        setTimeout(() => window.location.href = '/login/', 1500);
    });
}

function updateCartCount(count = null) {
    const badge = document.getElementById('cartCount');
    
    if (count !== null) {
        if (badge) {
            badge.textContent = count;
            if (count > 0) {
                badge.style.display = 'block';
                badge.classList.add('pulse');
            } else {
                badge.style.display = 'none';
            }
        }
    } else {
        // Fetch from server
        fetch('/get-cart-count/')
            .then(response => response.json())
            .then(data => {
                if (badge) {
                    badge.textContent = data.count;
                    if (data.count > 0) {
                        badge.style.display = 'block';
                    }
                }
            })
            .catch(error => console.error('Cart Count Error:', error));
    }
}

// ========================================
// COUPON CODE FUNCTIONALITY
// ========================================

document.querySelectorAll('.btn-copy-code').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const code = this.dataset.code;
        
        // Modern clipboard API
        if (navigator.clipboard) {
            navigator.clipboard.writeText(code).then(() => {
                copyCodeSuccess(this, code);
            }).catch(err => {
                fallbackCopyCode(code);
            });
        } else {
            fallbackCopyCode(code);
        }
    });
});

function copyCodeSuccess(btn, code) {
    const icon = btn.querySelector('i');
    const originalIcon = icon.className;
    
    // Change to check icon
    icon.className = 'bi bi-check2-circle';
    btn.classList.add('copied');
    
    showToast('Copied!', `Code "${code}" copied to clipboard`, 'success');
    
    // Reset after 2 seconds
    setTimeout(() => {
        icon.className = originalIcon;
        btn.classList.remove('copied');
    }, 2000);
}

function fallbackCopyCode(code) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = code;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied!', `Code "${code}" copied`, 'success');
    } catch (err) {
        showToast('Error', 'Failed to copy code', 'error');
    }
    
    document.body.removeChild(textArea);
}

// ========================================
// NEWSLETTER FORM
// ========================================

function initializeNewsletterForm() {
    const form = document.getElementById('newsletterForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = form.querySelector('input[name="email"]');
            const submitBtn = form.querySelector('button[type="submit"]');
            const email = emailInput.value.trim();
            
            if (!email || !isValidEmail(email)) {
                showToast('Invalid Email', 'Please enter a valid email address', 'error');
                return;
            }
            
            // Show loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Subscribing...';
            
            // Simulate API call (replace with actual endpoint)
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Subscribed!';
                emailInput.value = '';
                showToast('Success!', 'Thank you for subscribing!', 'success');
                
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Subscribe Now';
                }, 2000);
            }, 1500);
        });
    }
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ========================================
// BACK TO TOP BUTTON
// ========================================

function initializeBackToTop() {
    const backToTop = document.getElementById('backToTop');
    
    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        });
        
        backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// ========================================
// TOAST NOTIFICATIONS
// ========================================

function showToast(title, message, type = 'success') {
    // Remove existing toasts
    document.querySelectorAll('.toast-notification').forEach(t => t.remove());
    
    const icons = {
        success: 'check-circle-fill',
        error: 'exclamation-circle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill'
    };
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type} animate__animated animate__fadeInRight`;
    toast.style.borderLeft = `4px solid ${colors[type]}`;
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="bi bi-${icons[type]}" style="color: ${colors[type]};"></i>
        </div>
        <div class="toast-content">
            <h5 class="toast-title">${title}</h5>
            <p class="toast-message">${message}</p>
        </div>
        <button class="toast-close" aria-label="Close">&times;</button>
    `;
    
    document.body.appendChild(toast);
    
    // Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.classList.replace('animate__fadeInRight', 'animate__fadeOutRight');
        setTimeout(() => toast.remove(), 300);
    });
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.replace('animate__fadeInRight', 'animate__fadeOutRight');
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

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

function toggleMobileMenu() {
    const menu = document.querySelector('.navbar-main');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// ========================================
// PERFORMANCE OPTIMIZATION
// ========================================

// Lazy load images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ========================================
// ERROR HANDLING
// ========================================

window.addEventListener('error', function(e) {
    console.error('Global Error:', e.error);
    // Could send to analytics or logging service
});

// ========================================
// CONSOLE MESSAGE
// ========================================

console.log('%c🎉 Manovastra E-Commerce ', 'background: #667eea; color: white; font-size: 16px; padding: 10px;');
console.log('%cBusiness Ready v1.0 - 2026', 'color: #667eea; font-size: 12px;');



