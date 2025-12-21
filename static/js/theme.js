// Script para manejar cambio de tema día/oscuro en Pulse

// Detectar preferencia del sistema
function detectSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

// Obtener tema configurado (light, dark, o auto)
function getThemePreference() {
    const stored = localStorage.getItem('pulse-theme');
    return stored || 'auto';
}

// Obtener tema efectivo (resolviendo 'auto' a 'light' o 'dark')
function getCurrentTheme() {
    const preference = getThemePreference();
    if (preference === 'auto') {
        return detectSystemTheme();
    }
    return preference;
}

// Actualizar título del botón de tema
function updateThemeButton(effectiveTheme) {
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.title = effectiveTheme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
    }
}

// Aplicar tema al DOM
function applyThemeToDOM(theme) {
    const html = document.documentElement;
    
    // Remover ambas clases primero
    html.classList.remove('dark-mode', 'light-mode');
    
    // Aplicar la clase correspondiente
    if (theme === 'dark') {
        html.classList.add('dark-mode');
    } else if (theme === 'light') {
        html.classList.add('light-mode');
    }
    // Si no hay clase, usa auto (media query del sistema)
}

// Aplicar tema (guarda preferencia y actualiza DOM)
function applyTheme(themePreference) {
    localStorage.setItem('pulse-theme', themePreference);
    
    // Resolver el tema efectivo
    const effectiveTheme = themePreference === 'auto' ? detectSystemTheme() : themePreference;
    
    applyThemeToDOM(effectiveTheme);
    updateThemeButton(effectiveTheme);
    
    // Actualizar botones de configuración si existen
    updateThemeSettingsButtons(themePreference);
}

// Actualizar botones de la página de configuración
function updateThemeSettingsButtons(themePreference) {
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = document.getElementById(`theme-${themePreference}`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

// Cambiar tema manualmente (toggle del navbar)
function toggleTheme() {
    const currentEffective = getCurrentTheme();
    const newTheme = currentEffective === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    
    // Disparar evento personalizado
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    const preference = getThemePreference();
    const effectiveTheme = getCurrentTheme();
    
    applyThemeToDOM(effectiveTheme);
    updateThemeButton(effectiveTheme);
    updateThemeSettingsButtons(preference);
    
    // Añadir listener al botón de tema del navbar
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleTheme);
    }
    
    // Añadir listeners a los botones de configuración si existen
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.addEventListener('click', function() {
            const theme = this.getAttribute('data-theme');
            applyTheme(theme);
        });
    });
    
    // Escuchar cambios de preferencia del sistema (solo si está en modo auto)
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            const preference = getThemePreference();
            if (preference === 'auto') {
                applyThemeToDOM(e.matches ? 'dark' : 'light');
                updateThemeButton(e.matches ? 'dark' : 'light');
            }
        });
    }
});

// Exportar funciones para uso global
window.toggleTheme = toggleTheme;
window.getCurrentTheme = getCurrentTheme;
window.applyTheme = applyTheme;
window.getThemePreference = getThemePreference;
