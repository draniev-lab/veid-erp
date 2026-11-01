// VEID Field App - IndexedDB Manager (Offline-First Store & Queue)
const DB_NAME = 'veid_field_db';
const DB_VERSION = 1;

class VeidLocalDb {
  constructor() {
    this.db = null;
  }

  async init() {
    if (this.db) return this.db;
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        // Store for cached reference data (sites, lots, parcelles)
        if (!db.objectStoreNames.contains('reference_data')) {
          db.createObjectStore('reference_data', { keyPath: 'key' });
        }
        // Store for pending offline mutations awaiting sync
        if (!db.objectStoreNames.contains('sync_queue')) {
          const syncStore = db.createObjectStore('sync_queue', { keyPath: 'client_uuid' });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncStore.createIndex('status', 'status', { unique: false });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(this.db);
      };

      request.onerror = (event) => {
        console.error('[IndexedDB] Init error:', event.target.error);
        reject(event.target.error);
      };
    });
  }

  async saveReferenceData(key, data) {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('reference_data', 'readwrite');
      const store = tx.objectStore('reference_data');
      store.put({ key, data, cached_at: new Date().toISOString() });
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  async getReferenceData(key) {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('reference_data', 'readonly');
      const store = tx.objectStore('reference_data');
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result ? req.result.data : null);
      req.onerror = () => reject(req.error);
    });
  }

  async enqueueReport(report) {
    const db = await this.init();
    const item = {
      ...report,
      client_uuid: report.client_uuid || `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: report.timestamp || new Date().toISOString(),
      status: 'pending' // 'pending' | 'syncing' | 'synced' | 'failed'
    };

    return new Promise((resolve, reject) => {
      const tx = db.transaction('sync_queue', 'readwrite');
      const store = tx.objectStore('sync_queue');
      store.put(item);
      tx.oncomplete = () => resolve(item);
      tx.onerror = () => reject(tx.error);
    });
  }

  async getPendingReports() {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('sync_queue', 'readonly');
      const store = tx.objectStore('sync_queue');
      const req = store.getAll();
      req.onsuccess = () => {
        const items = (req.result || []).filter(r => r.status === 'pending' || r.status === 'failed');
        resolve(items);
      };
      req.onerror = () => reject(req.error);
    });
  }

  async getQueueCount() {
    const pending = await this.getPendingReports();
    return pending.length;
  }

  async markReportSynced(client_uuid) {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('sync_queue', 'readwrite');
      const store = tx.objectStore('sync_queue');
      const req = store.get(client_uuid);
      req.onsuccess = () => {
        if (req.result) {
          req.result.status = 'synced';
          store.put(req.result);
        }
        resolve(true);
      };
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  async clearSyncedReports() {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('sync_queue', 'readwrite');
      const store = tx.objectStore('sync_queue');
      const req = store.getAll();
      req.onsuccess = () => {
        const synced = (req.result || []).filter(r => r.status === 'synced');
        for (const item of synced) {
          store.delete(item.client_uuid);
        }
      };
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }
}

// Global instance
if (typeof window !== 'undefined') {
  window.veidDb = new VeidLocalDb();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { VeidLocalDb };
}
