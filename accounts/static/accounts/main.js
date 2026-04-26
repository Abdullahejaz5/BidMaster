const BidMaster = {
    init: function() {
        this.setupSmoothScrolling();
        this.setupFormValidation();
        this.setupAnimations();
        this.setupCountdowns();
    },

    setupSmoothScrolling: function() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },

    setupFormValidation: function() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('blur', function() {
                this.classList.add('was-validated');
            });
        });
    },

    setupAnimations: function() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.auction-card, .stats-card, .feature-card').forEach(el => {
            observer.observe(el);
        });
    },
    setupCountdowns: function() {
        const countdownElements = document.querySelectorAll('[data-countdown]');
        countdownElements.forEach(element => {
            const endTime = new Date(element.dataset.countdown).getTime();
            this.startCountdown(element, endTime);
        });
    },

    startCountdown: function(element, endTime) {
        const timer = setInterval(() => {
            const now = new Date().getTime();
            const distance = endTime - now;

            if (distance < 0) {
                clearInterval(timer);
                element.innerHTML = "Auction Ended";
                element.classList.add('text-muted');
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            let timeString = '';
            if (days > 0) timeString += `${days}d `;
            timeString += `${hours}h ${minutes}m`;
            
            element.innerHTML = `<i class="bi bi-clock"></i> Ends in ${timeString}`;
        }, 1000);
    },

    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },

    placeBid: function(auctionId, amount) {
        console.log(`Placing bid of ${this.formatCurrency(amount)} on auction ${auctionId}`);
        
        setTimeout(() => {
            this.showToast('Bid placed successfully!', 'success');
        }, 1000);
    },

    setupSearch: function() {
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        
        if (searchInput && searchButton) {
            searchButton.addEventListener('click', () => {
                this.performSearch(searchInput.value);
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(searchInput.value);
                }
            });
        }
    },

    performSearch: function(query) {
        if (!query.trim()) {
            this.showToast('Please enter a search term', 'warning');
            return;
        }
        
        console.log(`Searching for: ${query}`);
        this.showToast(`Searching for "${query}"...`, 'info');
    },

    loadMoreAuctions: function(page = 1) {
        console.log(`Loading page ${page} of auctions`);
        this.showToast('Loading more auctions...', 'info');
    },

    toggleFavorite: function(auctionId, element) {
        const isFavorited = element.classList.contains('favorited');
        
        if (isFavorited) {
            element.classList.remove('favorited');
            element.innerHTML = '<i class="bi bi-heart"></i>';
            this.showToast('Removed from favorites', 'info');
        } else {
            element.classList.add('favorited');
            element.innerHTML = '<i class="bi bi-heart-fill"></i>';
            this.showToast('Added to favorites', 'success');
        }
    }
};

document.addEventListener('DOMContentLoaded', function() {
    BidMaster.init();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = BidMaster;
}
