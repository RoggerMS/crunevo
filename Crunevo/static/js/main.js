// CRUNEVO Main JavaScript

(function() {
    'use strict';

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    function initializeApp() {
        initializeFeatherIcons();
        initializeNotifications();
        initializeFileUploads();
        initializeFormValidation();
        initializeTooltips();
        initializeProgressBars();
        initializeSmoothScroll();
        initializeImageLazyLoading();
        initializeAvatars();
        initializeSearch();
    }

    // Initialize Feather Icons
    function initializeFeatherIcons() {
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    // Auto-dismiss notifications
    function initializeNotifications() {
        const notifications = document.querySelectorAll('.notification, [class*="bg-red-"], [class*="bg-green-"], [class*="bg-blue-"]');
        
        notifications.forEach(function(notification) {
            // Auto-dismiss after 5 seconds
            setTimeout(function() {
                dismissNotification(notification);
            }, 5000);
            
            // Add close button if not present
            if (!notification.querySelector('.close-btn')) {
                const closeBtn = document.createElement('button');
                closeBtn.className = 'close-btn float-right text-xl font-bold opacity-70 hover:opacity-100';
                closeBtn.innerHTML = '&times;';
                closeBtn.onclick = function() {
                    dismissNotification(notification);
                };
                notification.insertBefore(closeBtn, notification.firstChild);
            }
        });
    }

    function dismissNotification(notification) {
        if (notification && notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(function() {
                notification.remove();
            }, 300);
        }
    }

    // Enhanced file upload functionality
    function initializeFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(function(input) {
            const dropArea = input.closest('.file-upload-area') || input.parentNode;
            
            if (dropArea) {
                // Drag and drop events
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
                    dropArea.addEventListener(eventName, preventDefaults, false);
                });

                ['dragenter', 'dragover'].forEach(function(eventName) {
                    dropArea.addEventListener(eventName, function() {
                        dropArea.classList.add('drag-over');
                    }, false);
                });

                ['dragleave', 'drop'].forEach(function(eventName) {
                    dropArea.addEventListener(eventName, function() {
                        dropArea.classList.remove('drag-over');
                    }, false);
                });

                dropArea.addEventListener('drop', function(e) {
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        input.files = files;
                        handleFileSelect(input);
                    }
                }, false);
            }

            // File change event
            input.addEventListener('change', function() {
                handleFileSelect(input);
            });
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleFileSelect(input) {
        const file = input.files[0];
        if (!file) return;

        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            showToast('El archivo es demasiado grande. Máximo 10MB.', 'error');
            input.value = '';
            return;
        }

        // Show file preview
        const preview = document.getElementById('file-preview');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');

        if (preview && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            preview.classList.remove('hidden');
        }

        // Add loading state
        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.classList.add('loading');
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Form validation enhancements
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(function(form) {
            form.addEventListener('submit', function(e) {
                if (!validateForm(form)) {
                    e.preventDefault();
                    return false;
                }
                
                // Add loading state to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                }
            });

            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(function(input) {
                input.addEventListener('blur', function() {
                    validateField(input);
                });
                
                input.addEventListener('input', function() {
                    clearFieldError(input);
                });
            });
        });
    }

    function validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(function(input) {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Este campo es obligatorio.';
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Ingresa un email válido.';
            }
        }

        // Password validation
        if (field.type === 'password' && value) {
            if (value.length < 8) {
                isValid = false;
                errorMessage = 'La contraseña debe tener al menos 8 caracteres.';
            }
        }

        // Password confirmation
        if (field.name === 'password2' && value) {
            const password = document.querySelector('input[name="password"]');
            if (password && value !== password.value) {
                isValid = false;
                errorMessage = 'Las contraseñas no coinciden.';
            }
        }

        if (!isValid) {
            showFieldError(field, errorMessage);
        } else {
            clearFieldError(field);
        }

        return isValid;
    }

    function showFieldError(field, message) {
        clearFieldError(field);
        
        field.classList.add('border-red-500');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-600 text-sm mt-1';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }

    function clearFieldError(field) {
        field.classList.remove('border-red-500');
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    // Initialize tooltips
    function initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(function(element) {
            element.addEventListener('mouseenter', function() {
                showTooltip(element);
            });
            
            element.addEventListener('mouseleave', function() {
                hideTooltip();
            });
        });
    }

    function showTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        
        tooltip.className = 'tooltip fixed bg-gray-900 text-white text-sm px-2 py-1 rounded z-50 pointer-events-none';
        tooltip.textContent = tooltipText;
        tooltip.id = 'tooltip';
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    }

    function hideTooltip() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    // Animate progress bars
    function initializeProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        progressBars.forEach(function(bar) {
            const targetWidth = bar.style.width || bar.getAttribute('data-width') || '0%';
            bar.style.width = '0%';
            
            setTimeout(function() {
                bar.style.width = targetWidth;
            }, 100);
        });
    }

    // Smooth scrolling for anchor links
    function initializeSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(function(link) {
            link.addEventListener('click', function(e) {
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Lazy loading for images
    function initializeImageLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(function(img) {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for browsers without IntersectionObserver
            images.forEach(function(img) {
                img.src = img.dataset.src;
            });
        }
    }

    // Initialize avatar fallbacks
    function initializeAvatars() {
        const avatars = document.querySelectorAll('.avatar img');
        
        avatars.forEach(function(img) {
            img.addEventListener('error', function() {
                const avatar = img.parentNode;
                const initials = avatar.getAttribute('data-initials') || '?';
                
                img.style.display = 'none';
                avatar.textContent = initials;
                avatar.classList.add('bg-primary', 'text-white');
            });
        });
    }

    // Enhanced search functionality
    function initializeSearch() {
        const searchInput = document.querySelector('input[name="q"]');
        
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = searchInput.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(function() {
                        // Add search suggestions or live search here
                        console.log('Searching for:', query);
                    }, 300);
                }
            });
        }
    }

    // Toast notifications
    function showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        const typeClasses = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        toast.className = `fixed top-4 right-4 ${typeClasses[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fadeIn`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, duration);
    }

    // Utility functions
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = function() {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(function() {
                    inThrottle = false;
                }, limit);
            }
        };
    }

    // Copy to clipboard functionality
    function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copiado al portapapeles', 'success');
            });
        } else {
            // Fallback
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showToast('Copiado al portapapeles', 'success');
            } catch (err) {
                showToast('Error al copiar', 'error');
            }
            document.body.removeChild(textArea);
        }
    }

    // Format numbers with thousands separator
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // Format time ago
    function timeAgo(date) {
        const now = new Date();
        const diffTime = Math.abs(now - new Date(date));
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
        const diffMinutes = Math.floor(diffTime / (1000 * 60));

        if (diffDays > 7) {
            return new Date(date).toLocaleDateString();
        } else if (diffDays > 0) {
            return `hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
        } else if (diffHours > 0) {
            return `hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
        } else if (diffMinutes > 0) {
            return `hace ${diffMinutes} minuto${diffMinutes > 1 ? 's' : ''}`;
        } else {
            return 'hace un momento';
        }
    }

    // Expose utility functions globally
    window.CRUNEVO = {
        showToast: showToast,
        copyToClipboard: copyToClipboard,
        formatNumber: formatNumber,
        timeAgo: timeAgo,
        debounce: debounce,
        throttle: throttle
    };

})();

// Additional functionality for specific pages
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal, [id$="-modal"]');
            modals.forEach(function(modal) {
                if (!modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                }
            });
        }
    });

    // Infinite scroll (if needed)
    const infiniteScrollContainer = document.querySelector('[data-infinite-scroll]');
    if (infiniteScrollContainer) {
        let loading = false;
        
        window.addEventListener('scroll', function() {
            if (loading) return;
            
            const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
            
            if (scrollTop + clientHeight >= scrollHeight - 5) {
                loading = true;
                // Load more content here
                console.log('Loading more content...');
                
                setTimeout(function() {
                    loading = false;
                }, 1000);
            }
        });
    }
});
