document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const downloadForm = document.getElementById('download-form');
    const downloadBtn = document.getElementById('download-btn');
    
    if (downloadForm) {
        downloadForm.addEventListener('submit', function() {
            // Show loading state
            downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            downloadBtn.disabled = true;
        });
    }
    
    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // URL input validation enhancement
    const urlInput = document.getElementById('instagram_url');
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            const url = this.value.trim();
            const isValidUrl = /^https?:\/\/(www\.)?instagram\.com\/(p|reel|reels)\/[^/]+\/?.*$/.test(url);
            
            if (url && !isValidUrl) {
                this.classList.add('is-invalid');
                if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.classList.add('invalid-feedback');
                    feedback.textContent = 'Please enter a valid Instagram post or reel URL';
                    this.parentNode.insertBefore(feedback, this.nextSibling);
                }
            } else {
                this.classList.remove('is-invalid');
                const feedback = this.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.remove();
                }
            }
        });
    }
    
    // Add "Copy Link" button functionality if needed
    document.querySelectorAll('.copy-link-btn').forEach(button => {
        button.addEventListener('click', function() {
            const urlToCopy = this.getAttribute('data-url');
            navigator.clipboard.writeText(urlToCopy).then(() => {
                // Temporarily change button text to show success
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });
});
