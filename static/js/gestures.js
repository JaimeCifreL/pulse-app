/**
 * Advanced Gestures for Pulse
 * - Double tap to like
 * - Long press for quick actions
 */

class GestureHandler {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            doubleTapDelay: options.doubleTapDelay || 300,
            longPressDelay: options.longPressDelay || 500,
            onDoubleTap: options.onDoubleTap || null,
            onLongPress: options.onLongPress || null,
            onSingleTap: options.onSingleTap || null,
        };

        this.lastTap = 0;
        this.tapCount = 0;
        this.longPressTimer = null;
        this.isLongPress = false;

        this.init();
    }

    init() {
        // Touch events
        this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
        this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });

        // Mouse events for desktop
        this.element.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.element.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.element.addEventListener('mousemove', this.handleMouseMove.bind(this));
    }

    handleTouchStart(e) {
        this.isLongPress = false;
        this.startLongPressTimer();
    }

    handleTouchMove(e) {
        // Cancel long press if user moves finger
        this.cancelLongPress();
    }

    handleTouchEnd(e) {
        this.cancelLongPress();

        if (this.isLongPress) {
            return;
        }

        const now = Date.now();
        const timeSinceLastTap = now - this.lastTap;

        if (timeSinceLastTap < this.options.doubleTapDelay && timeSinceLastTap > 0) {
            // Double tap detected
            this.tapCount = 0;
            this.lastTap = 0;
            if (this.options.onDoubleTap) {
                e.preventDefault();
                this.options.onDoubleTap(e);
                this.showHeartAnimation(e);
            }
        } else {
            // Single tap
            this.tapCount = 1;
            this.lastTap = now;
            
            setTimeout(() => {
                if (this.tapCount === 1 && this.options.onSingleTap) {
                    this.options.onSingleTap(e);
                }
                this.tapCount = 0;
            }, this.options.doubleTapDelay);
        }
    }

    handleMouseDown(e) {
        this.isLongPress = false;
        this.startLongPressTimer();
    }

    handleMouseMove(e) {
        this.cancelLongPress();
    }

    handleMouseUp(e) {
        this.cancelLongPress();
    }

    startLongPressTimer() {
        this.longPressTimer = setTimeout(() => {
            this.isLongPress = true;
            if (this.options.onLongPress) {
                this.options.onLongPress();
            }
        }, this.options.longPressDelay);
    }

    cancelLongPress() {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }
    }

    showHeartAnimation(e) {
        const heart = document.createElement('div');
        heart.className = 'double-tap-heart';
        heart.innerHTML = '❤️';
        
        // Position at tap location
        const rect = this.element.getBoundingClientRect();
        const x = e.touches ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
        const y = e.touches ? e.touches[0].clientY - rect.top : e.clientY - rect.top;
        
        heart.style.left = `${x}px`;
        heart.style.top = `${y}px`;
        
        this.element.appendChild(heart);
        
        // Remove after animation
        setTimeout(() => {
            heart.remove();
        }, 1000);
    }
}

// Initialize gestures on post cards
document.addEventListener('DOMContentLoaded', function() {
    const postCards = document.querySelectorAll('.post-card');
    
    postCards.forEach(card => {
        const postId = card.dataset.postId;
        const mediaContainer = card.querySelector('.media-container, .media-container-large, .grid-text-preview');
        
        if (mediaContainer) {
            new GestureHandler(mediaContainer, {
                onDoubleTap: (e) => {
                    // Double tap to like
                    likePost(postId);
                },
                onLongPress: () => {
                    // Long press to show quick actions
                    showQuickActions(postId, card);
                }
            });
        }
    });
});

// Quick actions menu
function showQuickActions(postId, card) {
    // Remove existing quick actions
    const existingMenu = document.querySelector('.quick-actions-menu');
    if (existingMenu) {
        existingMenu.remove();
    }

    const menu = document.createElement('div');
    menu.className = 'quick-actions-menu';
    menu.innerHTML = `
        <button onclick="likePost('${postId}'); this.parentElement.remove();">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
            Like
        </button>
        <button onclick="window.location.href='/post/${postId}/'; this.parentElement.remove();">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            Comentar
        </button>
        <button onclick="repostPost('${postId}'); this.parentElement.remove();">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="17 1 21 5 17 9"></polyline>
                <path d="M3 11v-4a4 4 0 0 1 4-4h14"></path>
                <polyline points="7 23 3 19 7 15"></polyline>
                <path d="M21 13v4a4 4 0 0 1-4 4H3"></path>
            </svg>
            Repost
        </button>
        <button onclick="copyPostLink('${postId}'); this.parentElement.remove();">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
            Copiar link
        </button>
        <button onclick="this.parentElement.remove();" class="cancel-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Cancelar
        </button>
    `;

    card.appendChild(menu);

    // Close menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closeMenu(e) {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }, 100);

    // Add vibration feedback if supported
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

function copyPostLink(postId) {
    const url = `${window.location.origin}/post/${postId}/`;
    navigator.clipboard.writeText(url).then(() => {
        showToast('Link copiado al portapapeles');
    }).catch(err => {
        console.error('Error copying link:', err);
    });
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
