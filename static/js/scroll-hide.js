// Sistema de ocultación progresiva de elementos al hacer scroll
class ScrollHideManager {
    constructor() {
        this.navbar = document.querySelector('.navbar');
        this.feedTabs = document.querySelector('.feed-tabs');
        this.trendingTabs = document.querySelector('.trending-tabs');
        
        this.lastScrollY = window.scrollY;
        this.scrollDirection = 'down';
        this.navbarHeight = this.navbar?.offsetHeight || 60;
        this.tabsHeight = (this.feedTabs || this.trendingTabs)?.offsetHeight || 50;
        
        // Estado de ocultación
        this.tabsHidden = false;
        this.navbarHidden = false;
        
        // Umbral de scroll para activar ocultación
        this.scrollThreshold = 5;
        
        this.init();
    }
    
    init() {
        if (!this.navbar) return;
        
        // Configurar estilos iniciales
        this.setupStyles();
        
        // Listener de scroll con throttle
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }
    
    setupStyles() {
        // Navbar con transición suave
        if (this.navbar) {
            this.navbar.style.transition = 'transform 0.15s linear';
            this.navbar.style.willChange = 'transform';
        }
        
        // Tabs con transición suave
        const tabs = this.feedTabs || this.trendingTabs;
        if (tabs) {
            tabs.style.transition = 'transform 0.15s linear';
            tabs.style.willChange = 'transform';
        }
    }
    
    handleScroll() {
        const currentScrollY = window.scrollY;
        const scrollDiff = currentScrollY - this.lastScrollY;
        
        // Determinar dirección
        if (Math.abs(scrollDiff) < this.scrollThreshold) {
            return; // Ignorar movimientos muy pequeños
        }
        
        const isScrollingDown = scrollDiff > 0;
        
        // Actualizar dirección
        this.scrollDirection = isScrollingDown ? 'down' : 'up';
        
        if (isScrollingDown) {
            this.handleScrollDown(currentScrollY);
        } else {
            this.handleScrollUp();
        }
        
        this.lastScrollY = currentScrollY;
    }
    
    handleScrollDown(scrollY) {
        const tabs = this.feedTabs || this.trendingTabs;
        
        // Primero ocultar tabs
        if (tabs && !this.tabsHidden) {
            const tabsScroll = Math.min(scrollY, this.tabsHeight);
            tabs.style.transform = `translateY(-${tabsScroll}px)`;
            
            if (scrollY >= this.tabsHeight) {
                this.tabsHidden = true;
            }
        }
        
        // Luego ocultar navbar (solo después de que tabs estén ocultas)
        if (this.tabsHidden && !this.navbarHidden) {
            const navbarScroll = Math.min(scrollY - this.tabsHeight, this.navbarHeight);
            this.navbar.style.transform = `translateY(-${navbarScroll}px)`;
            
            if (scrollY >= this.tabsHeight + this.navbarHeight) {
                this.navbarHidden = true;
            }
        }
    }
    
    handleScrollUp() {
        // Restaurar todo en orden inverso
        
        // Primero mostrar navbar
        if (this.navbarHidden || this.navbar.style.transform !== 'translateY(0px)') {
            this.navbar.style.transform = 'translateY(0)';
            this.navbarHidden = false;
        }
        
        // Luego mostrar tabs
        const tabs = this.feedTabs || this.trendingTabs;
        if (tabs && (this.tabsHidden || tabs.style.transform !== 'translateY(0px)')) {
            tabs.style.transform = 'translateY(0)';
            this.tabsHidden = false;
        }
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ScrollHideManager();
    });
} else {
    new ScrollHideManager();
}
