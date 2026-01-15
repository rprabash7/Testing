document.addEventListener('DOMContentLoaded', function() {
    
    // Update Cart & Wishlist Count on Page Load
    updateCartCount();
    updateWishlistUI();
    
    // Wishlist Toggle
    document.querySelectorAll('.btn-wishlist-toggle').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const icon = this.querySelector('i');
            const isActive = this.classList.contains('active');
            
            if (isActive) {
                // Remove from wishlist
                removeFromWishlist(productId, this);
            } else {
                // Add to wishlist
                addToWishlist(productId, this);
            }
        });
    });
    
    // Add to Cart Quick
    document.querySelectorAll('.btn-add-to-cart-quick').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const productColor = this.dataset.productColor;
            
            addToCartQuick(productId, productName, productColor, this);
        });
    });
    
});

// Add to Wishlist
function addToWishlist(productId, btn) {
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/add-to-wishlist/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btn.classList.add('active');
            showToast('Success', 'Added to wishlist!', 'success');
            updateWishlistCount(data.count);
        } else {
            showToast('Info', data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error', 'Something went wrong!', 'error');
    });
}

// Remove from Wishlist
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
            showToast('Success', 'Removed from wishlist', 'success');
            updateWishlistCount(data.count);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Add to Cart Quick
function addToCartQuick(productId, productName, productColor, btn) {
    // Show loading
    btn.classList.add('loading');
    btn.innerHTML = '<i class="bi bi-arrow-repeat"></i> Adding...';
    
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
    .then(response => response.json())
    .then(data => {
        btn.classList.remove('loading');
        
        if (data.success) {
            // Success state
            btn.classList.add('success');
            btn.innerHTML = '<i class="bi bi-check-circle"></i> Added!';
            
            showToast('Added to Cart', productName, 'success');
            updateCartCount(data.count);
            
            // Reset button after 2 seconds
            setTimeout(() => {
                btn.classList.remove('success');
                btn.innerHTML = '<i class="bi bi-bag-plus"></i> Add to Cart';
            }, 2000);
        } else {
            btn.innerHTML = '<i class="bi bi-bag-plus"></i> Add to Cart';
            showToast('Error', data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btn.classList.remove('loading');
        btn.innerHTML = '<i class="bi bi-bag-plus"></i> Add to Cart';
        showToast('Error', 'Something went wrong!', 'error');
    });
}

// Update Cart Count
function updateCartCount(count = null) {
    if (count !== null) {
        document.getElementById('cartCount').textContent = count;
        if (count > 0) {
            document.getElementById('cartCount').style.display = 'block';
        }
    } else {
        // Fetch from session
        fetch('/get-cart-count/')
            .then(response => response.json())
            .then(data => {
                document.getElementById('cartCount').textContent = data.count;
                if (data.count > 0) {
                    document.getElementById('cartCount').style.display = 'block';
                }
            });
    }
}

// Update Wishlist Count
function updateWishlistCount(count) {
    const badge = document.getElementById('wishlistCount');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.classList.add('active');
        } else {
            badge.classList.remove('active');
        }
    }
}

// Update Wishlist UI (mark active items)
function updateWishlistUI() {
    fetch('/get-wishlist-items/')
        .then(response => response.json())
        .then(data => {
            updateWishlistCount(data.count);
            
            // Mark wishlist items as active
            data.items.forEach(productId => {
                const btn = document.querySelector(`.btn-wishlist-toggle[data-product-id="${productId}"]`);
                if (btn) {
                    btn.classList.add('active');
                }
            });
        });
}

// Show Toast Notification
function showToast(title, message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-circle-fill'}"></i>
        <div class="toast-content">
            <h5>${title}</h5>
            <p>${message}</p>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    document.body.appendChild(toast);
    
    // Close on click
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Get CSRF Token
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



// ... existing code ...

// Copy Coupon Code
document.querySelectorAll('.btn-copy-code').forEach(btn => {
    btn.addEventListener('click', function() {
        const code = this.dataset.code;
        
        // Copy to clipboard
        navigator.clipboard.writeText(code).then(() => {
            // Show success
            const couponElement = this.previousElementSibling;
            couponElement.classList.add('copied');
            
            // Change icon
            const icon = this.querySelector('i');
            icon.className = 'bi bi-check2';
            
            // Show toast
            showToast('Copied!', `Code "${code}" copied to clipboard`, 'success');
            
            // Reset after 2 seconds
            setTimeout(() => {
                couponElement.classList.remove('copied');
                icon.className = 'bi bi-clipboard';
            }, 2000);
        }).catch(err => {
            showToast('Error', 'Failed to copy code', 'error');
        });
    });
});
