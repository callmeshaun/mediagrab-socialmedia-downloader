document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        // Check if user has a saved preference
        const savedTheme = localStorage.getItem('theme');
        
        // Apply the saved theme or default to light mode (already set in HTML)
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
        }
        
        themeToggleBtn.addEventListener('click', function() {
            // Get current theme
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            
            // Toggle theme
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Save preference to local storage
            localStorage.setItem('theme', newTheme);
            
            // Apply new theme
            document.documentElement.setAttribute('data-bs-theme', newTheme);
        });
    }
    
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
    
    // Download button handler
    const downloadLinkBtn = document.querySelector('.download-btn');
    if (downloadLinkBtn) {
        downloadLinkBtn.addEventListener('click', function(e) {
            // Visual feedback that download is starting
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Downloading...';
            
            // After a brief delay, restore the button text
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
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
        
        // Paste URL from clipboard feature
        const pasteFromClipboard = document.createElement('button');
        pasteFromClipboard.type = 'button';
        pasteFromClipboard.className = 'btn btn-secondary position-absolute end-0 top-0 mt-1 me-5';
        pasteFromClipboard.innerHTML = '<i class="fas fa-paste"></i>';
        pasteFromClipboard.title = 'Paste from clipboard';
        pasteFromClipboard.style.zIndex = '5';
        
        pasteFromClipboard.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                urlInput.value = text;
                // Trigger input event to validate
                urlInput.dispatchEvent(new Event('input'));
            } catch (err) {
                console.error('Failed to read clipboard: ', err);
            }
        });
        
        urlInput.parentElement.style.position = 'relative';
        urlInput.parentElement.appendChild(pasteFromClipboard);
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
