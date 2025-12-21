// Toast/Snackbar notifications system
class Toast {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }
    
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getIcon(type);
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    }
    
    getIcon(type) {
        const icons = {
            success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
            error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
            warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
            info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
        };
        return icons[type] || icons.info;
    }
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration) {
        return this.show(message, 'error', duration);
    }
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Global toast instance
window.toast = new Toast();

// Confirmation Dialog
function showConfirmDialog(options = {}) {
    const {
        title = '¿Estás seguro?',
        message = 'Esta acción no se puede deshacer',
        confirmText = 'Confirmar',
        cancelText = 'Cancelar',
        type = 'danger',
        onConfirm = () => {},
        onCancel = () => {}
    } = options;
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    
    // Create dialog
    const dialog = document.createElement('div');
    dialog.className = `confirm-dialog confirm-${type}`;
    dialog.innerHTML = `
        <div class="confirm-header">
            <h3>${title}</h3>
        </div>
        <div class="confirm-body">
            <p>${message}</p>
        </div>
        <div class="confirm-footer">
            <button class="btn btn-secondary confirm-cancel">${cancelText}</button>
            <button class="btn btn-${type} confirm-confirm">${confirmText}</button>
        </div>
    `;
    
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    
    // Animation
    setTimeout(() => {
        overlay.classList.add('show');
        dialog.classList.add('show');
    }, 10);
    
    // Event handlers
    const close = () => {
        overlay.classList.remove('show');
        dialog.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    };
    
    dialog.querySelector('.confirm-cancel').addEventListener('click', () => {
        close();
        onCancel();
    });
    
    dialog.querySelector('.confirm-confirm').addEventListener('click', () => {
        close();
        onConfirm();
    });
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            close();
            onCancel();
        }
    });
}

// Update deletePost function to use confirmation
function deletePost(postId) {
    showConfirmDialog({
        title: '¿Eliminar publicación?',
        message: 'Esta acción no se puede deshacer. El post se eliminará permanentemente.',
        confirmText: 'Eliminar',
        cancelText: 'Cancelar',
        type: 'danger',
        onConfirm: async () => {
            try {
                const response = await fetch(`/api/posts/${postId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                if (response.ok) {
                    const postCard = document.querySelector(`[data-post-id="${postId}"]`);
                    if (postCard) {
                        postCard.style.opacity = '0';
                        postCard.style.transform = 'scale(0.9)';
                        setTimeout(() => postCard.remove(), 300);
                    }
                    toast.success('Post eliminado correctamente');
                } else {
                    throw new Error('Error al eliminar');
                }
            } catch (error) {
                console.error('Error:', error);
                toast.error('Error al eliminar el post');
            }
        }
    });
}

// Helper function for cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
