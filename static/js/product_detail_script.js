document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Product Detail Script Loaded');
    
    // Check if data exists
    if (typeof IMAGES_BY_COLOR === 'undefined') {
        console.error('❌ IMAGES_BY_COLOR not defined!');
        return;
    }
    
    console.log('📦 Images by color:', IMAGES_BY_COLOR);

    const mainImageContainer = document.getElementById('mainImageContainer');
    const thumbnailGallery = document.getElementById('thumbnailGallery');
    const selectedColorName = document.getElementById('selectedColorName');
    const colorSwatches = document.querySelectorAll('.color-swatch');

    // ✅ ADD: Store selected color ID globally
    let selectedColorId = null;

    // ========== 1. COLOR SWITCHING ==========
    colorSwatches.forEach(function(swatch) {
        swatch.addEventListener('click', function(e) {
            e.preventDefault();
            
            const colorId = this.getAttribute('data-color-id');
            const colorName = this.getAttribute('data-color-name');
            
            // ✅ STORE COLOR ID
            selectedColorId = colorId;
            
            console.log('🎨 Color clicked:', colorName, '| ID:', colorId);

            // Update active swatch
            colorSwatches.forEach(function(s) {
                s.classList.remove('active');
            });
            this.classList.add('active');

            // Update color name display
            if (selectedColorName) {
                selectedColorName.textContent = colorName;
            }

            // Get images for this color
            const colorImages = IMAGES_BY_COLOR[colorId];
            
            if (!colorImages || colorImages.length === 0) {
                console.warn('⚠️ No images found for color ID:', colorId);
                mainImageContainer.innerHTML = '<div class="main-image-placeholder">No images available</div>';
                thumbnailGallery.innerHTML = '';
                return;
            }

            console.log('✅ Found', colorImages.length, 'images for', colorName);

            // Update main image to first image of selected color
            const firstImage = colorImages[0];
            mainImageContainer.innerHTML = '<img src="' + firstImage.url + '" alt="' + colorName + '" id="mainImage" style="width: 100%; height: 100%; object-fit: cover;">';

            // Clear and rebuild thumbnails
            thumbnailGallery.innerHTML = '';
            
            colorImages.forEach(function(img, index) {
                const thumbDiv = document.createElement('div');
                thumbDiv.className = 'thumbnail-item' + (index === 0 ? ' active' : '');
                thumbDiv.setAttribute('data-image', img.url);
                thumbDiv.innerHTML = '<img src="' + img.url + '" alt="Thumbnail ' + (index + 1) + '" style="width: 100%; height: 100%; object-fit: cover;">';
                thumbnailGallery.appendChild(thumbDiv);
            });

            console.log('✅ Thumbnails updated:', colorImages.length, 'images');

            // Re-attach thumbnail click events
            attachThumbnailClickEvents();
        });
    });

    // ✅ SET DEFAULT COLOR ID ON PAGE LOAD
    const activeColorSwatch = document.querySelector('.color-swatch.active');
    if (activeColorSwatch) {
        selectedColorId = activeColorSwatch.getAttribute('data-color-id');
        console.log('✅ Default color ID set:', selectedColorId);
    }

    // ========== 2. THUMBNAIL CLICKING ==========
    function attachThumbnailClickEvents() {
        const thumbnails = document.querySelectorAll('.thumbnail-item');
        
        thumbnails.forEach(function(thumb) {
            thumb.addEventListener('click', function() {
                const imageUrl = this.getAttribute('data-image');
                
                console.log('🖼️ Thumbnail clicked:', imageUrl);
                
                // Remove active from all thumbnails
                thumbnails.forEach(function(t) {
                    t.classList.remove('active');
                });
                
                // Add active to clicked thumbnail
                this.classList.add('active');
                
                // Update main image
                mainImageContainer.innerHTML = '<img src="' + imageUrl + '" alt="Product" id="mainImage" style="width: 100%; height: 100%; object-fit: cover;">';
                
                console.log('✅ Main image updated');
            });
        });
        
        console.log('✅ Thumbnail events attached to', thumbnails.length, 'thumbnails');
    }

    // Initial attach for default thumbnails
    attachThumbnailClickEvents();

    // ========== 3. QUANTITY CONTROLS ==========
    const qtyInput = document.querySelector('.qty-input');
    const qtyIncrease = document.querySelector('.qty-increase');
    const qtyDecrease = document.querySelector('.qty-decrease');

    if (qtyIncrease && qtyInput) {
        qtyIncrease.addEventListener('click', function() {
            let val = parseInt(qtyInput.value) || 1;
            if (val < 10) {
                qtyInput.value = val + 1;
                console.log('➕ Quantity:', qtyInput.value);
            }
        });
    }

    if (qtyDecrease && qtyInput) {
        qtyDecrease.addEventListener('click', function() {
            let val = parseInt(qtyInput.value) || 1;
            if (val > 1) {
                qtyInput.value = val - 1;
                console.log('➖ Quantity:', qtyInput.value);
            }
        });
    }

    // ========== 4. WISHLIST TOGGLE ==========
    const wishlistBtns = document.querySelectorAll('.btn-wishlist-desktop, .btn-wishlist-mobile');
    
    wishlistBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            this.classList.toggle('active');
            const icon = this.querySelector('i');
            
            if (this.classList.contains('active')) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                console.log('❤️ Added to wishlist');
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                console.log('💔 Removed from wishlist');
            }
        });
    });

    // ========== 5. ADD TO CART ==========
    const addToCartBtns = document.querySelectorAll('.btn-add-cart, .btn-add-cart-mobile');
    
    addToCartBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const qty = qtyInput ? qtyInput.value : 1;
            const color = selectedColorName ? selectedColorName.textContent : 'Default';
            
            console.log('🛒 Add to cart - Qty:', qty, '| Color:', color);
            
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="bi bi-check-circle-fill"></i> Added!';
            this.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
            
            setTimeout(function() {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
            }.bind(this), 2000);
        });
    });

    // ========== 6. BUY NOW - FIXED VERSION ==========
    const buyNowBtns = document.querySelectorAll('.btn-buy-now, .btn-buy-now-mobile, #buyNowBtn');
    
    // In your product_detail JavaScript file
// Find the Buy Now button click handler and replace with this:

buyNowBtns.forEach(function(btn) {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        
        const qty = qtyInput ? parseInt(qtyInput.value) : 1;
        
        // ✅ Get first color if available
        const activeColor = document.querySelector('.color-swatch.active');
        const colorId = activeColor ? activeColor.getAttribute('data-color-id') : null;
        
        console.log('⚡ Buy Now clicked');
        console.log('  - Color ID:', colorId);
        console.log('  - Quantity:', qty);
        
        // Disable button
        btn.disabled = true;
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
        
        // Get product slug from URL
        const productSlug = window.location.pathname.split('/')[2];
        
        // Send request
        fetch('/product/' + productSlug + '/buy-now/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                color_id: colorId,
                quantity: qty
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            
            // Check if redirected to login
            if (response.redirected && response.url.includes('/login/')) {
                if (confirm('⚠️ Please login to continue!\n\nClick OK to go to Login page')) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                }
                btn.disabled = false;
                btn.innerHTML = originalHTML;
                return null;
            }
            
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            
            if (!data) return;
            
            if (data.success) {
                console.log('✅ Buy Now successful');
                
                if (data.show_address_modal) {
                    // Show address modal
                    const addressModal = new bootstrap.Modal(document.getElementById('addressModal'));
                    addressModal.show();
                } else if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
                
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            } else {
                console.error('❌ Error:', data.message);
                alert('❌ ' + (data.message || 'An error occurred'));
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            }
        })
        .catch(error => {
            console.error('❌ Fetch Error:', error);
            alert('Network error. Please check your connection and try again.');
            btn.disabled = false;
            btn.innerHTML = originalHTML;
        });
    });
});


    // ========== PINCODE CHECKER ==========
    const checkPincodeBtn = document.getElementById('checkPincodeBtn');
    const pincodeInput = document.getElementById('pincodeInput');
    const pincodeResult = document.getElementById('pincodeResult');

    if (checkPincodeBtn && pincodeInput) {
        checkPincodeBtn.addEventListener('click', function() {
            const pincode = pincodeInput.value.trim();
            
            if (!pincode || pincode.length !== 6) {
                showPincodeError('Please enter a valid 6-digit pincode');
                return;
            }
            
            checkPincodeBtn.disabled = true;
            checkPincodeBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Checking...';
            
            fetch('/check-pincode/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: 'pincode=' + pincode
            })
            .then(response => response.json())
            .then(data => {
                checkPincodeBtn.disabled = false;
                checkPincodeBtn.innerHTML = 'Check';
                
                if (data.success && data.serviceable) {
                    showPincodeSuccess(data);
                } else {
                    showPincodeError(data.message || 'Pincode not serviceable');
                }
            })
            .catch(error => {
                checkPincodeBtn.disabled = false;
                checkPincodeBtn.innerHTML = 'Check';
                showPincodeError('Error checking pincode. Please try again.');
                console.error('Error:', error);
            });
        });
    }

    function showPincodeSuccess(data) {
        pincodeResult.style.display = 'block';
        pincodeResult.className = 'pincode-result success';
        pincodeResult.innerHTML = `
            <div class="pincode-success">
                <i class="bi bi-check-circle-fill"></i>
                <strong>Delivery available to ${data.city}, ${data.state}</strong>
            </div>
            <div class="delivery-info-list mt-3">
                <div class="delivery-info-item">
                    <i class="bi bi-box-seam"></i>
                    <div>
                        <strong>Standard Delivery</strong>
                        <p>Delivery by ${data.standard_delivery.date} | Free</p>
                    </div>
                </div>
                <div class="delivery-info-item">
                    <i class="bi bi-lightning-charge"></i>
                    <div>
                        <strong>Express Delivery</strong>
                        <p>Delivery by ${data.express_delivery.date} | ₹${data.express_delivery.charge}</p>
                    </div>
                </div>
                ${data.cod_available ? `
                <div class="delivery-info-item">
                    <i class="bi bi-cash-coin"></i>
                    <div>
                        <strong>Cash on Delivery Available</strong>
                        <p>Pay when you receive the product</p>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }

    function showPincodeError(message) {
        pincodeResult.style.display = 'block';
        pincodeResult.className = 'pincode-result error';
        pincodeResult.innerHTML = `
            <div class="pincode-error">
                <i class="bi bi-x-circle-fill"></i>
                <strong>${message}</strong>
            </div>
        `;
    }

    console.log('✅✅✅ ALL FUNCTIONALITY LOADED SUCCESSFULLY ✅✅✅');
});

// Get CSRF token function
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
