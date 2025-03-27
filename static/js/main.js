document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }

    // Search form validation
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Basic validation
            const minPrice = document.getElementById('min_price');
            const maxPrice = document.getElementById('max_price');
            
            if (minPrice && maxPrice && minPrice.value && maxPrice.value) {
                if (parseFloat(minPrice.value) > parseFloat(maxPrice.value)) {
                    e.preventDefault();
                    alert('Minimum price cannot be greater than maximum price');
                }
            }
            
            const minYear = document.getElementById('min_year');
            const maxYear = document.getElementById('max_year');
            
            if (minYear && maxYear && minYear.value && maxYear.value) {
                if (parseInt(minYear.value) > parseInt(maxYear.value)) {
                    e.preventDefault();
                    alert('Minimum year cannot be greater than maximum year');
                }
            }
        });
    }

    // Vehicle card hover effects
    const vehicleCards = document.querySelectorAll('.vehicle-card');
    vehicleCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
        });
    });

    // Brand-model chained dropdown
    const brandSelect = document.getElementById('brand');
    const modelSelect = document.getElementById('model');
    
    if (brandSelect && modelSelect) {
        brandSelect.addEventListener('change', function() {
            const brand = this.value;
            if (brand) {
                // Clear current options
                modelSelect.innerHTML = '<option value="">Select Model</option>';
                
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
                modelSelect.innerHTML = '<option value="">Select Model</option>';
            }
        });
    }

    // Price range slider (if present)
    const priceRange = document.getElementById('price-range');
    const minPriceDisplay = document.getElementById('min-price-display');
    const maxPriceDisplay = document.getElementById('max-price-display');
    const minPriceInput = document.getElementById('min_price');
    const maxPriceInput = document.getElementById('max_price');
    
    if (priceRange && minPriceDisplay && maxPriceDisplay && minPriceInput && maxPriceInput) {
        noUiSlider.create(priceRange, {
            start: [0, 50000],
            connect: true,
            step: 1000,
            range: {
                'min': 0,
                'max': 100000
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

    // Format price helper function
    function formatPrice(price) {
        price = parseInt(price);
        if (price >= 1000000) {
            return '$' + (price / 1000000).toFixed(2) + ' Million';
        } else {
            return '$' + price.toLocaleString('en-US');
        }
    }

    // Back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }

    // Image gallery (if on vehicle detail page)
    const mainImage = document.getElementById('main-vehicle-image');
    const thumbnails = document.querySelectorAll('.vehicle-thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Update main image src
                mainImage.src = this.dataset.src;
                
                // Update active thumbnail
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Mobile filter toggle
    const filterToggleBtn = document.getElementById('filter-toggle');
    const filterContainer = document.getElementById('filter-container');
    
    if (filterToggleBtn && filterContainer) {
        filterToggleBtn.addEventListener('click', function() {
            filterContainer.classList.toggle('show');
        });
    }
});
