// Gestión del Feed Header Hero
document.addEventListener('DOMContentLoaded', function() {
    const feedHeader = document.getElementById('feedHeader');
    const closeBtn = document.getElementById('closeFeedHeader');
    
    if (!feedHeader || !closeBtn) return;
    
    // Verificar si el usuario ya cerró el header
    const headerClosed = localStorage.getItem('feedHeaderClosed');
    
    if (headerClosed === 'true') {
        feedHeader.classList.add('hidden');
    }
    
    // Manejar el click en el botón de cerrar
    closeBtn.addEventListener('click', function() {
        feedHeader.style.opacity = '0';
        feedHeader.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            feedHeader.classList.add('hidden');
            localStorage.setItem('feedHeaderClosed', 'true');
        }, 300);
    });
});
