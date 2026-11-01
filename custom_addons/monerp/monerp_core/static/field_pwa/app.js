// VEID Field App - Application Logic & Bi-directional Sync
const API_BASE = window.location.origin.includes('8069') ? window.location.origin : 'http://127.0.0.1:8069';

class VeidFieldApp {
  constructor() {
    this.db = window.veidDb;
    this.isOnline = navigator.onLine;
    this.activeTab = 'btp';
    this.cachedData = {
      construction_sites: [],
      farm_parcels: []
    };

    this.init();
  }

  async init() {
    await this.db.init();
    this.setupEventListeners();
    this.updateNetworkStatus();
    await this.loadReferenceData();
    await this.updateQueueUI();

    // Register service worker if available
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js').catch(err => {
        console.log('[SW] Registration notice:', err);
      });
    }

    // Auto-sync if online at launch
    if (this.isOnline) {
      this.syncPendingQueue();
    }
  }

  setupEventListeners() {
    // Network change listeners
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.updateNetworkStatus();
      this.showFeedback('Connexion rétablie ! Lancement de la synchronisation...', 'info');
      this.syncPendingQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.updateNetworkStatus();
      this.showFeedback('Mode hors-ligne actif (Zone blanche). Les données seront stockées localement.', 'info');
    });

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = e.currentTarget.dataset.tab;
        this.switchTab(tab);
      });
    });

    // Forms
    document.getElementById('form-btp').addEventListener('submit', (e) => this.handleBtpSubmit(e));
    document.getElementById('form-agro').addEventListener('submit', (e) => this.handleAgroSubmit(e));
    document.getElementById('btn-manual-sync').addEventListener('click', () => this.syncPendingQueue());

    // Dynamic dropdown updates
    const siteSelect = document.getElementById('btp-site-select');
    if (siteSelect) {
      siteSelect.addEventListener('change', () => this.updateLotDropdown());
    }
  }

  updateNetworkStatus() {
    const badge = document.getElementById('network-badge');
    const label = document.getElementById('network-label');
    if (this.isOnline) {
      badge.className = 'network-badge online';
      label.textContent = 'En Ligne';
    } else {
      badge.className = 'network-badge offline';
      label.textContent = 'Hors-Ligne (Zone Blanche)';
    }
  }

  switchTab(tabName) {
    this.activeTab = tabName;
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-panel').forEach(p => {
      p.classList.toggle('active', p.id === `tab-${tabName}`);
    });
    if (tabName === 'queue') {
      this.updateQueueUI();
    }
  }

  async loadReferenceData() {
    // 1. Try local cache first (Instant UI render)
    const local = await this.db.getReferenceData('bootstrap_cache');
    if (local) {
      this.cachedData = local;
      this.populateDropdowns();
    }

    // 2. If online, refresh from VEID API
    if (this.isOnline) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/veid/field/bootstrap`, {
          headers: { 'Accept': 'application/json' }
        });
        if (res.ok) {
          const json = await res.json();
          if (json.status === 'success') {
            this.cachedData = {
              construction_sites: json.construction_sites || [],
              farm_parcels: json.farm_parcels || []
            };
            await this.db.saveReferenceData('bootstrap_cache', this.cachedData);
            this.populateDropdowns();
          }
        }
      } catch (err) {
        console.log('[FieldApp] Offline or bootstrap error, using cached data:', err);
      }
    }
  }

  populateDropdowns() {
    // Populate BTP sites
    const siteSelect = document.getElementById('btp-site-select');
    if (siteSelect) {
      const sites = this.cachedData.construction_sites || [];
      siteSelect.innerHTML = sites.length ? '' : '<option value="">Aucun chantier en cache</option>';
      sites.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = `${s.code} - ${s.name} (${s.progress_percentage}%)`;
        siteSelect.appendChild(opt);
      });
      this.updateLotDropdown();
    }

    // Populate Parcelles
    const parcelSelect = document.getElementById('agro-parcel-select');
    if (parcelSelect) {
      const parcels = this.cachedData.farm_parcels || [];
      parcelSelect.innerHTML = parcels.length ? '' : '<option value="">Aucune parcelle en cache</option>';
      parcels.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = `${p.code} - ${p.name} (${p.crop_type || 'Culture'})`;
        parcelSelect.appendChild(opt);
      });
    }
  }

  updateLotDropdown() {
    const siteSelect = document.getElementById('btp-site-select');
    const lotSelect = document.getElementById('btp-lot-select');
    if (!siteSelect || !lotSelect) return;

    const selectedSiteId = parseInt(siteSelect.value, 10);
    const site = (this.cachedData.construction_sites || []).find(s => s.id === selectedSiteId);
    lotSelect.innerHTML = '';

    if (site && site.lots && site.lots.length) {
      site.lots.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l.id;
        opt.textContent = `${l.name} (Actuel: ${l.progress_percentage}%)`;
        lotSelect.appendChild(opt);
      });
    } else {
      lotSelect.innerHTML = '<option value="">Lot général du chantier</option>';
    }
  }

  async handleBtpSubmit(e) {
    e.preventDefault();
    const siteId = parseInt(document.getElementById('btp-site-select').value, 10);
    const lotId = parseInt(document.getElementById('btp-lot-select').value, 10) || null;
    const progress = parseFloat(document.getElementById('btp-progress-input').value);
    const notes = document.getElementById('btp-notes-input').value;

    if (!siteId) {
      alert('Veuillez sélectionner un chantier.');
      return;
    }

    const report = {
      type: 'construction_progress',
      site_id: siteId,
      lot_id: lotId,
      new_progress: progress,
      notes: notes,
      timestamp: new Date().toISOString()
    };

    await this.processReportSubmission(report, 'Pointage chantier BTP');
    document.getElementById('form-btp').reset();
  }

  async handleAgroSubmit(e) {
    e.preventDefault();
    const parcelId = parseInt(document.getElementById('agro-parcel-select').value, 10);
    const weight = parseFloat(document.getElementById('agro-weight-input').value);
    const notes = document.getElementById('agro-notes-input').value;

    if (!parcelId || isNaN(weight)) {
      alert('Veuillez sélectionner une parcelle et renseigner le poids.');
      return;
    }

    const report = {
      type: 'harvest_weighing',
      parcel_id: parcelId,
      actual_yield_tonnes: weight,
      notes: notes,
      timestamp: new Date().toISOString()
    };

    await this.processReportSubmission(report, 'Pesée récolte agricole');
    document.getElementById('form-agro').reset();
  }

  async processReportSubmission(report, label) {
    // 1. Toujours enregistrer dans IndexedDB en premier pour garantir zéro perte de données (Offline-First)
    const enqueued = await this.db.enqueueReport(report);
    await this.updateQueueUI();

    if (!this.isOnline) {
      this.showFeedback(`${label} enregistré avec succès en local (Mode Déconnecté).`, 'info');
      return;
    }

    // 2. Si en ligne, tenter la synchronisation immédiate
    this.showFeedback(`${label} enregistré localement, synchronisation réseau en cours...`, 'info');
    await this.syncPendingQueue();
  }

  async syncPendingQueue() {
    if (!this.isOnline) {
      this.showFeedback('Impossible de synchroniser : appareil hors-ligne.', 'info');
      return;
    }

    const pending = await this.db.getPendingReports();
    if (!pending.length) {
      this.updateQueueUI();
      return;
    }

    const syncBtn = document.getElementById('btn-manual-sync');
    if (syncBtn) {
      syncBtn.disabled = true;
      syncBtn.textContent = 'Synchronisation en cours...';
    }

    try {
      const res = await fetch(`${API_BASE}/api/v1/veid/field/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ reports: pending })
      });

      if (res.ok) {
        const json = await res.json();
        for (const item of pending) {
          await this.db.markReportSynced(item.client_uuid);
        }
        await this.db.clearSyncedReports();
        this.showFeedback(`Synchronisation réussie ! ${pending.length} opération(s) intégrée(s) au serveur central VEID.`, 'success');
      } else {
        this.showFeedback('Erreur serveur lors de la synchronisation, les données restent conservées en local.', 'info');
      }
    } catch (err) {
      console.error('[Sync] Network error:', err);
      this.showFeedback('Connexion instable, la synchronisation réessayera au prochain signal réseau.', 'info');
    } finally {
      if (syncBtn) {
        syncBtn.disabled = false;
        syncBtn.textContent = 'Synchroniser maintenant';
      }
      await this.updateQueueUI();
      await this.loadReferenceData();
    }
  }

  async updateQueueUI() {
    const queueList = document.getElementById('queue-items-container');
    const queueCountBadge = document.getElementById('queue-count-badge');
    const navBadge = document.getElementById('tab-queue-badge');

    const pending = await this.db.getPendingReports();
    const count = pending.length;

    if (queueCountBadge) queueCountBadge.textContent = `${count} en attente`;
    if (navBadge) {
      navBadge.textContent = count ? `(${count})` : '';
      navBadge.style.display = count ? 'inline' : 'none';
    }

    if (!queueList) return;

    if (!count) {
      queueList.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 24px;">Aucune opération en attente. Tout est synchronisé avec le serveur central VEID.</div>';
      return;
    }

    queueList.innerHTML = '';
    pending.forEach(item => {
      const div = document.createElement('div');
      div.className = 'queue-item';
      const isBtp = item.type === 'construction_progress';
      div.innerHTML = `
        <div>
          <div class="queue-title">${isBtp ? '🏗️ Avancement Chantier BTP' : '🌾 Pesée Récolte Agricole'}</div>
          <div class="queue-meta">${isBtp ? `Progression: ${item.new_progress}%` : `Poids: ${item.actual_yield_tonnes} tonnes`} • ${new Date(item.timestamp).toLocaleTimeString()}</div>
        </div>
        <span class="badge-pending">En attente</span>
      `;
      queueList.appendChild(div);
    });
  }

  showFeedback(message, type = 'success') {
    const el = document.getElementById('feedback-alert');
    if (!el) return;
    el.className = `alert-feedback ${type}`;
    el.textContent = message;
    el.style.display = 'block';
    setTimeout(() => {
      el.style.display = 'none';
    }, 5000);
  }
}

// Bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.fieldApp = new VeidFieldApp();
});
