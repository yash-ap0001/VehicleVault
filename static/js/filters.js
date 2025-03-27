document.addEventListener('DOMContentLoaded', function() {
    // Price range filter
    const priceRange = document.getElementById('price-range');
    const minPriceDisplay = document.getElementById('min-price-display');
    const maxPriceDisplay = document.getElementById('max-price-display');
    const minPriceInput = document.getElementById('min_price');
    const maxPriceInput = document.getElementById('max_price');
    
    if (priceRange && minPriceDisplay && maxPriceDisplay && minPriceInput && maxPriceInput) {
        // Get initial values from inputs if they exist
        const initialMin = minPriceInput.value ? parseInt(minPriceInput.value) : 0;
        const initialMax = maxPriceInput.value ? parseInt(maxPriceInput.value) : 10000000;
        
        noUiSlider.create(priceRange, {
            start: [initialMin, initialMax],
            connect: true,
            step: 50000,
            range: {
                'min': 0,
                'max': 10000000
            },
            format: {
                to: function(value) {
                    return Math.round(value);
                },
                from: function(value) {
                    return Math.round(value);
                }
            }
        });
        
        priceRange.noUiSlider.on('update', function(values, handle) {
            const value = values[handle];
            
            if (handle === 0) {
                minPriceDisplay.textContent = formatPrice(value);
                minPriceInput.value = value;
            } else {
                maxPriceDisplay.textContent = formatPrice(value);
                maxPriceInput.value = value;
            }
        });
    }
    
    // Year range filter
    const yearRange = document.getElementById('year-range');
    const minYearDisplay = document.getElementById('min-year-display');
    const maxYearDisplay = document.getElementById('max-year-display');
    const minYearInput = document.getElementById('min_year');
    const maxYearInput = document.getElementById('max_year');
    
    if (yearRange && minYearDisplay && maxYearDisplay && minYearInput && maxYearInput) {
        const currentYear = new Date().getFullYear();
        
        // Get initial values from inputs if they exist
        const initialMinYear = minYearInput.value ? parseInt(minYearInput.value) : 2000;
        const initialMaxYear = maxYearInput.value ? parseInt(maxYearInput.value) : currentYear;
        
        noUiSlider.create(yearRange, {
            start: [initialMinYear, initialMaxYear],
            connect: true,
            step: 1,
            range: {
                'min': 1990,
                'max': currentYear
            },
            format: {
                to: function(value) {
                    return Math.round(value);
                },
                from: function(value) {
                    return Math.round(value);
                }
            }
        });
        
        yearRange.noUiSlider.on('update', function(values, handle) {
            const value = values[handle];
            
            if (handle === 0) {
                minYearDisplay.textContent = value;
                minYearInput.value = value;
            } else {
                maxYearDisplay.textContent = value;
                maxYearInput.value = value;
            }
        });
    }
    
    // Brand-model chained dropdown
    const brandSelect = document.getElementById('brand');
    const modelSelect = document.getElementById('model');
    
    if (brandSelect && modelSelect) {
        brandSelect.addEventListener('change', function() {
            const brand = this.value;
            if (brand) {
                // Clear current options
                modelSelect.innerHTML = '<option value="">All Models</option>';
                
                // Fetch models for the selected brand
                fetch(`/api/models/${brand}`)
                    .then(response => response.json())
                    .then(models => {
                        models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            modelSelect.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching models:', error));
            } else {
                // Clear model select if no brand selected
                modelSelect.innerHTML = '<option value="">All Models</option>';
            }
        });
    }
    
    // Mobile filter toggle
    const filterToggleBtn = document.getElementById('filter-toggle');
    const filterContainer = document.getElementById('filter-container');
    
    if (filterToggleBtn && filterContainer) {
        filterToggleBtn.addEventListener('click', function() {
            filterContainer.classList.toggle('show-filters');
            
            // Update button text
            if (filterContainer.classList.contains('show-filters')) {
                this.textContent = 'Hide Filters';
            } else {
                this.textContent = 'Show Filters';
            }
        });
    }
    
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Reset all inputs
            const form = this.closest('form');
            const inputs = form.querySelectorAll('input:not([type=hidden]), select');
            
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'number' || input.tagName === 'SELECT') {
                    input.value = '';
                } else if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                }
            });
            
            // Reset range sliders if they exist
            if (priceRange && priceRange.noUiSlider) {
                priceRange.noUiSlider.set([0, 10000000]);
            }
            
            if (yearRange && yearRange.noUiSlider) {
                const currentYear = new Date().getFullYear();
                yearRange.noUiSlider.set([1990, currentYear]);
            }
            
            // Submit form to clear all filters
            form.submit();
        });
    }

    // Format price helper function
    function formatPrice(price) {
        price = parseInt(price);
        if (price >= 10000000) {
            return '₹ ' + (price / 10000000).toFixed(2) + ' Cr';
        } else if (price >= 100000) {
            return '₹ ' + (price / 100000).toFixed(2) + ' Lakh';
        } else {
            return '₹ ' + price.toLocaleString('en-IN');
        }
    }
    
    // Quick filter buttons
    const quickFilterButtons = document.querySelectorAll('.quick-filter');
    
    quickFilterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filterType;
            const filterValue = this.dataset.filterValue;
            
            // Update form field and submit
            if (filterType && filterValue) {
                const input = document.getElementById(filterType);
                if (input) {
                    input.value = filterValue;
                    document.getElementById('search-form').submit();
                }
            }
        });
    });
});
