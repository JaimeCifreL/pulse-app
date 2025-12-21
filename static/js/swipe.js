// Swipe functionality for mobile
class SwipeHandler {
    constructor(element, callbacks, options = {}) {
        this.element = element;
        this.callbacks = callbacks;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.minSwipeDistance = 50;
        this.allowBackNavigation = options.allowBackNavigation || false;
        
        this.init();
    }
    
    init() {
        this.element.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
        this.element.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
        this.element.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: false });
    }
    
    handleTouchStart(e) {
        this.touchStartX = e.changedTouches[0].screenX;
        this.touchStartY = e.changedTouches[0].screenY;
    }
    
    handleTouchMove(e) {
        const touchX = e.changedTouches[0].screenX;
        const touchY = e.changedTouches[0].screenY;
        const diffX = touchX - this.touchStartX;
        const diffY = Math.abs(touchY - this.touchStartY);
        
        // If back navigation is NOT allowed, prevent swipe right from triggering browser back
        if (!this.allowBackNavigation) {
            // If swiping right (diffX > 0) and horizontal movement is significant
            if (diffX > 10 && Math.abs(diffX) > diffY) {
                e.preventDefault();
            }
        }
        
        // Always prevent left swipe from default behavior if it's horizontal
        if (diffX < -10 && Math.abs(diffX) > diffY) {
            e.preventDefault();
        }
    }
    
    handleTouchEnd(e) {
        this.touchEndX = e.changedTouches[0].screenX;
        this.touchEndY = e.changedTouches[0].screenY;
        this.handleSwipe();
    }
    
    handleSwipe() {
        const diffX = this.touchStartX - this.touchEndX;
        const diffY = Math.abs(this.touchStartY - this.touchEndY);
        
        // Only trigger swipe if horizontal movement is more than vertical
        if (Math.abs(diffX) > this.minSwipeDistance && Math.abs(diffX) > diffY) {
            if (diffX > 0) {
                // Swipe left (next)
                if (this.callbacks.onSwipeLeft) {
                    this.callbacks.onSwipeLeft();
                }
            } else {
                // Swipe right (prev)
                if (this.callbacks.onSwipeRight) {
                    this.callbacks.onSwipeRight();
                }
            }
        }
    }
}

// Tab navigation with swipe
class TabSwiper {
    constructor(containerSelector, tabsSelector, contentSelector) {
        this.container = document.querySelector(containerSelector);
        this.tabs = document.querySelectorAll(tabsSelector);
        this.contents = document.querySelectorAll(contentSelector);
        this.currentIndex = 0;
        
        if (this.container && this.tabs.length > 0) {
            this.init();
        }
    }
    
    init() {
        // Find initial active tab
        this.tabs.forEach((tab, index) => {
            if (tab.classList.contains('active')) {
                this.currentIndex = index;
            }
            tab.addEventListener('click', () => this.switchTab(index));
        });
        
        // Setup swipe
        new SwipeHandler(this.container, {
            onSwipeLeft: () => this.next(),
            onSwipeRight: () => this.prev()
        });
    }
    
    switchTab(index) {
        if (index < 0 || index >= this.tabs.length) return;
        
        this.currentIndex = index;
        
        // Update tabs
        this.tabs.forEach((tab, i) => {
            tab.classList.toggle('active', i === index);
        });
        
        // Update content if exists
        if (this.contents.length > 0) {
            this.contents.forEach((content, i) => {
                content.classList.toggle('active', i === index);
            });
        }
        
        // Trigger callback if exists
        if (this.onSwitch) {
            this.onSwitch(index);
        }
    }
    
    next() {
        const nextIndex = (this.currentIndex + 1) % this.tabs.length;
        this.switchTab(nextIndex);
    }
    
    prev() {
        const prevIndex = (this.currentIndex - 1 + this.tabs.length) % this.tabs.length;
        this.switchTab(prevIndex);
    }
}
