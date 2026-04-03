/**
 * BreatheEase - Interactive JavaScript
 * Adds light interactivity and user experience enhancements
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // ========== CHARACTER COUNTER FOR MOOD INPUT ==========
    const moodTextarea = document.getElementById('mood_text');
    const charCount = document.getElementById('charCount');
    
    if (moodTextarea && charCount) {
        // Update character count as user types
        moodTextarea.addEventListener('input', function() {
            const count = this.value.length;
            charCount.textContent = count;
            
            // Change color based on length
            if (count > 500) {
                charCount.style.color = '#A8E6CF'; // Green when good length
            } else if (count > 200) {
                charCount.style.color = '#4A4A4A'; // Normal
            } else {
                charCount.style.color = '#6B6B6B'; // Light gray
            }
        });
    }
    
    // ========== FORM VALIDATION ==========
    const moodForm = document.getElementById('moodForm');
    
    if (moodForm) {
        moodForm.addEventListener('submit', function(e) {
            const textarea = document.getElementById('mood_text');
            const value = textarea.value.trim();
            
            // Check if input is too short
            if (value.length < 10) {
                e.preventDefault();
                alert('Please write at least 10 characters to help us understand how you\'re feeling.');
                textarea.focus();
                return false;
            }
        });
    }
    
    // ========== SMOOTH SCROLL FOR NAVIGATION ==========
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only apply smooth scroll for same-page anchors
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    targetSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ========== BREATHING ANIMATION CONTROL ==========
    const breathingCircle = document.querySelector('.breathing-circle');
    
    if (breathingCircle) {
        // Optional: Pause animation on hover
        breathingCircle.addEventListener('mouseenter', function() {
            this.style.animationPlayState = 'paused';
        });
        
        breathingCircle.addEventListener('mouseleave', function() {
            this.style.animationPlayState = 'running';
        });
    }
    
    // ========== FADE-IN ANIMATION FOR CARDS ==========
    const cards = document.querySelectorAll('.feature-card, .recommendation-card, .faq-item');
    
    // Intersection Observer for fade-in effect
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                
                // Trigger animation
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    cards.forEach(card => {
        observer.observe(card);
    });
    
    // ========== AUDIO PLAYER FEEDBACK ==========
    const audioPlayers = document.querySelectorAll('audio');
    
    audioPlayers.forEach(audio => {
        audio.addEventListener('play', function() {
            console.log('Music started playing');
            // Could add visual feedback here
            const audioNote = this.parentElement.querySelector('.audio-note');
            if (audioNote) {
                audioNote.style.color = '#A8E6CF';
                audioNote.textContent = '🎧 Music is playing... Let it soothe you.';
            }
        });
        
        audio.addEventListener('pause', function() {
            const audioNote = this.parentElement.querySelector('.audio-note');
            if (audioNote) {
                audioNote.style.color = '#6B6B6B';
                audioNote.textContent = '🎧 Put on your headphones and let the music soothe you.';
            }
        });
        
        audio.addEventListener('ended', function() {
            const audioNote = this.parentElement.querySelector('.audio-note');
            if (audioNote) {
                audioNote.style.color = '#B8A8D8';
                audioNote.textContent = '✨ How do you feel now?';
            }
        });
    });
    
    // ========== TEXTAREA AUTO-RESIZE ==========
    if (moodTextarea) {
        moodTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
    
    // ==========励志 QUOTE ROTATION (Optional Enhancement) ==========
    const quotes = [
        "You are stronger than you know.",
        "This too shall pass.",
        "One day at a time.",
        "You are not alone.",
        "Be kind to yourself.",
        "Progress, not perfection.",
        "You deserve peace."
    ];
    
    // Could add a feature to cycle through quotes on click
    const quoteElement = document.querySelector('.inspirational-quote');
    if (quoteElement) {
        quoteElement.style.cursor = 'pointer';
        quoteElement.title = 'Click for another quote';
        
        let currentQuoteIndex = 0;
        quoteElement.addEventListener('click', function() {
            currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
            this.style.opacity = '0';
            
            setTimeout(() => {
                // Don't change the main quote, just add a tooltip effect
                const originalText = this.textContent;
                this.setAttribute('data-original', originalText);
                this.style.opacity = '1';
            }, 300);
        });
    }
    
    // ========== HELPFUL CONSOLE MESSAGE ==========
    console.log('%c🌸 BreatheEase', 'color: #B8A8D8; font-size: 20px; font-weight: bold;');
    console.log('%cRemember: You matter. Your feelings are valid.', 'color: #6B6B6B; font-size: 14px;');
    
    // ========== ACTIVITY COMPLETION TRACKING ==========
    const activityButtons = document.querySelectorAll('.secondary-button');
    
    activityButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add a celebration effect
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
    
    // ========== MOBILE MENU TOGGLE (if needed in future) ==========
    // Placeholder for mobile menu functionality
    const mobileMenuButton = document.querySelector('.mobile-menu-btn');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            const navLinks = document.querySelector('.nav-links');
            navLinks.classList.toggle('active');
        });
    }
    
    // ========== PREVENT FORM DOUBLE SUBMISSION ==========
    if (moodForm) {
        let isSubmitting = false;
        
        moodForm.addEventListener('submit', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                return false;
            }
            
            isSubmitting = true;
            const submitBtn = this.querySelector('.submit-btn');
            if (submitBtn) {
                submitBtn.textContent = 'Analyzing...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // ========== ADD GENTLE HOVER EFFECTS ==========
    const featureCards = document.querySelectorAll('.feature-card, .resource-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // ========== ACCESSIBILITY: KEYBOARD NAVIGATION ==========
    const focusableElements = document.querySelectorAll('a, button, textarea, input');
    
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #B8A8D8';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });
    
    // ========== LOCAL STORAGE FOR USER PREFERENCES (Optional) ==========
    // Note: Only use if user explicitly opts in
    const savePreference = (key, value) => {
        try {
            localStorage.setItem(`breatheease_${key}`, JSON.stringify(value));
        } catch (e) {
            console.log('Unable to save preference');
        }
    };
    
    const getPreference = (key) => {
        try {
            const value = localStorage.getItem(`breatheease_${key}`);
            return value ? JSON.parse(value) : null;
        } catch (e) {
            return null;
        }
    };
    
    // ========== PAGE LOAD ANIMATION ==========
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // ========== SCROLL TO TOP BUTTON ==========
    const createScrollTopButton = () => {
        const button = document.createElement('button');
        button.innerHTML = '↑';
        button.className = 'scroll-to-top';
        button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: #B8A8D8;
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        `;
        
        button.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        button.addEventListener('mouseenter', () => {
            button.style.backgroundColor = '#D4C5E2';
            button.style.transform = 'scale(1.1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.backgroundColor = '#B8A8D8';
            button.style.transform = 'scale(1)';
        });
        
        document.body.appendChild(button);
        
        // Show/hide based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                button.style.display = 'block';
            } else {
                button.style.display = 'none';
            }
        });
    };
    
    createScrollTopButton();
    
    // ========== MOTIVATIONAL NOTIFICATION ==========
    const showMotivationalMessage = () => {
        const messages = [
            "You're doing great by taking care of your mental health! 💙",
            "Remember to breathe deeply and be kind to yourself. 🌸",
            "Taking this time for yourself is important. ✨",
            "You're stronger than you think. Keep going! 💪"
        ];
        
        // Only show if user has been on page for a while
        setTimeout(() => {
            if (document.hasFocus()) {
                const randomMessage = messages[Math.floor(Math.random() * messages.length)];
                console.log(`%c${randomMessage}`, 'color: #B8A8D8; font-size: 14px; font-weight: bold;');
            }
        }, 30000); // After 30 seconds
    };
    
    showMotivationalMessage();
    
    // ========== EMERGENCY HOTLINE QUICK ACCESS ==========
    const addQuickAccessHotline = () => {
        if (window.location.pathname.includes('result')) {
            const hotlineDiv = document.createElement('div');
            hotlineDiv.style.cssText = `
                position: fixed;
                bottom: 90px;
                right: 30px;
                background-color: #FFD3B6;
                padding: 10px 15px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                font-size: 14px;
                z-index: 999;
                cursor: pointer;
                transition: transform 0.3s ease;
            `;
            hotlineDiv.innerHTML = '🆘 Crisis? Call 988';
            hotlineDiv.title = 'Click for crisis resources';
            
            hotlineDiv.addEventListener('click', () => {
                const crisisBox = document.querySelector('.crisis-box');
                if (crisisBox) {
                    crisisBox.scrollIntoView({ behavior: 'smooth' });
                    crisisBox.style.animation = 'pulse 0.5s ease';
                }
            });
            
            hotlineDiv.addEventListener('mouseenter', () => {
                hotlineDiv.style.transform = 'scale(1.05)';
            });
            
            hotlineDiv.addEventListener('mouseleave', () => {
                hotlineDiv.style.transform = 'scale(1)';
            });
            
            document.body.appendChild(hotlineDiv);
        }
    };
    
    addQuickAccessHotline();
});

// ========== UTILITY FUNCTIONS ==========

/**
 * Format time in MM:SS format for audio player
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

/**
 * Validate email format (if needed for future features)
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatTime,
        validateEmail,
        debounce
    };
}