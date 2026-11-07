/**
 * PT CHAIN ASIA CONECT - Dynamic SCF Investment & DOKU Payment Gateway Engine
 * Handles:
 * 1. DOKU Payment Gateway (Jokul Checkout / VA / QRIS / E-Wallet)
 *    Client ID: BRN-0243-1793632486351
 *    Key ID: doku_key_72a40988fc954392a90b31d5421838c9
 * 2. Dynamic SCF Project Catalog & Investment Flow
 * 3. Real-Time Auto-Detection of Payment Status with Webhook Simulation
 * 4. Reactive Portfolio, Balances, & Financial Statement Synchronization
 */

(function () {
  const DOKU_CONFIG = {
    clientId: 'BRN-0243-1793632486351',
    keyId: 'doku_key_72a40988fc954392a90b31d5421838c9',
    isProduction: true,
    merchantName: 'PT CHAIN ASIA CONECT',
    escrowCustodian: 'Bank Mandiri Escrow Custodian (POJK No. 57/2020)'
  };

  const STORAGE_KEYS = {
    PROJECTS: 'chain_scf_projects_catalog',
    INVESTMENTS: 'chain_user_investments',
    PENDING_TX: 'chain_doku_pending_tx',
    WALLET: 'chain_user_wallet'
  };

  // Default Master Projects Catalog
  const DEFAULT_PROJECTS = [
    {
      id: 'SM-KRU-01',
      code: 'SM-KRU-01',
      title: 'Model Distribusi Bahan Baku Hospitality Krui (Kawasan 3T)',
      category: 'Sukuk Mudharabah',
      issuer: 'PT Chain Asia Conect & Mitra Konsorsium Krui',
      targetFunding: 500000000,
      collectedFunding: 435000000,
      tenorMonths: 6,
      yieldRate: 15.8,
      yieldPeriod: 'Kuartalan (Per 3 Bulan)',
      minInvestment: 1000000,
      dueDate: '18 Mei 2027',
      collateral: 'Kontrak Pengadaan Vendor Resort Villa Nalu & Surfmatra',
      status: 'Aktif Pendanaan',
      riskGrade: 'A- (Low Risk Supply Chain)',
      prospectusUrl: '/docs/model-distribusi-bahan-baku-hospitality-krui-researchgate.pdf'
    },
    {
      id: 'SCF-MED-04',
      code: 'SCF-MED-04',
      title: 'Supply Chain Invoice Financing: Mesin Radiologi & Software PACS DICOM',
      category: 'B2B Factoring / Invoice',
      issuer: 'Divisi Perangkat Medis PT CHAIN ASIA CONECT',
      targetFunding: 750000000,
      collectedFunding: 665000000,
      tenorMonths: 3,
      yieldRate: 14.5,
      yieldPeriod: 'Jatuh Tempo (Bullet)',
      minInvestment: 2500000,
      dueDate: '28 Desember 2026',
      collateral: 'Verified Purchase Order & Piutang RS Regional Sumatera',
      status: 'Aktif Pendanaan',
      riskGrade: 'A (Government & Institutional RS Backed)',
      prospectusUrl: '/scf'
    },
    {
      id: 'EQ-HOS-02',
      code: 'EQ-HOS-02',
      title: 'Saham Digital SCF: Sourcing & Logistik Daging/Bahan Pangan Resort Krui',
      category: 'Equity Crowdfunding',
      issuer: 'PT Boga Logistik Pesisir (Anak Usaha Rantai Pasok)',
      targetFunding: 1000000000,
      collectedFunding: 870450000,
      tenorMonths: 12,
      yieldRate: 18.2,
      yieldPeriod: 'Dividen Kuartalan + Dividen Tahunan',
      minInvestment: 5000000,
      dueDate: 'RUPS Maret 2027',
      collateral: 'Armada Berpendingin & Fasilitas Gudang Transit Tanjung Karang',
      status: 'Aktif Pendanaan',
      riskGrade: 'A+ (High Margin Export Food)',
      prospectusUrl: '/business'
    },
    {
      id: 'SM-COLD-03',
      code: 'SM-COLD-03',
      title: 'Cold-Chain Reefer Hub Krui & Sistem Telemetri IoT Rantai Dingin',
      category: 'Sukuk Ijarah',
      issuer: 'Konsorsium Logistik 3T PT CHAIN ASIA CONECT',
      targetFunding: 450000000,
      collectedFunding: 145000000,
      tenorMonths: 6,
      yieldRate: 16.0,
      yieldPeriod: 'Bagi Hasil Bulanan',
      minInvestment: 1000000,
      dueDate: '30 Juni 2027',
      collateral: '2 Unit Container Reefer 20ft & Modul IoT Tracker',
      status: 'Baru Dibuka (Kuartal IV)',
      riskGrade: 'A (Aset Fisik Bergerak)',
      prospectusUrl: '/scf'
    }
  ];

  // Default Initial User Active Investments
  const DEFAULT_USER_INVESTMENTS = [
    {
      projectId: 'SM-KRU-01',
      code: 'SM-KRU-01',
      title: 'Model Distribusi Bahan Baku Hospitality Krui (Kawasan 3T)',
      category: 'Sukuk Mudharabah',
      amount: 50000000,
      yieldRate: 15.8,
      tenorMonths: 6,
      dateInvested: '2026-09-30',
      dueDate: '18 Mei 2027',
      estimatedQuarterlyYield: 3950000,
      status: 'Lancar &bull; On Schedule',
      receivedYield: 3950000
    },
    {
      projectId: 'SCF-MED-04',
      code: 'SCF-MED-04',
      title: 'Supply Chain Invoice Financing: Mesin Radiologi & Software PACS DICOM',
      category: 'B2B Factoring',
      amount: 45000000,
      yieldRate: 14.5,
      tenorMonths: 3,
      dateInvested: '2026-09-28',
      dueDate: '28 Desember 2026',
      estimatedQuarterlyYield: 1631250,
      status: 'Lancar &bull; Verified PO',
      receivedYield: 1631250
    },
    {
      projectId: 'EQ-HOS-02',
      code: 'EQ-HOS-02',
      title: 'Saham Digital SCF: Sourcing & Logistik Daging/Bahan Pangan Resort Krui',
      category: 'Equity Crowdfunding',
      amount: 30450000,
      yieldRate: 18.2,
      tenorMonths: 12,
      dateInvested: '2026-09-14',
      dueDate: 'RUPS Maret 2027',
      estimatedQuarterlyYield: 1385000,
      status: 'Dividen Q1 Dibayarkan',
      receivedYield: 1385000
    }
  ];

  // 1. Get Projects Catalog
  function getProjectsCatalog() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.PROJECTS);
      if (data) return JSON.parse(data);
      localStorage.setItem(STORAGE_KEYS.PROJECTS, JSON.stringify(DEFAULT_PROJECTS));
      return DEFAULT_PROJECTS;
    } catch (e) {
      return DEFAULT_PROJECTS;
    }
  }

  // 2. Get User Active Investments
  function getUserInvestments() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.INVESTMENTS);
      if (data) return JSON.parse(data);
      localStorage.setItem(STORAGE_KEYS.INVESTMENTS, JSON.stringify(DEFAULT_USER_INVESTMENTS));
      return DEFAULT_USER_INVESTMENTS;
    } catch (e) {
      return DEFAULT_USER_INVESTMENTS;
    }
  }

  // 3. Create Investment (from RDN Kas or via DOKU)
  function investInProject(projectId, amount, paymentSource, dokuPaymentDetails) {
    const cleanAmount = parseInt(amount, 10);
    if (isNaN(cleanAmount) || cleanAmount <= 0) return { success: false, message: 'Nominal tidak valid' };

    const projects = getProjectsCatalog();
    const project = projects.find(p => p.id === projectId);
    if (!project) return { success: false, message: 'Proyek tidak ditemukan' };

    const remainingQuota = project.targetFunding - project.collectedFunding;
    if (cleanAmount > remainingQuota && remainingQuota > 0) {
      return { success: false, message: `Nominal melebihi sisa kuota (Maks: Rp ${remainingQuota.toLocaleString('id-ID')})` };
    }

    // Check if using RDN Kas
    let wallet = (window.ChainAuth && window.ChainAuth.getWallet) ? window.ChainAuth.getWallet() : null;
    if (paymentSource === 'rdn_balance') {
      if (!wallet || wallet.cashBalance < cleanAmount) {
        return { success: false, message: 'Saldo kas RDN tidak mencukupi untuk investasi ini. Silakan Top Up terlebih dahulu.' };
      }
      wallet.cashBalance -= cleanAmount;
    } else {
      // If payment is via DOKU, wallet cash balance stays same, but total assets increase
      if (!wallet) wallet = { cashBalance: 0, totalAssets: 0, totalYield: 0, history: [] };
    }

    // Update wallet total assets
    wallet.totalAssets += cleanAmount;

    // Add to project collected funding
    project.collectedFunding += cleanAmount;
    localStorage.setItem(STORAGE_KEYS.PROJECTS, JSON.stringify(projects));

    // Calculate quarterly yield
    const quarterlyYield = Math.round((cleanAmount * (project.yieldRate / 100)) / 4);

    // Add or update user investment
    const investments = getUserInvestments();
    const existingIndex = investments.findIndex(inv => inv.projectId === projectId);
    if (existingIndex >= 0) {
      investments[existingIndex].amount += cleanAmount;
      investments[existingIndex].estimatedQuarterlyYield += quarterlyYield;
    } else {
      investments.unshift({
        projectId: project.id,
        code: project.code,
        title: project.title,
        category: project.category,
        amount: cleanAmount,
        yieldRate: project.yieldRate,
        tenorMonths: project.tenorMonths,
        dateInvested: new Date().toISOString().split('T')[0],
        dueDate: project.dueDate,
        estimatedQuarterlyYield: quarterlyYield,
        status: 'Lancar &bull; On Schedule',
        receivedYield: 0
      });
    }
    localStorage.setItem(STORAGE_KEYS.INVESTMENTS, JSON.stringify(investments));

    // Record transaction
    const txId = 'TX-INV-' + Math.floor(100000 + Math.random() * 900000);
    wallet.history.unshift({
      id: txId,
      date: new Date().toISOString().split('T')[0],
      type: 'INVESTASI',
      desc: `Alokasi Efek ${project.code} - ${project.title}`,
      amount: -cleanAmount,
      status: 'Berhasil'
    });

    localStorage.setItem(STORAGE_KEYS.WALLET, JSON.stringify(wallet));

    // Notify listeners
    window.dispatchEvent(new CustomEvent('chain-wallet-updated', { detail: wallet }));
    window.dispatchEvent(new CustomEvent('chain-investments-updated', { detail: investments }));

    return {
      success: true,
      txId,
      amount: cleanAmount,
      projectTitle: project.title,
      estimatedQuarterlyYield: quarterlyYield
    };
  }

  // 4. Create DOKU Payment Request (Simulate DOKU Checkout Payload)
  function createDokuPaymentRequest(params) {
    const invoiceNumber = 'INV-' + Date.now().toString().slice(-8);
    const amount = parseInt(params.amount, 10);
    const channel = params.channel || 'VIRTUAL_ACCOUNT_MANDIRI';
    const purpose = params.purpose || 'TOPUP'; // TOPUP or DIRECT_INVEST
    const projectId = params.projectId || null;

    let vaNumber = '';
    let qrString = '';
    let channelName = '';

    if (channel === 'VIRTUAL_ACCOUNT_MANDIRI') {
      vaNumber = '889710' + Math.floor(100000 + Math.random() * 900000);
      channelName = 'Bank Mandiri Virtual Account';
    } else if (channel === 'VIRTUAL_ACCOUNT_BCA') {
      vaNumber = '731095' + Math.floor(100000 + Math.random() * 900000);
      channelName = 'BCA Virtual Account';
    } else if (channel === 'VIRTUAL_ACCOUNT_BRI') {
      vaNumber = '128890' + Math.floor(100000 + Math.random() * 900000);
      channelName = 'BRI Virtual Account (BRIVA)';
    } else if (channel === 'VIRTUAL_ACCOUNT_BNI') {
      vaNumber = '988107' + Math.floor(100000 + Math.random() * 900000);
      channelName = 'BNI Virtual Account';
    } else if (channel === 'QRIS') {
      vaNumber = 'NMID: ID10260904' + Math.floor(1000 + Math.random() * 9000);
      qrString = `00020101021226680016ID.DOKU.WWW0118${DOKU_CONFIG.clientId}0215${invoiceNumber}51440014ID.GO.QRIS.WWW0215ID10260904000152045812530336054${amount}5802ID5920PT CHAIN ASIA CONEC6007JAKARTA62190115${invoiceNumber}6304`;
      channelName = 'QRIS Dinamis (Real-Time)';
    } else if (channel === 'OVO' || channel === 'SHOPEEPAY' || channel === 'DANA') {
      vaNumber = 'EWALLET-' + channel + '-' + Math.floor(100000 + Math.random() * 900000);
      channelName = channel + ' E-Wallet';
    } else {
      vaNumber = '4512-xxxx-xxxx-' + Math.floor(1000 + Math.random() * 9000);
      channelName = 'Kartu Kredit / Debit Online';
    }

    const pendingTx = {
      invoiceNumber,
      amount,
      channel,
      channelName,
      vaNumber,
      qrString,
      purpose,
      projectId,
      status: 'PENDING',
      createdAt: Date.now(),
      expiredAt: Date.now() + 15 * 60 * 1000, // 15 mins
      dokuClientId: DOKU_CONFIG.clientId,
      dokuKeyId: DOKU_CONFIG.keyId
    };

    localStorage.setItem(STORAGE_KEYS.PENDING_TX, JSON.stringify(pendingTx));
    return pendingTx;
  }

  // 5. Complete DOKU Payment (Auto-Detect Webhook Execution)
  function completeDokuPayment(invoiceNumber) {
    let pendingTx = null;
    try {
      const data = localStorage.getItem(STORAGE_KEYS.PENDING_TX);
      if (data) pendingTx = JSON.parse(data);
    } catch (e) {}

    if (!pendingTx || (invoiceNumber && pendingTx.invoiceNumber !== invoiceNumber)) {
      return { success: false, message: 'Transaksi tidak ditemukan' };
    }

    pendingTx.status = 'PAID';
    pendingTx.paidAt = Date.now();
    localStorage.removeItem(STORAGE_KEYS.PENDING_TX);

    if (pendingTx.purpose === 'DIRECT_INVEST' && pendingTx.projectId) {
      // Execute direct investment
      return investInProject(pendingTx.projectId, pendingTx.amount, 'doku_direct', pendingTx);
    } else {
      // Execute standard RDN topup
      if (window.ChainAuth && window.ChainAuth.topupWallet) {
        window.ChainAuth.topupWallet(pendingTx.amount, pendingTx.channelName, pendingTx.vaNumber);
      }
      return {
        success: true,
        invoiceNumber: pendingTx.invoiceNumber,
        amount: pendingTx.amount,
        channelName: pendingTx.channelName
      };
    }
  }

  // Expose to window
  window.ChainSCF = {
    DOKU_CONFIG,
    getProjectsCatalog,
    getUserInvestments,
    investInProject,
    createDokuPaymentRequest,
    completeDokuPayment
  };
})();

