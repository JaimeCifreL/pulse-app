// Infinite Scroll functionality
class InfiniteScroll {
    constructor(options = {}) {
        this.container = options.container || document.querySelector('.posts-list');
        this.threshold = options.threshold || 300; // pixels from bottom
        this.onLoadMore = options.onLoadMore;
        this.loading = false;
        this.hasMore = true;
        this.currentPage = options.initialPage || 1;
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        // Create loading indicator
        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'infinite-scroll-loading';
        this.loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <span>Cargando más posts...</span>
        `;
        this.loadingIndicator.style.display = 'none';
        
        // Insert after posts list
        this.container.parentElement.insertBefore(
            this.loadingIndicator,
            this.container.nextSibling
        );
        
        // Scroll event listener
        window.addEventListener('scroll', this.handleScroll.bind(this));
    }
    
    handleScroll() {
        if (this.loading || !this.hasMore) return;
        
        const scrollPosition = window.innerHeight + window.scrollY;
        const documentHeight = document.documentElement.scrollHeight;
        
        if (scrollPosition >= documentHeight - this.threshold) {
            this.loadMore();
        }
    }
    
    async loadMore() {
        if (this.loading || !this.hasMore) return;
        
        this.loading = true;
        this.loadingIndicator.style.display = 'flex';
        
        try {
            this.currentPage++;
            const urlParams = new URLSearchParams(window.location.search);
            const feedType = urlParams.get('feed') || 'for_you';
            
            const response = await fetch(`?feed=${feedType}&page=${this.currentPage}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error('Error al cargar posts');
            }
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newPosts = doc.querySelectorAll('.post-card');
            
            if (newPosts.length === 0) {
                this.hasMore = false;
                this.loadingIndicator.innerHTML = '<span>No hay más posts</span>';
                setTimeout(() => {
                    this.loadingIndicator.style.display = 'none';
                }, 2000);
                return;
            }
            
            // Append new posts
            newPosts.forEach(post => {
                this.container.appendChild(post.cloneNode(true));
            });
            
            // Reinitialize timers for new posts
            if (typeof updatePostTimers === 'function') {
                updatePostTimers();
            }
            
            if (this.onLoadMore) {
                this.onLoadMore(newPosts.length);
            }
            
        } catch (error) {
            console.error('Error loading more posts:', error);
            this.loadingIndicator.innerHTML = '<span>Error al cargar posts</span>';
        } finally {
            this.loading = false;
            setTimeout(() => {
                if (this.hasMore) {
                    this.loadingIndicator.style.display = 'none';
                }
            }, 500);
        }
    }
    
    destroy() {
        window.removeEventListener('scroll', this.handleScroll.bind(this));
        if (this.loadingIndicator) {
            this.loadingIndicator.remove();
        }
    }
}

// Inicializar solo en móvil
if (window.innerWidth <= 768 && document.querySelector('.posts-list')) {
    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = parseInt(urlParams.get('page')) || 1;
    
    new InfiniteScroll({
        container: document.querySelector('.posts-list'),
        initialPage: currentPage,
        onLoadMore: (count) => {
            console.log(`Loaded ${count} more posts`);
        }
    });
    
    // Ocultar paginación nativa
    const pagination = document.querySelector('.pagination');
    if (pagination) {
        pagination.style.display = 'none';
    }
}
