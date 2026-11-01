/**
 * DevOpsVaultX - Core Client-Side Logic & SEO Engine
 * Provides instant in-browser filtering, URL state synchronization, and zero-CLS interactions.
 */

let currentCategory = 'all';

// Initialize interactions on DOMContentLoaded
window.addEventListener('DOMContentLoaded', () => {
    initCards();
    checkUrlParams();
    setupTypingEffect();
    initMobileMenu();
});

// Setup mouse tracking glow effect on bento cards with single passive event delegation
function initCards() {
    const grid = document.getElementById('grid-container');
    if (!grid) return;

    grid.addEventListener('mousemove', e => {
        const card = e.target.closest('.bento-card');
        if (!card) return;
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
        card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
    }, { passive: true });
}

// Category selection with URL hash state for SEO deep-linking
function setCategory(category) {
    currentCategory = category;
    
    // Update ARIA tabs and active visual states
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        const isMatch = btn.getAttribute('data-category') === category || btn.id === `tab-${category}`;
        btn.classList.toggle('active', isMatch);
        btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
    });

    // Clean URL state without page refresh (supports back button and direct sharing)
    if (category === 'all') {
        if (window.location.hash) {
            history.replaceState(null, '', window.location.pathname + window.location.search);
        }
    } else {
        history.replaceState(null, '', '#' + encodeURIComponent(category));
    }

    filterHub();
}

// Filter cards instantly based on active category and user search input (Zero Forced Reflow)
function filterHub() {
    const searchInput = document.getElementById('engine-search');
    const noResults = document.getElementById('no-results');
    
    if (!searchInput) return;

    const query = searchInput.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.bento-card');
    let matchedCount = 0;

    cards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        const cardMeta = (card.getAttribute('data-search') || '').toLowerCase();

        const matchesCat = (currentCategory === 'all' || cardCat === currentCategory);
        const matchesSearch = query === '' || cardMeta.includes(query);

        if (matchesCat && matchesSearch) {
            card.classList.remove('hidden');
            matchedCount++;
        } else {
            card.classList.add('hidden');
        }
    });

    if (noResults) {
        noResults.classList.toggle('hidden', matchedCount !== 0);
    }
}

// Clear all active filters and reset view
function clearSearchFilters() {
    const searchInput = document.getElementById('engine-search');
    if (searchInput) searchInput.value = '';
    setCategory('all');
}

// Check deep-linking query parameters & hash on load (#pdf, ?category=text, ?search=merge)
function checkUrlParams() {
    const validCategories = ['all', 'pdf', 'text', 'img', 'utilities', 'devops'];
    const hash = window.location.hash.replace('#', '').toLowerCase();
    
    const searchParams = new URLSearchParams(window.location.search);
    const catParam = searchParams.get('category')?.toLowerCase();
    const queryParam = searchParams.get('search');

    if (hash && validCategories.includes(hash)) {
        setCategory(hash);
    } else if (catParam && validCategories.includes(catParam)) {
        setCategory(catParam);
    }

    if (queryParam) {
        const searchInput = document.getElementById('engine-search');
        if (searchInput) {
            searchInput.value = queryParam;
            filterHub();
        }
    }
}

// Pre-rendered banner subtitle - preserves 0.000 CLS and zero main-thread overhead
function setupTypingEffect() {
    // Text is pre-rendered statically in the HTML to guarantee 0.000 CLS.
}

// -----------------------------------------------------------------------------
// Seamless Mobile Navigation Toggle & Drawer Handler
// -----------------------------------------------------------------------------
function initMobileMenu() {
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const navActions = document.getElementById('mainNavActions');
    if (!toggleBtn || !navActions) return;

    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = navActions.classList.toggle('active');
        toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        toggleBtn.classList.toggle('active', isOpen);
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.className = isOpen ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
        }
    });

    // Close when clicking outside of nav actions
    document.addEventListener('click', (e) => {
        if (!toggleBtn.contains(e.target) && !navActions.contains(e.target) && navActions.classList.contains('active')) {
            navActions.classList.remove('active');
            toggleBtn.setAttribute('aria-expanded', 'false');
            toggleBtn.classList.remove('active');
            const icon = toggleBtn.querySelector('i');
            if (icon) icon.className = 'fa-solid fa-bars';
        }
    });

    // Close when clicking any nav link
    navActions.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (navActions.classList.contains('active')) {
                navActions.classList.remove('active');
                toggleBtn.setAttribute('aria-expanded', 'false');
                toggleBtn.classList.remove('active');
                const icon = toggleBtn.querySelector('i');
                if (icon) icon.className = 'fa-solid fa-bars';
            }
        });
    });
}
