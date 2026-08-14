// ============================================
// IMRAN SIDDIQUE - PORTFOLIO SCRIPTS
//
// Deliberately small. Four behaviours were removed on 2026-08-14 because the
// site read as busy rather than considered:
//
//   1. Scroll-reveal on every card. It set opacity to 0 up front and waited for
//      an IntersectionObserver, so content was invisible until it animated in,
//      and invisible for good if the observer never fired.
//   2. A typing effect that cycled four job descriptions in the hero forever.
//   3. Counting-up stat numbers. It also mangled "4,877", since parseInt stops
//      at the comma and it counted to 4.
//   4. Mouse-follow 3D tilt on cards.
//
// What is left is navigation, the theme toggle and a copy button.
// ============================================

document.addEventListener('DOMContentLoaded', function () {

    // ============================================
    // THEME TOGGLE
    // Light is the default. A visitor who has chosen dark keeps it.
    // ============================================
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            themeToggle.setAttribute('aria-pressed', String(next === 'dark'));
        });
        themeToggle.setAttribute('aria-pressed', String(savedTheme === 'dark'));
    }

    // ============================================
    // MOBILE NAVIGATION
    // ============================================
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        const setOpen = function (open) {
            navLinks.classList.toggle('active', open);
            hamburger.classList.toggle('active', open);
            hamburger.setAttribute('aria-expanded', String(open));
            const spans = hamburger.querySelectorAll('span');
            if (spans.length === 3) {
                spans[0].style.transform = open ? 'rotate(45deg) translate(5px, 5px)' : 'none';
                spans[1].style.opacity = open ? '0' : '1';
                spans[2].style.transform = open ? 'rotate(-45deg) translate(5px, -5px)' : 'none';
            }
        };

        hamburger.addEventListener('click', function (e) {
            e.stopPropagation();
            setOpen(!navLinks.classList.contains('active'));
        });

        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () { setOpen(false); });
        });

        document.addEventListener('click', function (event) {
            if (!hamburger.contains(event.target) && !navLinks.contains(event.target)) {
                setOpen(false);
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') setOpen(false);
        });
    }

    // ============================================
    // NAVBAR SHADOW ON SCROLL
    // A one-pixel shadow so the bar separates from the content under it.
    // ============================================
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const syncNavbar = function () {
            navbar.classList.toggle('scrolled', window.pageYOffset > 8);
        };
        syncNavbar();
        window.addEventListener('scroll', syncNavbar, { passive: true });
    }

    // ============================================
    // IN-PAGE ANCHORS
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ block: 'start' });
        });
    });

    // ============================================
    // COPY BUTTON ON CODE BLOCKS
    // ============================================
    document.querySelectorAll('pre code').forEach(function (block) {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.type = 'button';
        button.textContent = 'Copy';

        button.addEventListener('click', function () {
            navigator.clipboard.writeText(block.textContent).then(function () {
                button.textContent = 'Copied';
                setTimeout(function () { button.textContent = 'Copy'; }, 2000);
            });
        });

        block.parentNode.style.position = 'relative';
        block.parentNode.appendChild(button);
    });
});
