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
