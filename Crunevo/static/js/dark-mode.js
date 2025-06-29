// CRUNEVO Dark Mode Implementation

(function() {
    'use strict';

    // Theme constants
    const THEME_KEY = 'crunevo-theme';
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark',
        SYSTEM: 'system'
    };

    // Theme state
    let currentTheme = THEMES.SYSTEM;
    let systemPreference = getSystemPreference();

    // Initialize dark mode on DOM load
    document.addEventListener('DOMContentLoaded', function() {
        initializeDarkMode();
    });

    function initializeDarkMode() {
        // Load saved theme preference
        loadThemePreference();
        
        // Apply initial theme
        applyTheme(currentTheme);
        
        // Set up theme toggle buttons
        setupThemeToggles();
        
        // Listen for system theme changes
        listenForSystemChanges();
        
        // Update theme toggle states
        updateToggleStates();
    }

    function loadThemePreference() {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme && Object.values(THEMES).includes(savedTheme)) {
            currentTheme = savedTheme;
        } else {
            currentTheme = THEMES.SYSTEM;
        }
    }

    function saveThemePreference(theme) {
        localStorage.setItem(THEME_KEY, theme);
        currentTheme = theme;
    }

    function getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? THEMES.DARK : THEMES.LIGHT;
    }

    function getEffectiveTheme() {
        if (currentTheme === THEMES.SYSTEM) {
            return systemPreference;
        }
        return currentTheme;
    }

    function applyTheme(theme) {
        const effectiveTheme = theme === THEMES.SYSTEM ? systemPreference : theme;
        const isDark = effectiveTheme === THEMES.DARK;
        
        // Toggle dark class on document element
        document.documentElement.classList.toggle('dark', isDark);
        
        // Update data attribute for CSS targeting
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update meta theme-color for mobile browsers
        updateMetaThemeColor(isDark);
        
        // Dispatch theme change event
        dispatchThemeChangeEvent(effectiveTheme);
        
        // Update favicon if needed
        updateFavicon(isDark);
        
        // Animate theme transition
        animateThemeTransition();
    }

    function updateMetaThemeColor(isDark) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.setAttribute('name', 'theme-color');
            document.head.appendChild(metaThemeColor);
        }
        
        metaThemeColor.setAttribute('content', isDark ? '#1A1A1A' : '#7E57C2');
    }

    function updateFavicon(isDark) {
        // Update favicon based on theme if you have different versions
        const favicon = document.querySelector('link[rel="icon"]');
        if (favicon) {
            const faviconPath = isDark ? '/static/favicon-dark.ico' : '/static/favicon-light.ico';
            // Only update if different favicon files exist
            // favicon.href = faviconPath;
        }
    }

    function animateThemeTransition() {
        // Add transition class to body for smooth theme switching
        document.body.classList.add('theme-transition');
        
        setTimeout(function() {
            document.body.classList.remove('theme-transition');
        }, 300);
    }

    function dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme: theme }
        });
        window.dispatchEvent(event);
    }

    function setupThemeToggles() {
        // Simple toggle button
        const toggleButtons = document.querySelectorAll('#theme-toggle, [data-theme-toggle]');
        
        toggleButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                toggleTheme();
            });
        });

        // Theme selector dropdown (if exists)
        const themeSelector = document.querySelector('[data-theme-selector]');
        if (themeSelector) {
            themeSelector.addEventListener('change', function() {
                setTheme(this.value);
            });
        }

        // Individual theme buttons
        const lightButton = document.querySelector('[data-theme="light"]');
        const darkButton = document.querySelector('[data-theme="dark"]');
        const systemButton = document.querySelector('[data-theme="system"]');

        if (lightButton) {
            lightButton.addEventListener('click', function() {
                setTheme(THEMES.LIGHT);
            });
        }

        if (darkButton) {
            darkButton.addEventListener('click', function() {
                setTheme(THEMES.DARK);
            });
        }

        if (systemButton) {
            systemButton.addEventListener('click', function() {
                setTheme(THEMES.SYSTEM);
            });
        }
    }

    function toggleTheme() {
        const effectiveTheme = getEffectiveTheme();
        const newTheme = effectiveTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
        setTheme(newTheme);
    }

    function setTheme(theme) {
        if (!Object.values(THEMES).includes(theme)) {
            console.warn('Invalid theme:', theme);
            return;
        }

        saveThemePreference(theme);
        applyTheme(theme);
        updateToggleStates();
        
        // Show toast notification
        if (window.CRUNEVO && window.CRUNEVO.showToast) {
            const messages = {
                [THEMES.LIGHT]: 'Tema claro activado',
                [THEMES.DARK]: 'Tema oscuro activado',
                [THEMES.SYSTEM]: 'Siguiendo preferencia del sistema'
            };
            window.CRUNEVO.showToast(messages[theme], 'info', 2000);
        }
    }

    function updateToggleStates() {
        const effectiveTheme = getEffectiveTheme();
        
        // Update toggle button icons
        const toggleButtons = document.querySelectorAll('#theme-toggle, [data-theme-toggle]');
        toggleButtons.forEach(function(button) {
            const sunIcon = button.querySelector('[data-feather="sun"]');
            const moonIcon = button.querySelector('[data-feather="moon"]');
            
            if (sunIcon && moonIcon) {
                sunIcon.style.display = effectiveTheme === THEMES.DARK ? 'block' : 'none';
                moonIcon.style.display = effectiveTheme === THEMES.DARK ? 'none' : 'block';
            }
        });

        // Update theme selector
        const themeSelector = document.querySelector('[data-theme-selector]');
        if (themeSelector) {
            themeSelector.value = currentTheme;
        }

        // Update individual theme buttons
        const themeButtons = document.querySelectorAll('[data-theme]');
        themeButtons.forEach(function(button) {
            const buttonTheme = button.getAttribute('data-theme');
            button.classList.toggle('active', buttonTheme === currentTheme);
        });
    }

    function listenForSystemChanges() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        mediaQuery.addEventListener('change', function(e) {
            systemPreference = e.matches ? THEMES.DARK : THEMES.LIGHT;
            
            // Only apply if current theme is system
            if (currentTheme === THEMES.SYSTEM) {
                applyTheme(THEMES.SYSTEM);
                updateToggleStates();
            }
        });
    }

    // Keyboard shortcuts for theme switching
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Shift + D for dark mode toggle
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleTheme();
        }
    });

    // Auto-apply theme based on time of day (optional feature)
    function setupAutoTheme() {
        const autoThemeEnabled = localStorage.getItem('crunevo-auto-theme') === 'true';
        
        if (autoThemeEnabled) {
            const hour = new Date().getHours();
            const isDarkTime = hour < 7 || hour >= 19; // Dark between 7 PM and 7 AM
            
            setTheme(isDarkTime ? THEMES.DARK : THEMES.LIGHT);
        }
    }

    // Theme transition CSS
    const themeTransitionCSS = `
        .theme-transition,
        .theme-transition *,
        .theme-transition *:before,
        .theme-transition *:after {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
            transition-delay: 0 !important;
        }
    `;

    // Inject transition CSS
    const styleSheet = document.createElement('style');
    styleSheet.textContent = themeTransitionCSS;
    document.head.appendChild(styleSheet);

    // Theme persistence across page loads
    function handlePageLoad() {
        // Apply theme immediately to prevent flash
        const savedTheme = localStorage.getItem(THEME_KEY) || THEMES.SYSTEM;
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const effectiveTheme = savedTheme === THEMES.SYSTEM ? (systemDark ? THEMES.DARK : THEMES.LIGHT) : savedTheme;
        
        document.documentElement.classList.toggle('dark', effectiveTheme === THEMES.DARK);
    }

    // Apply theme immediately (before DOMContentLoaded)
    handlePageLoad();

    // Export theme functions globally
    window.CRUNEVO = window.CRUNEVO || {};
    window.CRUNEVO.theme = {
        get current() {
            return currentTheme;
        },
        get effective() {
            return getEffectiveTheme();
        },
        set: setTheme,
        toggle: toggleTheme,
        THEMES: THEMES
    };

    // Listen for storage changes (multi-tab sync)
    window.addEventListener('storage', function(e) {
        if (e.key === THEME_KEY && e.newValue !== currentTheme) {
            currentTheme = e.newValue || THEMES.SYSTEM;
            applyTheme(currentTheme);
            updateToggleStates();
        }
    });

    // Theme analytics (optional)
    window.addEventListener('themechange', function(e) {
        // Track theme changes for analytics
        if (window.gtag) {
            gtag('event', 'theme_change', {
                'theme': e.detail.theme
            });
        }
    });

})();

// High contrast mode detection and handling
(function() {
    'use strict';
    
    function handleHighContrast() {
        const isHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
        document.documentElement.classList.toggle('high-contrast', isHighContrast);
    }
    
    // Check on load
    handleHighContrast();
    
    // Listen for changes
    window.matchMedia('(prefers-contrast: high)').addEventListener('change', handleHighContrast);
})();

// Reduced motion detection
(function() {
    'use strict';
    
    function handleReducedMotion() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        document.documentElement.classList.toggle('reduced-motion', prefersReducedMotion);
        
        if (prefersReducedMotion) {
            // Disable animations
            const style = document.createElement('style');
            style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Check on load
    handleReducedMotion();
    
    // Listen for changes
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', handleReducedMotion);
})();
