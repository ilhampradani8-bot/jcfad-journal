/**
 * PT CHAIN ASIA CONECT - Client-Side Authentication & Session Controller
 * Supports:
 * 1. Google OAuth 2.0 (Google Identity Services / One Tap / Button)
 *    Client ID: 812430784237-ipa8k92fujeoirmi47vefbrekgqv46op.apps.googleusercontent.com
 * 2. Instant Demo Investor Account for fast testing & evaluation
 * 3. Reactive UI synchronization across header, drawer, and dashboard
 */

(function () {
  const STORAGE_KEY = 'chain_user_session';
  const WALLET_KEY = 'chain_user_wallet';
  const GOOGLE_CLIENT_ID = '812430784237-ipa8k92fujeoirmi47vefbrekgqv46op.apps.googleusercontent.com';

  // Decode JWT payload
  function parseJwt(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      console.warn('[ChainAuth] Failed to decode JWT:', e);
      return null;
    }
  }

  // Get current session
  function getSession() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  }

  // Set session
  function setSession(userData) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
      // Initialize wallet if not yet set
      if (!localStorage.getItem(WALLET_KEY)) {
        localStorage.setItem(
          WALLET_KEY,
          JSON.stringify({
            cashBalance: 18250000,
            totalAssets: 125450000,
            totalYield: 14820000,
            activeProjectsCount: 3,
            history: [
              {
                id: 'TX-2026-091',
                date: '2026-10-28',
                type: 'DIVIDEN',
                desc: 'Bagi Hasil Sukuk Mudharabah Krui (Q3)',
                amount: 3950000,
                status: 'Berhasil'
              },
              {
                id: 'TX-2026-084',
                date: '2026-10-15',
                type: 'TOPUP',
                desc: 'Setoran Dana RDN via Bank Mandiri VA',
                amount: 10000000,
                status: 'Berhasil'
              },
              {
                id: 'TX-2026-072',
                date: '2026-09-30',
                type: 'INVESTASI',
                desc: 'Alokasi Proyek Distribusi Krui 3T',
                amount: -50000000,
                status: 'Selesai'
              }
            ]
          })
        );
      }
      updateUI();
      window.dispatchEvent(new CustomEvent('chain-auth-changed', { detail: userData }));
    } catch (e) {
      console.error('[ChainAuth] Error saving session:', e);
    }
  }

  // Clear session
  function clearSession() {
    localStorage.removeItem(STORAGE_KEY);
    updateUI();
    window.dispatchEvent(new CustomEvent('chain-auth-changed', { detail: null }));
  }

  // Get wallet state
  function getWallet() {
    try {
      const w = localStorage.getItem(WALLET_KEY);
      if (w) return JSON.parse(w);
      const defaultWallet = {
        cashBalance: 18250000,
        totalAssets: 125450000,
        totalYield: 14820000,
        activeProjectsCount: 3,
        history: []
      };
      localStorage.setItem(WALLET_KEY, JSON.stringify(defaultWallet));
      return defaultWallet;
    } catch (e) {
      return { cashBalance: 18250000, totalAssets: 125450000, totalYield: 14820000, activeProjectsCount: 3, history: [] };
    }
  }

  // Top up wallet
  function topupWallet(amount, bankName, vaNumber) {
    const wallet = getWallet();
    const cleanAmount = parseInt(amount, 10);
    if (isNaN(cleanAmount) || cleanAmount <= 0) return false;

    wallet.cashBalance += cleanAmount;
    wallet.totalAssets += cleanAmount;
    wallet.history.unshift({
      id: 'TX-' + Math.floor(100000 + Math.random() * 900000),
      date: new Date().toISOString().split('T')[0],
      type: 'TOPUP',
      desc: `Top Up RDN Escrow via ${bankName} (${vaNumber})`,
      amount: cleanAmount,
      status: 'Berhasil'
    });

    localStorage.setItem(WALLET_KEY, JSON.stringify(wallet));
    window.dispatchEvent(new CustomEvent('chain-wallet-updated', { detail: wallet }));
    return true;
  }

  // Update header UI elements
  function updateUI() {
    const session = getSession();

    // Desktop elements
    const loginBtn = document.getElementById('header-login-btn');
    const userBadge = document.getElementById('header-user-badge');
    const userImg = document.getElementById('header-user-img');
    const userLabel = document.getElementById('header-user-name');

    // Mobile elements
    const mobileLoginBtn = document.getElementById('mobile-login-btn');
    const mobileUserBox = document.getElementById('mobile-user-box');
    const mobileUserImg = document.getElementById('mobile-user-img');
    const mobileUserName = document.getElementById('mobile-user-name');

    if (session) {
      if (loginBtn) loginBtn.style.display = 'none';
      if (userBadge) {
        userBadge.style.display = 'inline-flex';
        if (userImg) userImg.src = session.avatar || '/images/CAC-LOGO.jpg';
        if (userLabel) userLabel.textContent = session.name.split(' ')[0] || 'Dashboard';
      }

      if (mobileLoginBtn) mobileLoginBtn.style.display = 'none';
      if (mobileUserBox) {
        mobileUserBox.style.display = 'flex';
        if (mobileUserImg) mobileUserImg.src = session.avatar || '/images/CAC-LOGO.jpg';
        if (mobileUserName) mobileUserName.textContent = session.name || 'Investor';
      }
    } else {
      if (loginBtn) loginBtn.style.display = 'inline-flex';
      if (userBadge) userBadge.style.display = 'none';

      if (mobileLoginBtn) mobileLoginBtn.style.display = 'flex';
      if (mobileUserBox) mobileUserBox.style.display = 'none';
    }
  }

  // Open modal
  function openLoginModal() {
    const modal = document.getElementById('chain-auth-modal');
    if (modal) {
      modal.classList.add('is-active');
      document.body.style.overflow = 'hidden';
      // Trigger Google button render if available
      renderGoogleButton();
    }
  }

  // Close modal
  function closeLoginModal() {
    const modal = document.getElementById('chain-auth-modal');
    if (modal) {
      modal.classList.remove('is-active');
      document.body.style.overflow = '';
    }
  }

  // Render Google Button using GIS
  function renderGoogleButton() {
    if (typeof window.google !== 'undefined' && window.google.accounts) {
      const container = document.getElementById('g_id_signin_slot');
      if (container && container.childNodes.length === 0) {
        try {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCredentialResponse,
            auto_select: false
          });

          window.google.accounts.id.renderButton(container, {
            theme: 'outline',
            size: 'large',
            type: 'standard',
            shape: 'pill',
            text: 'signin_with',
            logo_alignment: 'left',
            width: 280
          });
        } catch (err) {
          console.warn('[ChainAuth] GIS render failed:', err);
        }
      }
    }
  }

  // Handle Google OAuth Credential
  function handleGoogleCredentialResponse(response) {
    if (!response || !response.credential) return;
    const payload = parseJwt(response.credential);
    if (!payload) return;

    const userData = {
      id: payload.sub || 'G-' + Date.now(),
      name: payload.name || 'Investor Terverifikasi',
      email: payload.email || 'investor@chainasiaconnect.co.id',
      avatar: payload.picture || '/images/CAC-LOGO.jpg',
      authProvider: 'Google OAuth 2.0',
      role: 'Verified Investor (Level 2 KYC)',
      loggedInAt: Date.now()
    };

    setSession(userData);
    closeLoginModal();

    // Redirect to dashboard if currently on home or login prompt
    if (window.location.pathname === '/' || window.location.pathname.startsWith('/about')) {
      window.location.href = '/scf/dashboard';
    }
  }

  // Demo Login Handler
  function loginDemoAccount(type) {
    let userData;
    if (type === 'admin') {
      userData = {
        id: 'CAC-ADM-001',
        name: 'Ilham Pradani, S.H.',
        email: 'ilham@chainasiaconnect.co.id',
        avatar: '/images/CAC-LOGO.jpg',
        authProvider: 'Corporate Internal Auth',
        role: 'Director & Managing Partner',
        loggedInAt: Date.now()
      };
    } else {
      userData = {
        id: 'INV-2026-904',
        name: 'Investor Rekanan PT CHAIN',
        email: 'investor.scf@chainasiaconnect.co.id',
        avatar: '/images/CAC-LOGO.jpg',
        authProvider: 'Investor Portal SSO',
        role: 'Verified Investor (Level 2 KYC)',
        loggedInAt: Date.now()
      };
    }

    setSession(userData);
    closeLoginModal();
    if (window.location.pathname !== '/scf/dashboard') {
      window.location.href = '/scf/dashboard';
    }
  }

  // Initialize listeners
  document.addEventListener('DOMContentLoaded', () => {
    updateUI();

    // Login triggers
    const loginBtn = document.getElementById('header-login-btn');
    if (loginBtn) loginBtn.addEventListener('click', openLoginModal);

    const mobileLoginBtn = document.getElementById('mobile-login-btn');
    if (mobileLoginBtn) mobileLoginBtn.addEventListener('click', openLoginModal);

    // Logout triggers
    const logoutBtn = document.getElementById('header-quick-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (confirm('Keluar dari sesi portal investor?')) {
          clearSession();
          if (window.location.pathname.includes('/dashboard')) {
            window.location.href = '/';
          }
        }
      });
    }

    const mobileLogoutBtn = document.getElementById('mobile-quick-logout');
    if (mobileLogoutBtn) {
      mobileLogoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        clearSession();
        if (window.location.pathname.includes('/dashboard')) {
          window.location.href = '/';
        }
      });
    }

    // Modal close triggers
    const modalCloseBtn = document.getElementById('chain-modal-close');
    if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeLoginModal);

    const modalBackdrop = document.getElementById('chain-modal-backdrop');
    if (modalBackdrop) modalBackdrop.addEventListener('click', closeLoginModal);

    // Demo login buttons
    const demoBtn = document.getElementById('btn-demo-investor');
    if (demoBtn) demoBtn.addEventListener('click', () => loginDemoAccount('investor'));

    const demoAdminBtn = document.getElementById('btn-demo-director');
    if (demoAdminBtn) demoAdminBtn.addEventListener('click', () => loginDemoAccount('admin'));

    // Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeLoginModal();
    });

    // Check GIS initialization periodically if script loads slightly later
    let attempts = 0;
    const gisCheck = setInterval(() => {
      attempts++;
      if (typeof window.google !== 'undefined' && window.google.accounts) {
        renderGoogleButton();
        clearInterval(gisCheck);
      }
      if (attempts > 20) clearInterval(gisCheck);
    }, 300);
  });

  // Expose public API
  window.ChainAuth = {
    getSession,
    setSession,
    clearSession,
    getWallet,
    topupWallet,
    openLoginModal,
    closeLoginModal,
    loginDemoAccount,
    updateUI
  };
})();

