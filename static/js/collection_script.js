document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Collection page loaded');

    // ========== SORTING ==========
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', this.value);
            currentUrl.searchParams.set('page', 1);
            window.location.href = currentUrl.toString();
        });
    }

    // ========== FILTER TOGGLE ==========
    const filterTitles = document.querySelectorAll('.filter-group-title');
    filterTitles.forEach(title => {
        title.addEventListener('click', function() {
            this.classList.toggle('collapsed');
            const content = this.nextElementSibling;
            if (content.style.display === 'none') {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        });
    });

    // ========== COLOR FILTER TOGGLE (Visual) ==========
    const colorFilterItems = document.querySelectorAll('.color-filter-item');
    colorFilterItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
            }
            
            if (this.querySelector('input').checked) {
                this.classList.add('active');
            } else {
                this.classList.remove('active');
            }
            
            applyFilters();
            updateActiveFilterTags();
        });
    });

    // ========== ALL FILTERS ==========
    const filterCheckboxes = document.querySelectorAll('.filter-checkbox input, .color-filter-item input');
    const productItems = document.querySelectorAll('.product-item');
    const activeFiltersDiv = document.querySelector('.active-filters');

    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            applyFilters();
            updateActiveFilterTags();
        });
    });

    // ========== APPLY FILTERS FUNCTION ==========
    function applyFilters() {
        // Get selected filters
        const selectedFabrics = Array.from(document.querySelectorAll('input[name="fabric"]:checked')).map(cb => cb.value);
        const selectedColors = Array.from(document.querySelectorAll('input[name="color"]:checked')).map(cb => cb.value);
        const selectedOccasions = Array.from(document.querySelectorAll('input[name="occasion"]:checked')).map(cb => cb.value);
        const selectedPrices = Array.from(document.querySelectorAll('input[name="price"]:checked')).map(cb => cb.value);
        const selectedDiscounts = Array.from(document.querySelectorAll('input[name="discount"]:checked')).map(cb => cb.value);
        const inStockOnly = document.querySelector('input[name="in_stock"]')?.checked;

        let visibleCount = 0;

        productItems.forEach(item => {
            let show = true;

            // Fabric filter
            if (selectedFabrics.length > 0) {
                const itemFabric = item.getAttribute('data-fabric');
                if (!selectedFabrics.includes(itemFabric)) show = false;
            }

            // Color filter
            if (selectedColors.length > 0 && show) {
                const itemColor = item.getAttribute('data-color');
                if (!selectedColors.includes(itemColor)) show = false;
            }

            // Occasion filter
            if (selectedOccasions.length > 0 && show) {
                const itemOccasions = item.getAttribute('data-occasion');
                let occasionMatch = false;
                selectedOccasions.forEach(occasion => {
                    if (itemOccasions.includes(occasion)) occasionMatch = true;
                });
                if (!occasionMatch) show = false;
            }

            // Price filter
            if (selectedPrices.length > 0 && show) {
                const itemPrice = parseFloat(item.getAttribute('data-price'));
                let priceMatch = false;
                selectedPrices.forEach(range => {
                    const [min, max] = range.split('-').map(Number);
                    if (itemPrice >= min && itemPrice <= max) priceMatch = true;
                });
                if (!priceMatch) show = false;
            }

            // Discount filter
            if (selectedDiscounts.length > 0 && show) {
                const itemDiscount = parseInt(item.getAttribute('data-discount'));
                const minDiscount = Math.max(...selectedDiscounts.map(Number));
                if (itemDiscount < minDiscount) show = false;
            }

            // Stock filter
            if (inStockOnly && show) {
                const inStock = item.getAttribute('data-in-stock') === 'True';
                if (!inStock) show = false;
            }

            // Show/hide product
            if (show) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        // Update results count
        const resultsCount = document.querySelector('.results-count');
        if (resultsCount) {
            resultsCount.textContent = `Showing ${visibleCount} of ${productItems.length} results`;
        }

        console.log('✅ Filters applied. Showing', visibleCount, 'products');
    }

    // ========== UPDATE ACTIVE FILTER TAGS ==========
    function updateActiveFilterTags() {
        if (!activeFiltersDiv) return;

        activeFiltersDiv.innerHTML = '';

        // Get all checked filters
        const checkedFilters = document.querySelectorAll('.filter-checkbox input:checked, .color-filter-item input:checked');
        
        checkedFilters.forEach(filter => {
            const filterName = filter.name;
            const filterValue = filter.value;
            let displayText = filterValue;

            // For color filters, get title
            if (filterName === 'color') {
                const colorItem = filter.closest('.color-filter-item');
                displayText = colorItem ? colorItem.getAttribute('title') : filterValue;
            }

            const tag = document.createElement('span');
            tag.className = 'active-filter-tag';
            tag.innerHTML = `${displayText} <i class="bi bi-x"></i>`;
            tag.dataset.filterName = filterName;
            tag.dataset.filterValue = filterValue;

            tag.addEventListener('click', function() {
                filter.checked = false;
                const colorItem = filter.closest('.color-filter-item');
                if (colorItem) colorItem.classList.remove('active');
                applyFilters();
                updateActiveFilterTags();
            });

            activeFiltersDiv.appendChild(tag);
        });

        // Add "Clear All" link if there are active filters
        if (checkedFilters.length > 0) {
            const clearAllLink = document.createElement('a');
            clearAllLink.href = '#';
            clearAllLink.className = 'clear-all-link';
            clearAllLink.textContent = 'Clear All';
            clearAllLink.addEventListener('click', function(e) {
                e.preventDefault();
                clearAllFilters();
            });
            activeFiltersDiv.appendChild(clearAllLink);
        }
    }

    // ========== CLEAR ALL FILTERS ==========
    function clearAllFilters() {
        filterCheckboxes.forEach(cb => cb.checked = false);
        colorFilterItems.forEach(item => item.classList.remove('active'));
        applyFilters();
        updateActiveFilterTags();
    }

    // Clear filters button
    const clearFiltersBtn = document.querySelector('.clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearAllFilters();
        });
    }

    // ========== WISHLIST ==========
    const wishlistBtns = document.querySelectorAll('.product-wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-heart')) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                this.style.color = '#e53e3e';
                console.log('❤️ Added to wishlist');
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                this.style.color = '';
                console.log('💔 Removed from wishlist');
            }
        });
    });

    // Initialize on load
    updateActiveFilterTags();

    console.log('✅✅✅ ALL COLLECTION FEATURES LOADED ✅✅✅');
});



// CSRF Token Helper
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

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== FILTER FUNCTIONALITY ==========
    
    const allProducts = document.querySelectorAll('.product-item');
    const activeFiltersContainer = document.getElementById('activeFilters');
    
    let selectedFilters = {
        price: [],
        fabric: [],
        color: [],
        occasion: [],
        discount: [],
        inStock: true
    };
    
    // Filter change event listeners
    document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const filterType = this.name;
            const filterValue = this.value;
            
            if (this.checked) {
                if (!selectedFilters[filterType].includes(filterValue)) {
                    selectedFilters[filterType].push(filterValue);
                }
            } else {
                selectedFilters[filterType] = selectedFilters[filterType].filter(v => v !== filterValue);
            }
            
            applyFilters();
            updateActiveFilters();
        });
    });
    
    // Color filter click
    document.querySelectorAll('.color-filter-item input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const colorValue = this.value;
            
            if (this.checked) {
                if (!selectedFilters.color.includes(colorValue)) {
                    selectedFilters.color.push(colorValue);
                }
            } else {
                selectedFilters.color = selectedFilters.color.filter(c => c !== colorValue);
            }
            
            applyFilters();
            updateActiveFilters();
        });
    });
    
    // Stock filter
    const stockCheckbox = document.querySelector('input[name="in_stock"]');
    if (stockCheckbox) {
        stockCheckbox.addEventListener('change', function() {
            selectedFilters.inStock = this.checked;
            applyFilters();
        });
    }
    
    // Apply Filters Function
    function applyFilters() {
        let visibleCount = 0;
        
        allProducts.forEach(product => {
            let shouldShow = true;
            
            // Price Filter
            if (selectedFilters.price.length > 0) {
                const price = parseFloat(product.dataset.price);
                let priceMatch = false;
                
                selectedFilters.price.forEach(range => {
                    const [min, max] = range.split('-').map(Number);
                    if (price >= min && price <= max) {
                        priceMatch = true;
                    }
                });
                
                if (!priceMatch) shouldShow = false;
            }
            
            // Fabric Filter
            if (selectedFilters.fabric.length > 0) {
                const productFabric = product.dataset.fabric;
                if (!selectedFilters.fabric.includes(productFabric)) {
                    shouldShow = false;
                }
            }
            
            // Color Filter
            if (selectedFilters.color.length > 0) {
                const productColor = product.dataset.color;
                if (!selectedFilters.color.includes(productColor)) {
                    shouldShow = false;
                }
            }
            
            // Occasion Filter
            if (selectedFilters.occasion.length > 0) {
                const productOccasions = product.dataset.occasion.split(',').map(o => o.trim());
                let occasionMatch = false;
                
                selectedFilters.occasion.forEach(selectedOccasion => {
                    if (productOccasions.includes(selectedOccasion)) {
                        occasionMatch = true;
                    }
                });
                
                if (!occasionMatch) shouldShow = false;
            }
            
            // Discount Filter
            if (selectedFilters.discount.length > 0) {
                const productDiscount = parseInt(product.dataset.discount);
                const maxDiscount = Math.max(...selectedFilters.discount.map(Number));
                
                if (productDiscount < maxDiscount) {
                    shouldShow = false;
                }
            }
            
            // Stock Filter
            if (selectedFilters.inStock) {
                const inStock = product.dataset.inStock === 'True';
                if (!inStock) shouldShow = false;
            }
            
            // Show/Hide Product
            if (shouldShow) {
                product.style.display = 'block';
                visibleCount++;
            } else {
                product.style.display = 'none';
            }
        });
        
        // Update results count
        const resultsCount = document.querySelector('.results-count');
        if (resultsCount) {
            const categoryName = resultsCount.textContent.split(' - ')[0];
            resultsCount.textContent = `${categoryName} - Showing ${visibleCount} results`;
        }
    }
    
    // Update Active Filters Display
    function updateActiveFilters() {
        activeFiltersContainer.innerHTML = '';
        
        let hasFilters = false;
        
        // Add filter badges
        Object.keys(selectedFilters).forEach(filterType => {
            if (filterType === 'inStock') return;
            
            selectedFilters[filterType].forEach(value => {
                hasFilters = true;
                
                const badge = document.createElement('span');
                badge.className = 'filter-badge';
                badge.innerHTML = `
                    ${value}
                    <i class="bi bi-x" data-filter-type="${filterType}" data-filter-value="${value}"></i>
                `;
                activeFiltersContainer.appendChild(badge);
                
                // Remove filter on badge click
                badge.querySelector('i').addEventListener('click', function() {
                    const type = this.dataset.filterType;
                    const val = this.dataset.filterValue;
                    
                    // Uncheck the checkbox
                    const checkbox = document.querySelector(`input[name="${type}"][value="${val}"]`);
                    if (checkbox) {
                        checkbox.checked = false;
                    }
                    
                    // Remove from selected filters
                    selectedFilters[type] = selectedFilters[type].filter(v => v !== val);
                    
                    applyFilters();
                    updateActiveFilters();
                });
            });
        });
        
        // Show/hide clear all button
        if (hasFilters) {
            activeFiltersContainer.style.display = 'flex';
        } else {
            activeFiltersContainer.style.display = 'none';
        }
    }
    
    // Clear All Filters
    document.querySelector('.clear-filters').addEventListener('click', function(e) {
        e.preventDefault();
        
        // Reset all checkboxes
        document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        document.querySelectorAll('.color-filter-item input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        // Reset filters object
        selectedFilters = {
            price: [],
            fabric: [],
            color: [],
            occasion: [],
            discount: [],
            inStock: true
        };
        
        // Show all products
        applyFilters();
        updateActiveFilters();
    });
    
    
    // ========== SORTING ==========
    
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', sortValue);
            window.location.href = currentUrl.toString();
        });
    }
    
    
    // ========== MOBILE FILTER TOGGLE ==========
    
    const filterToggle = document.querySelector('.btn-filter-toggle');
    const filtersSidebar = document.querySelector('.filters-sidebar');
    
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            filtersSidebar.classList.toggle('active');
            document.body.classList.toggle('filter-open');
        });
    }
    
    
    // ========== FILTER GROUP ACCORDION ==========
    
    document.querySelectorAll('.filter-group-title').forEach(title => {
        title.addEventListener('click', function() {
            this.parentElement.classList.toggle('collapsed');
        });
    });
    
    
    // ========== WISHLIST ==========
    
    document.querySelectorAll('.product-wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productCard = this.closest('.product-item');
            const productId = productCard.querySelector('.product-image-collection a').href.split('/').slice(-2, -1)[0];
            
            // Check if user is logged in (you can customize this)
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
                    this.classList.add('active');
                    this.innerHTML = '<i class="bi bi-heart-fill"></i>';
                    
                    // Show success message
                    showToast('Added to wishlist!', 'success');
                } else {
                    // Redirect to login if not logged in
                    if (data.message && data.message.includes('login')) {
                        window.location.href = '/login/';
                    } else {
                        showToast(data.message || 'Already in wishlist', 'info');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Please login to add to wishlist', 'error');
            });
        });
    });
    
    // Toast notification function
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 9999;
            font-weight: 500;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .filter-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #f3f4f6;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 14px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .filter-badge:hover {
        background: #e5e7eb;
    }
    
    .filter-badge i {
        cursor: pointer;
        font-weight: bold;
    }
    
    .product-wishlist-btn.active {
        color: #ef4444;
    }
    
    .color-filter-item input:checked + .color-swatch {
        border: 3px solid #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    .filter-group.collapsed .filter-group-content {
        display: none;
    }
    
    .filter-group-title {
        cursor: pointer;
        user-select: none;
    }
    
    @media (max-width: 991px) {
        .filters-sidebar {
            position: fixed;
            left: -100%;
            top: 0;
            height: 100vh;
            z-index: 999;
            background: white;
            width: 300px;
            transition: left 0.3s ease;
            overflow-y: auto;
        }
        
        .filters-sidebar.active {
            left: 0;
        }
        
        body.filter-open::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 998;
        }
    }
`;
document.head.appendChild(style);



// ========== WISHLIST (UPDATED) ==========

document.querySelectorAll('.product-wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const productId = this.dataset.productId; // Get from data attribute
        
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
                this.classList.add('active');
                this.innerHTML = '<i class="bi bi-heart-fill"></i>';
                showToast('Added to wishlist!', 'success');
            } else {
                if (data.message && data.message.includes('login')) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                } else {
                    showToast(data.message || 'Already in wishlist', 'info');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Redirect to login page
            window.location.href = '/login/?next=' + window.location.pathname;
        });
    });
});





document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Collection Script Loaded');

    const productItems = document.querySelectorAll('.product-item');
    const activeFiltersDiv = document.getElementById('activeFilters');
    const filtersSidebar = document.querySelector('.filters-sidebar');
    const filterToggle = document.querySelector('.btn-filter-toggle');

    // ===== SORTING =====
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const url = new URL(window.location.href);
            url.searchParams.set('sort', this.value);
            url.searchParams.set('page', 1);
            window.location.href = url.toString();
        });
    }

    // ===== FILTER STATE =====
    let selectedFilters = {
        price: [],
        fabric: [],
        color: [],
        occasion: [],
        discount: [],
        inStock: true
    };

    // ===== ACCORDION =====
    document.querySelectorAll('.filter-group-title').forEach(title => {
        title.addEventListener('click', function() {
            this.parentElement.classList.toggle('collapsed');
        });
    });

    // ===== MOBILE FILTER TOGGLE =====
    if (filterToggle && filtersSidebar) {
        filterToggle.addEventListener('click', function() {
            filtersSidebar.classList.toggle('active');
            document.body.classList.toggle('filter-open');
        });
    }

    // ===== NORMAL CHECKBOX FILTERS =====
    document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', function() {
            const name = this.name;
            const value = this.value;

            if (name === 'in_stock') {
                selectedFilters.inStock = this.checked;
                applyFilters();
                updateActiveFiltersUI();
                return;
            }

            if (this.checked) {
                if (!selectedFilters[name].includes(value)) {
                    selectedFilters[name].push(value);
                }
            } else {
                selectedFilters[name] = selectedFilters[name].filter(v => v !== value);
            }

            applyFilters();
            updateActiveFiltersUI();
        });
    });

    // ===== COLOR FILTER (visual + state) =====
    document.querySelectorAll('.color-filter-item').forEach(item => {
        const cb = item.querySelector('input[type="checkbox"]');
        item.addEventListener('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                cb.checked = !cb.checked;
            }

            const value = cb.value;

            if (cb.checked) {
                item.classList.add('active');
                if (!selectedFilters.color.includes(value)) {
                    selectedFilters.color.push(value);
                }
            } else {
                item.classList.remove('active');
                selectedFilters.color = selectedFilters.color.filter(c => c !== value);
            }

            applyFilters();
            updateActiveFiltersUI();
        });
    });

    // ===== APPLY FILTERS =====
    function applyFilters() {
        let visibleCount = 0;

        productItems.forEach(item => {
            let show = true;

            const itemFabric = item.dataset.fabric;
            const itemColor = item.dataset.color;
            const itemOccasionRaw = item.dataset.occasion || '';
            const itemOccasions = itemOccasionRaw.split(',').map(o => o.trim());
            const itemPrice = parseFloat(item.dataset.price);
            const itemDiscount = parseInt(item.dataset.discount);
            const inStock = item.dataset.inStock === 'True';

            // Fabric
            if (selectedFilters.fabric.length > 0) {
                if (!selectedFilters.fabric.includes(itemFabric)) show = false;
            }

            // Color
            if (selectedFilters.color.length > 0 && show) {
                if (!selectedFilters.color.includes(itemColor)) show = false;
            }

            // Occasion
            if (selectedFilters.occasion.length > 0 && show) {
                let match = false;
                selectedFilters.occasion.forEach(o => {
                    if (itemOccasions.includes(o)) match = true;
                });
                if (!match) show = false;
            }

            // Price
            if (selectedFilters.price.length > 0 && show) {
                let priceMatch = false;
                selectedFilters.price.forEach(range => {
                    const [min, max] = range.split('-').map(Number);
                    if (itemPrice >= min && itemPrice <= max) priceMatch = true;
                });
                if (!priceMatch) show = false;
            }

            // Discount
            if (selectedFilters.discount.length > 0 && show) {
                const minDiscount = Math.max(...selectedFilters.discount.map(Number));
                if (itemDiscount < minDiscount) show = false;
            }

            // In stock
            if (selectedFilters.inStock && show) {
                if (!inStock) show = false;
            }

            if (show) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        const resultsCount = document.querySelector('.results-count');
        if (resultsCount) {
            const catName = resultsCount.textContent.split(' - ')[0];
            resultsCount.textContent = `${catName} - Showing ${visibleCount} results`;
        }

        console.log('Filters applied, visible:', visibleCount);
    }

    // ===== ACTIVE FILTER TAGS TOP BAR =====
    function updateActiveFiltersUI() {
        if (!activeFiltersDiv) return;
        activeFiltersDiv.innerHTML = '';

        let hasFilters = false;

        Object.keys(selectedFilters).forEach(type => {
            if (type === 'inStock') return;

            selectedFilters[type].forEach(value => {
                hasFilters = true;
                const tag = document.createElement('span');
                tag.className = 'filter-badge';
                tag.innerHTML = `
                    ${value}
                    <i class="bi bi-x" data-type="${type}" data-value="${value}"></i>
                `;
                tag.querySelector('i').addEventListener('click', function() {
                    const t = this.dataset.type;
                    const v = this.dataset.value;

                    // uncheck checkbox
                    const cb = document.querySelector(`input[name="${t}"][value="${v}"]`);
                    if (cb) cb.checked = false;

                    if (t === 'color' && cb) {
                        const colorItem = cb.closest('.color-filter-item');
                        if (colorItem) colorItem.classList.remove('active');
                    }

                    selectedFilters[t] = selectedFilters[t].filter(x => x !== v);
                    applyFilters();
                    updateActiveFiltersUI();
                });
                activeFiltersDiv.appendChild(tag);
            });
        });

        if (hasFilters || !selectedFilters.inStock) {
            const clearLink = document.createElement('a');
            clearLink.href = '#';
            clearLink.className = 'clear-all-link';
            clearLink.textContent = 'Clear All';
            clearLink.addEventListener('click', function(e) {
                e.preventDefault();
                clearAllFilters();
            });
            activeFiltersDiv.appendChild(clearLink);
            activeFiltersDiv.style.display = 'flex';
        } else {
            activeFiltersDiv.style.display = 'none';
        }
    }

    function clearAllFilters() {
        selectedFilters = {
            price: [],
            fabric: [],
            color: [],
            occasion: [],
            discount: [],
            inStock: true
        };

        document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(cb => {
            if (cb.name === 'in_stock') cb.checked = true;
            else cb.checked = false;
        });

        document.querySelectorAll('.color-filter-item').forEach(item => {
            item.classList.remove('active');
            const cb = item.querySelector('input[type="checkbox"]');
            cb.checked = false;
        });

        applyFilters();
        updateActiveFiltersUI();
    }

    const clearFiltersBtn = document.querySelector('.clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearAllFilters();
        });
    }

    console.log('✅ Collection filters initialized');
});
