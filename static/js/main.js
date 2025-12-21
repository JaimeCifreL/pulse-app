// Funciones JavaScript para Pulse

// Like post
function likePost(postId) {
    const csrftoken = getCookie('csrftoken');

    fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la petición');
        }
        return response.json();
    })
    .then(data => {
        if (window.toast) {
            toast.success(data.liked ? 'Te gusta este post' : 'Ya no te gusta', 2000);
        }
        // Actualizar UI sin recargar
        const likeBtn = document.querySelector(`[data-post-id="${postId}"] .action-btn`);
        if (likeBtn && data.likes_count !== undefined) {
            const span = likeBtn.querySelector('span[data-likes-count]');
            if (span) span.textContent = data.likes_count;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (window.toast) {
            toast.error('Error al dar like al post');
        }
    });
}

// Repost post
function repostPost(postId) {
    const csrftoken = getCookie('csrftoken');

    fetch(`/post/${postId}/repost/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la petición');
        }
        return response.json();
    })
    .then(data => {
        if (window.toast) {
            toast.success(data.reposted ? 'Post reposteado' : 'Repost eliminado', 2000);
        }
        setTimeout(() => location.reload(), 1000);
    })
    .catch(error => {
        console.error('Error:', error);
        if (window.toast) {
            toast.error('Error al repostear');
        }
    });
}

// Vote on poll
function votePoll(postId, optionId) {
    const csrftoken = getCookie('csrftoken');

    fetch(`/post/${postId}/poll/vote/${optionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la petición');
        }
        return response.json();
    })
    .then(data => {
        // Recargar para mostrar resultados actualizados
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al votar en la encuesta');
    });
}

// Obtener CSRF token
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

// Actualizar contador de caracteres
document.addEventListener('DOMContentLoaded', function() {
    const textArea = document.getElementById('text_content');
    if (textArea) {
        textArea.addEventListener('input', function() {
            const charCount = document.getElementById('char-count');
            if (charCount) {
                charCount.textContent = this.value.length + ' / 2000 caracteres';
            }
        });
    }

    // Refresco de tiempo de vida de posts
    updatePostTimers();
    setInterval(updatePostTimers, 1000);
});

// Actualizar temporizadores de posts usando tiempo del servidor
function updatePostTimers() {
    const elements = document.querySelectorAll('[data-time-remaining]');
    elements.forEach(el => {
        // Obtener el tiempo inicial del servidor desde el atributo data
        let secondsRemaining = parseInt(el.getAttribute('data-time-remaining'));
        
        // Obtener la marca de tiempo en que se cargó este elemento
        let loadedAt = parseInt(el.getAttribute('data-loaded-at'));
        let nowTime = Date.now();
        
        // Calcular cuántos segundos han pasado desde que se cargó el elemento
        let secondsElapsed = Math.floor((nowTime - loadedAt) / 1000);
        
        // Calcular los segundos restantes restando los segundos transcurridos
        secondsRemaining = secondsRemaining - secondsElapsed;
        
        if (secondsRemaining > 0) {
            const minutes = Math.floor(secondsRemaining / 60);
            const seconds = secondsRemaining % 60;
            
            if (minutes > 0) {
                el.textContent = `${minutes}m ${seconds}s`;
            } else {
                el.textContent = `${seconds}s`;
            }
        } else {
            el.textContent = `Expirado`;
            el.classList.add('expired');
        }
    });
}

// Añadir opción a encuesta
function addPollOption() {
    const pollOptions = document.getElementById('poll-options');
    const newOption = document.createElement('div');
    newOption.className = 'poll-option-input';
    newOption.innerHTML = '<input type="text" name="poll_options[]" class="form-input" placeholder="Opción ' + (pollOptions.children.length + 1) + '">';
    pollOptions.appendChild(newOption);
}

// Preview de archivo media
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('content_file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const preview = document.getElementById('preview');
            const file = e.target.files[0];

            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    preview.innerHTML = '';
                    if (file.type.startsWith('image/')) {
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        img.style.maxWidth = '100%';
                        img.style.borderRadius = '8px';
                        preview.appendChild(img);
                    } else if (file.type.startsWith('video/')) {
                        const video = document.createElement('video');
                        video.src = event.target.result;
                        video.controls = true;
                        video.style.maxWidth = '100%';
                        video.style.borderRadius = '8px';
                        preview.appendChild(video);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

// Cambio de tipo de post
document.addEventListener('DOMContentLoaded', function() {
    const typeBtns = document.querySelectorAll('.type-btn');
    typeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            typeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            document.querySelectorAll('.form-section').forEach(s => s.classList.remove('active'));

            const type = this.dataset.type;
            document.getElementById('post_type').value = type;

            if (type === 'text') {
                document.getElementById('text-section').classList.add('active');
            } else if (type === 'photo' || type === 'video') {
                document.getElementById('media-section').classList.add('active');
            } else if (type === 'poll') {
                document.getElementById('poll-section').classList.add('active');
            }
        });
    });
});

// Filtros de trending
document.addEventListener('DOMContentLoaded', function() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            filterTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            // Aquí iría la lógica para filtrar posts
        });
    });
});

// Toggle post menu
function togglePostMenu(postId) {
    const menu = document.getElementById('menu-' + postId);
    const allMenus = document.querySelectorAll('.post-menu-dropdown');
    
    // Cerrar todos los otros menús
    allMenus.forEach(m => {
        if (m.id !== 'menu-' + postId) {
            m.style.display = 'none';
        }
    });
    
    // Toggle el menú actual
    if (menu.style.display === 'none' || menu.style.display === '') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
}

// Cerrar menús al hacer clic fuera
document.addEventListener('click', function(event) {
    if (!event.target.closest('.post-menu-container')) {
        document.querySelectorAll('.post-menu-dropdown').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});

// Delete post
function deletePost(postId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este post?')) {
        return;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/post/${postId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al eliminar el post');
        }
        return response.json();
    })
    .then(data => {
        // Redirigir al feed principal después de eliminar
        window.location.href = '/';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al eliminar el post');
    });
}

// Toggle pin post
function togglePinPost(postId) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/post/${postId}/pin/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al fijar/desfijar el post');
        }
        return response.json();
    })
    .then(data => {
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al fijar/desfijar el post');
    });
}

// Toggle comments
function toggleComments(postId) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/post/${postId}/toggle-comments/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al cambiar configuración de comentarios');
        }
        return response.json();
    })
    .then(data => {
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al cambiar configuración de comentarios');
    });
}

console.log('Pulse loaded successfully');
