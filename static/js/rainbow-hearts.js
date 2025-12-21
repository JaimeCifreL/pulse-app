// Sistema de corazones arco iris para likes en tiempo real

const rainbowColors = [
    '#FF0000', // Rojo
    '#FF7F00', // Naranja
    '#FFFF00', // Amarillo
    '#00FF00', // Verde
    '#0000FF', // Azul
    '#4B0082', // Índigo
    '#9400D3'  // Violeta
];

// Obtener el color del arco iris basado en el número de likes
function getRainbowColor(likesCount) {
    const index = likesCount % rainbowColors.length;
    return rainbowColors[index];
}

// Actualizar el color de todos los corazones en la página
function updateHeartColors() {
    // En la página de índice y trending - botones de like
    const likeButtons = document.querySelectorAll('.action-btn button, a.action-btn');
    likeButtons.forEach(button => {
        const likesSpan = button.querySelector('span[data-likes-count]');
        
        if (likesSpan) {
            const likesCount = parseInt(likesSpan.getAttribute('data-likes-count')) || 0;
            const heartIcon = button.querySelector('svg');
            
            if (heartIcon) {
                heartIcon.style.color = getRainbowColor(likesCount);
                heartIcon.style.transition = 'color 0.3s ease';
            }
        }
    });

    // En la página de detalle del post
    const postStatsLikes = document.querySelector('.post-stats span:first-child');
    if (postStatsLikes) {
        const likesCountSpan = postStatsLikes.querySelector('span[data-likes-count]');
        if (likesCountSpan) {
            const likesCount = parseInt(likesCountSpan.getAttribute('data-likes-count')) || 0;
            const heartIcon = postStatsLikes.querySelector('svg');
            
            if (heartIcon) {
                heartIcon.style.color = getRainbowColor(likesCount);
                heartIcon.style.transition = 'color 0.3s ease';
            }
        }
    }

    // En la página de perfil (grid)
    const gridLikes = document.querySelectorAll('.grid-likes');
    gridLikes.forEach(element => {
        const likesCountSpan = element.querySelector('span[data-likes-count]');
        if (likesCountSpan) {
            const likesCount = parseInt(likesCountSpan.getAttribute('data-likes-count')) || 0;
            const heartIcon = element.querySelector('svg');
            
            if (heartIcon) {
                heartIcon.style.color = getRainbowColor(likesCount);
                heartIcon.style.transition = 'color 0.3s ease';
            }
        }
    });

    // En post-badge (trending)
    const postBadges = document.querySelectorAll('.post-badge span:first-child');
    postBadges.forEach(badge => {
        const likesCountSpan = badge.querySelector('span[data-likes-count]');
        if (likesCountSpan) {
            const likesCount = parseInt(likesCountSpan.getAttribute('data-likes-count')) || 0;
            const heartIcon = badge.querySelector('svg');
            
            if (heartIcon) {
                heartIcon.style.color = getRainbowColor(likesCount);
                heartIcon.style.transition = 'color 0.3s ease';
            }
        }
    });
}

// Polling para actualizar likes cada 2 segundos
function startLikesPolling() {
    // Obtener todos los post IDs en la página
    const postCards = document.querySelectorAll('[data-post-id]');
    
    if (postCards.length === 0) return;

    setInterval(() => {
        postCards.forEach(card => {
            const postId = card.getAttribute('data-post-id');
            
            if (!postId) return;

            fetch(`/api/posts/${postId}/likes/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.likes_count !== undefined) {
                    // Actualizar el contador de likes
                    const likesSpans = card.querySelectorAll('span[data-likes-count]');
                    likesSpans.forEach(span => {
                        const oldCount = parseInt(span.getAttribute('data-likes-count')) || 0;
                        
                        if (oldCount !== data.likes_count) {
                            span.setAttribute('data-likes-count', data.likes_count);
                            span.textContent = data.likes_count;
                            
                            // Actualizar color del corazón asociado
                            const heartIcon = span.closest('[class*="action-btn"], [class*="post-badge"], [class*="post-stats"], [class*="grid-likes"]')?.querySelector('svg');
                            if (heartIcon) {
                                heartIcon.style.color = getRainbowColor(data.likes_count);
                            }
                        }
                    });
                }
            })
            .catch(error => console.error('Error al actualizar likes:', error));
        });
    }, 2000); // Actualizar cada 2 segundos
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    updateHeartColors();
    startLikesPolling();
});
