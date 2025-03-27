document.addEventListener('DOMContentLoaded', function() {
    // Delete vehicle confirmation
    const deleteButtons = document.querySelectorAll('.delete-vehicle-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const vehicleId = this.dataset.vehicleId;
            const vehicleName = this.dataset.vehicleName;
            
            // Create and show confirmation modal
            const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
            document.getElementById('vehicleToDelete').textContent = vehicleName;
            
            // Set form action
            const deleteForm = document.getElementById('deleteVehicleForm');
            deleteForm.action = `/dealer/vehicle/delete/${vehicleId}`;
            
            modal.show();
        });
    });
    
    // Mark as sold toggle
    const soldToggle = document.querySelectorAll('.sold-toggle');
    
    soldToggle.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const vehicleId = this.dataset.vehicleId;
            const isSold = this.checked;
            
            // Update vehicle sold status via fetch API
            fetch(`/dealer/vehicle/update-sold/${vehicleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ is_sold: isSold })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    const card = this.closest('.vehicle-card');
                    if (isSold) {
                        card.classList.add('vehicle-sold');
                    } else {
                        card.classList.remove('vehicle-sold');
                    }
                    
                    // Show toast notification
                    const toast = new bootstrap.Toast(document.getElementById('statusToast'));
                    document.getElementById('toastMessage').textContent = 
                        isSold ? 'Vehicle marked as sold' : 'Vehicle marked as available';
                    toast.show();
                } else {
                    alert('Failed to update status. Please try again.');
                    // Revert toggle
                    this.checked = !isSold;
                }
            })
            .catch(error => {
                console.error('Error updating vehicle status:', error);
                alert('An error occurred. Please try again.');
                // Revert toggle
                this.checked = !isSold;
            });
        });
    });
    
    // Featured toggle
    const featuredToggle = document.querySelectorAll('.featured-toggle');
    
    featuredToggle.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const vehicleId = this.dataset.vehicleId;
            const isFeatured = this.checked;
            
            // Update vehicle featured status via fetch API
            fetch(`/dealer/vehicle/update-featured/${vehicleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ is_featured: isFeatured })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show toast notification
                    const toast = new bootstrap.Toast(document.getElementById('statusToast'));
                    document.getElementById('toastMessage').textContent = 
                        isFeatured ? 'Vehicle marked as featured' : 'Vehicle removed from featured';
                    toast.show();
                } else {
                    alert('Failed to update featured status. Please try again.');
                    // Revert toggle
                    this.checked = !isFeatured;
                }
            })
            .catch(error => {
                console.error('Error updating featured status:', error);
                alert('An error occurred. Please try again.');
                // Revert toggle
                this.checked = !isFeatured;
            });
        });
    });
    
    // Dashboard stats (simple chart)
    const statsCanvas = document.getElementById('vehicle-stats-chart');
    
    if (statsCanvas) {
        const ctx = statsCanvas.getContext('2d');
        
        // Get data from data attributes
        const activeListings = parseInt(statsCanvas.dataset.active) || 0;
        const soldVehicles = parseInt(statsCanvas.dataset.sold) || 0;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active Listings', 'Sold Vehicles'],
                datasets: [{
                    data: [activeListings, soldVehicles],
                    backgroundColor: [
                        '#3498DB',
                        '#E74C3C'
                    ],
                    borderColor: [
                        '#2980B9',
                        '#C0392B'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Inventory Status'
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    // Quick filters
    const filterButtons = document.querySelectorAll('.dashboard-filter-btn');
    const vehicleItems = document.querySelectorAll('.vehicle-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            
            vehicleItems.forEach(item => {
                if (filter === 'all') {
                    item.style.display = 'block';
                } else if (filter === 'active' && !item.classList.contains('vehicle-sold')) {
                    item.style.display = 'block';
                } else if (filter === 'sold' && item.classList.contains('vehicle-sold')) {
                    item.style.display = 'block';
                } else if (filter === 'featured' && item.classList.contains('vehicle-featured')) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});
