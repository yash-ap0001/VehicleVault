document.addEventListener('DOMContentLoaded', function() {
    // Image preview for vehicle form
    const imageInput = document.getElementById('images');
    const previewContainer = document.getElementById('image-preview-container');
    const existingImages = document.querySelectorAll('.existing-image');
    
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function() {
            // Clear previous previews for new files
            const previousPreviews = document.querySelectorAll('.new-image-preview');
            previousPreviews.forEach(preview => preview.remove());
            
            // Preview each selected file
            Array.from(this.files).forEach(file => {
                if (!file.type.match('image.*')) {
                    return;
                }
                
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'image-preview new-image-preview';
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.alt = 'Image Preview';
                    
                    previewDiv.appendChild(img);
                    previewContainer.appendChild(previewDiv);
                };
                
                reader.readAsDataURL(file);
            });
        });
    }
    
    // Delete existing image functionality
    const deleteButtons = document.querySelectorAll('.delete-image-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const imageId = this.dataset.imageId;
            const imagePreview = this.closest('.existing-image');
            
            if (confirm('Are you sure you want to delete this image?')) {
                // Send delete request
                fetch(`/dealer/vehicle/delete-image/${imageId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove image preview from DOM
                        imagePreview.remove();
                    } else {
                        alert('Failed to delete image. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error deleting image:', error);
                    alert('An error occurred. Please try again.');
                });
            }
        });
    });
    
    // Set as primary image functionality
    const primaryButtons = document.querySelectorAll('.set-primary-btn');
    
    primaryButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const imageId = this.dataset.imageId;
            const vehicleId = this.dataset.vehicleId;
            
            // Send update request
            fetch(`/dealer/vehicle/set-primary-image/${vehicleId}/${imageId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    primaryButtons.forEach(btn => {
                        const indicator = btn.querySelector('.primary-indicator');
                        if (indicator) {
                            indicator.textContent = 'Set as primary';
                        }
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-outline-primary');
                    });
                    
                    const indicator = this.querySelector('.primary-indicator');
                    if (indicator) {
                        indicator.textContent = 'Primary Image';
                    }
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-primary');
                } else {
                    alert('Failed to set primary image. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error setting primary image:', error);
                alert('An error occurred. Please try again.');
            });
        });
    });
});
