// Pull to Refresh functionality for mobile
class PullToRefresh {
    constructor(options = {}) {
        this.container = options.container || document.querySelector('.feed-container');
        this.threshold = options.threshold || 80;
        this.onRefresh = options.onRefresh || (() => window.location.reload());
        
        this.startY = 0;
        this.currentY = 0;
        this.isDragging = false;
        this.isRefreshing = false;
        
        this.init();
    }
    
    init() {
        if (!this.container) return;
        
        // Create pull indicator
        this.indicator = document.createElement('div');
        this.indicator.className = 'pull-to-refresh-indicator';
        this.indicator.innerHTML = `
            <div class="pull-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
            </div>
            <span class="pull-text">Desliza para actualizar</span>
        `;
        
        this.container.insertBefore(this.indicator, this.container.firstChild);
        
        // Event listeners
        this.container.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        this.container.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        this.container.addEventListener('touchend', this.handleTouchEnd.bind(this));
    }
    
    handleTouchStart(e) {
        if (this.isRefreshing) return;
        
        // Solo activar si estamos en el top de la página
        if (window.scrollY > 0) return;
        
        this.startY = e.touches[0].clientY;
        this.isDragging = true;
    }
    
    handleTouchMove(e) {
        if (!this.isDragging || this.isRefreshing) return;
        
        this.currentY = e.touches[0].clientY;
        const pullDistance = this.currentY - this.startY;
        
        // Solo permitir pull down
        if (pullDistance > 0) {
            // Prevenir scroll nativo solo cuando estamos tirando
            if (window.scrollY === 0) {
                e.preventDefault();
            }
            
            // Aplicar resistencia
            const resistance = 2.5;
            const adjustedDistance = pullDistance / resistance;
            
            // Actualizar UI
            this.indicator.style.transform = `translateY(${Math.min(adjustedDistance, this.threshold)}px)`;
            this.indicator.style.opacity = Math.min(adjustedDistance / this.threshold, 1);
            
            // Cambiar texto cuando se alcanza el threshold
            const pullText = this.indicator.querySelector('.pull-text');
            if (adjustedDistance >= this.threshold) {
                pullText.textContent = 'Suelta para actualizar';
                this.indicator.classList.add('ready');
            } else {
                pullText.textContent = 'Desliza para actualizar';
                this.indicator.classList.remove('ready');
            }
        }
    }
    
    handleTouchEnd() {
        if (!this.isDragging || this.isRefreshing) return;
        
        const pullDistance = (this.currentY - this.startY) / 2.5;
        
        if (pullDistance >= this.threshold) {
            this.refresh();
        } else {
            this.reset();
        }
        
        this.isDragging = false;
    }
    
    async refresh() {
        this.isRefreshing = true;
        this.indicator.classList.add('refreshing');
        this.indicator.querySelector('.pull-text').textContent = 'Actualizando...';
        
        try {
            await this.onRefresh();
        } catch (error) {
            console.error('Error al actualizar:', error);
        }
        
        setTimeout(() => {
            this.reset();
            this.isRefreshing = false;
        }, 500);
    }
    
    reset() {
        this.indicator.style.transform = 'translateY(0)';
        this.indicator.style.opacity = '0';
        this.indicator.classList.remove('ready', 'refreshing');
        this.indicator.querySelector('.pull-text').textContent = 'Desliza para actualizar';
    }
}

// Inicializar en el feed
if (window.innerWidth <= 768 && document.querySelector('.feed-container')) {
    new PullToRefresh({
        container: document.querySelector('.feed-container'),
        onRefresh: async () => {
            // Recargar la página actual manteniendo el feed type
            const urlParams = new URLSearchParams(window.location.search);
            const feedType = urlParams.get('feed') || 'for_you';
            window.location.href = `?feed=${feedType}`;
        }
    });
}
