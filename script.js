// ===== VARIABLES =====
let map;
let markers = [];
let heatmapLayer = null;
let currentFilter = 'all';
let violationData = [];

// DOM Elements
const form = document.getElementById('violationForm');
const locationInput = document.getElementById('locationName');
const autoCategory = document.getElementById('autoCategory');
const photoInput = document.getElementById('photo');
const latitudeInput = document.getElementById('latitude');
const longitudeInput = document.getElementById('longitude');
const photoPreview = document.getElementById('photoPreview');
const predictionResult = document.getElementById('predictionResult');
const clearFormBtn = document.getElementById('clearFormBtn');
const clearAllBtn = document.getElementById('clearAllBtn');
const heatmapToggle = document.getElementById('heatmapToggle');
const filterButtons = document.querySelectorAll('.filter-btn');
const confirmModal = document.getElementById('confirmModal');
const confirmMessage = document.getElementById('confirmMessage');
const cancelConfirm = document.getElementById('cancelConfirm');
const confirmAction = document.getElementById('confirmAction');

// Category icons
const categoryIcons = {
    patuh: 'fa-check-circle',
    ringan: 'fa-exclamation-triangle',
    berat: 'fa-times-circle'
};

// Category labels
const categoryLabels = {
    patuh: '✅ Patuh',
    ringan: '⚠️ Pelanggaran Ringan',
    berat: '🔴 Pelanggaran Berat'
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    loadData();
    setupEventListeners();
});

// ===== MAP INITIALIZATION =====
function initMap() {
    // Initialize map centered on Indonesia (Jakarta)
    map = L.map('map', {
        center: [-6.2088, 106.8456],
        zoom: 13,
        zoomControl: true
    });

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add map click event
    map.on('click', function(e) {
        latitudeInput.value = e.latlng.lat.toFixed(6);
        longitudeInput.value = e.latlng.lng.toFixed(6);
        
        // Show toast
        showToast('Lokasi berhasil dipilih!', 'success');
    });

    // Try to get user's location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                map.setView([position.coords.latitude, position.coords.longitude], 15);
            },
            function(error) {
                console.log('Could not get user location:', error);
            }
        );
    }
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Form submission
    form.addEventListener('submit', handleFormSubmit);

    // Photo preview
    photoInput.addEventListener('change', handlePhotoPreview);

    // Clear form button
    clearFormBtn.addEventListener('click', clearForm);

    // Clear all data button
    clearAllBtn.addEventListener('click', () => {
        showConfirmModal('Apakah Anda yakin ingin menghapus semua data?', () => {
            clearAllData();
        });
    });

    // Heatmap toggle
    heatmapToggle.addEventListener('change', toggleHeatmap);

    // Filter buttons
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => handleFilter(btn.dataset.filter));
    });

    // Modal events
    cancelConfirm.addEventListener('click', hideConfirmModal);
    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) hideConfirmModal();
    });
}

// ===== FORM HANDLING =====
function handleFormSubmit(e) {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
        return;
    }

    // Create violation object
    const categoryValue = autoCategory.querySelector('span')?.textContent || 'Unknown';
    let categoryKey = 'berat';
    if (categoryValue.includes('RINGAN')) {
        categoryKey = 'ringan';
    } else if (categoryValue.includes('PATUH')) {
        categoryKey = 'patuh';
    }
    const violation = {
        id: Date.now(),
        locationName: locationInput.value.trim(),
        category: categoryKey,
        latitude: parseFloat(latitudeInput.value),
        longitude: parseFloat(longitudeInput.value),
        photo: photoInput.files[0] ? photoInput.files[0] : null,
        photoData: photoPreview.querySelector('img')?.src || null,
        timestamp: new Date().toISOString()
    };

    // Save to localStorage
    saveViolation(violation);

    // Add marker to map
    addMarker(violation);

    // Update statistics
    updateStatistics();

    // Show success message
    showToast('Data berhasil disimpan!', 'success');

    // Clear form
    clearForm();
}

function validateForm() {
    if (!locationInput.value.trim()) {
        showToast('Mohon masukkan nama lokasi!', 'error');
        locationInput.focus();
        return false;
    }

    if (!latitudeInput.value || !longitudeInput.value) {
        showToast('Mohon klik pada peta untuk memilih lokasi!', 'error');
        return false;
    }

    return true;
}

function handlePhotoPreview(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            photoPreview.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
            photoPreview.classList.add('active');
            
            // Call prediction API
            predictImage(file);
        };
        reader.readAsDataURL(file);
    } else {
        photoPreview.innerHTML = '';
        photoPreview.classList.remove('active');
        predictionResult.innerHTML = '';
        predictionResult.classList.remove('active');
    }
}

function clearForm() {
    form.reset();
    photoPreview.innerHTML = '';
    photoPreview.classList.remove('active');
    predictionResult.innerHTML = '';
    predictionResult.classList.remove('active');
    autoCategory.innerHTML = '<span class="text-slate-400">Upload foto untuk deteksi otomatis</span>';
    autoCategory.className = 'w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm';
    latitudeInput.value = '';
    longitudeInput.value = '';
}

// ===== AI PREDICTION =====
async function predictImage(file) {
    // Show loading state
    predictionResult.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mendeteksi...',
    predictionResult.className = 'prediction-result active loading';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.error) {
            predictionResult.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error: ${result.error}`;
            predictionResult.className = 'prediction-result active error';
            return;
        }
        
        // Display detection results
        let detectionsHTML = '';
        if (result.detections && result.detections.length > 0) {
            result.detections.forEach(det => {
                detectionsHTML += `
                    <div class="detection-item">
                        <span>${det.class}</span>
                        <span>${(det.confidence * 100).toFixed(1)}%</span>
                    </div>
                `;
            });
        } else {
            detectionsHTML = '<div class="detection-item">Tidak ada objek terdeteksi</div>';
        }
        
        // Get compliance status
        const compliance = result.compliance || {};
        
        // Determine category based on user's rules:
        // - Ada Rokok = ringan
        // - Ada Merokok = berat
        // - Tidak ada keduanya = patuh
        const hasMerokok = result.summary?.has_merokok || false;
        const hasRokok = result.summary?.has_rokok || false;
        
        let categoryValue = '';
        let categoryText = '';
        let badgeClass = '';
        
        if (hasMerokok) {
            categoryValue = 'berat';
            categoryText = '🔴 PELANGGARAN BERAT';
            badgeClass = 'berat';
        } else if (hasRokok) {
            categoryValue = 'ringan';
            categoryText = '⚠️ PELANGGARAN RINGAN';
            badgeClass = 'ringan';
        } else {
            categoryValue = 'patuh';
            categoryText = '✅ PATUH';
            badgeClass = 'patuh';
        }
        
        // Update auto category display
        autoCategory.innerHTML = `<span class="font-semibold">${categoryText}</span>`;
        autoCategory.className = 'w-full px-3 py-2 border rounded-lg text-sm ' + 
            (badgeClass === 'berat' ? 'bg-red-50 border-red-300 text-red-700' : 
             badgeClass === 'ringan' ? 'bg-yellow-50 border-yellow-300 text-yellow-700' : 
             'bg-green-50 border-green-300 text-green-700');
        
        predictionResult.innerHTML = `
            <div><strong>Deteksi:</strong></div>
            ${detectionsHTML}
            <div><strong>Status:</strong> ${compliance.status || 'Unknown'}</div>
            <span class="compliance-badge ${badgeClass}">${compliance.status || 'Unknown'}</span>
        `;
        predictionResult.className = 'prediction-result active success';
        
    } catch (error) {
        console.error('Prediction error:', error);
        predictionResult.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error: ${error.message}`;
        predictionResult.className = 'prediction-result active error';
    }
}

// ===== MARKER MANAGEMENT =====
function addMarker(violation) {
    // Create custom icon based on category
    const icon = createMarkerIcon(violation.category);

    // Create marker
    const marker = L.marker([violation.latitude, violation.longitude], { icon })
        .addTo(map);

    // Create popup content
    const popupContent = createPopupContent(violation);
    marker.bindPopup(popupContent);

    // Add to markers array
    markers.push({
        id: violation.id,
        marker: marker,
        category: violation.category
    });

    // Apply current filter
    applyFilter();

    return marker;
}

function createMarkerIcon(category) {
    const colors = {
        patuh: '#22c55e',
        ringan: '#eab308',
        berat: '#ef4444'
    };

    const icons = {
        patuh: '✓',
        ringan: '!',
        berat: '✕'
    };

    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            width: 36px;
            height: 36px;
            background: ${colors[category]};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 16px;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        ">${icons[category]}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -18]
    });
}

function createPopupContent(violation) {
    const photoHTML = violation.photoData 
        ? `<img src="${violation.photoData}" alt="Foto" class="popup-photo" />` 
        : '<p style="color: #94a3b8; font-style: italic;">Tidak ada foto</p>';

    return `
        <div class="popup-content">
            <h4>${violation.locationName}</h4>
            <span class="popup-category ${violation.category}">${categoryLabels[violation.category]}</span>
            ${photoHTML}
            <p class="popup-coords">
                <i class="fas fa-map-marker-alt"></i> 
                ${violation.latitude.toFixed(6)}, ${violation.longitude.toFixed(6)}
            </p>
            <button class="popup-delete" onclick="deleteMarker(${violation.id})">
                <i class="fas fa-trash-alt"></i> Hapus
            </button>
        </div>
    `;
}

function deleteMarker(id) {
    // Find marker
    const markerIndex = markers.findIndex(m => m.id === id);
    if (markerIndex > -1) {
        // Remove from map
        map.removeLayer(markers[markerIndex].marker);
        
        // Remove from array
        markers.splice(markerIndex, 1);

        // Remove from localStorage
        violationData = violationData.filter(v => v.id !== id);
        localStorage.setItem('violationData', JSON.stringify(violationData));

        // Update statistics
        updateStatistics();

        // Update heatmap if enabled
        if (heatmapToggle.checked) {
            updateHeatmap();
        }

        showToast('Marker berhasil dihapus!', 'success');
    }
}

// ===== DATA STORAGE =====
function saveViolation(violation) {
    violationData.push(violation);
    localStorage.setItem('violationData', JSON.stringify(violationData));
}

function loadData() {
    const storedData = localStorage.getItem('violationData');
    if (storedData) {
        violationData = JSON.parse(storedData);
        
        // Add markers for all stored data
        violationData.forEach(violation => {
            addMarker(violation);
        });

        // Update statistics
        updateStatistics();
    }
}

function clearAllData() {
    // Remove all markers from map
    markers.forEach(m => map.removeLayer(m.marker));
    markers = [];

    // Clear localStorage
    violationData = [];
    localStorage.removeItem('violationData');

    // Update statistics
    updateStatistics();

    // Hide heatmap if visible
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
        heatmapLayer = null;
    }

    hideConfirmModal();
    showToast('Semua data berhasil dihapus!', 'success');
}

// ===== STATISTICS =====
function updateStatistics() {
    const stats = {
        patuh: violationData.filter(v => v.category === 'patuh').length,
        ringan: violationData.filter(v => v.category === 'ringan').length,
        berat: violationData.filter(v => v.category === 'berat').length,
        total: violationData.length
    };

    document.getElementById('statPatuh').textContent = stats.patuh;
    document.getElementById('statRingan').textContent = stats.ringan;
    document.getElementById('statBerat').textContent = stats.berat;
    document.getElementById('statTotal').textContent = stats.total;
}

// ===== FILTERING =====
function handleFilter(filter) {
    currentFilter = filter;

    // Update button states
    filterButtons.forEach(btn => {
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Apply filter
    applyFilter();
}

function applyFilter() {
    markers.forEach(m => {
        if (currentFilter === 'all' || m.category === currentFilter) {
            m.marker.setOpacity(1);
            m.marker.setZIndexOffset(1000);
        } else {
            m.marker.setOpacity(0);
            m.marker.setZIndexOffset(0);
        }
    });
}

// ===== HEATMAP =====
function toggleHeatmap() {
    if (heatmapToggle.checked) {
        showHeatmap();
    } else {
        hideHeatmap();
    }
}

function showHeatmap() {
    // Get violations with berat category
    const beratViolations = violationData.filter(v => v.category === 'berat');

    if (beratViolations.length === 0) {
        showToast('Tidak ada pelanggaran berat untuk ditampilkan!', 'info');
        heatmapToggle.checked = false;
        return;
    }

    // Create heatmap data
    const heatData = beratViolations.map(v => [v.latitude, v.longitude, 0.8]);

    // Add heatmap layer
    heatmapLayer = L.heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        gradient: {
            0.2: 'blue',
            0.4: 'cyan',
            0.6: 'lime',
            0.8: 'yellow',
            1.0: 'red'
        }
    }).addTo(map);

    showToast('Heatmap pelanggaran berat ditampilkan!', 'info');
}

function hideHeatmap() {
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
        heatmapLayer = null;
    }
}

function updateHeatmap() {
    if (heatmapToggle.checked) {
        hideHeatmap();
        showHeatmap();
    }
}

// ===== MODAL =====
function showConfirmModal(message, onConfirm) {
    confirmMessage.textContent = message;
    confirmModal.classList.add('active');
    
    // Store the confirm action
    confirmAction.onclick = onConfirm;
}

function hideConfirmModal() {
    confirmModal.classList.remove('active');
}

// ===== TOAST NOTIFICATION =====
function showToast(message, type = 'info') {
    // Get toast container
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Icon mapping
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };

    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    // Show toast
    setTimeout(() => toast.style.opacity = '1', 10);

    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== UTILITY FUNCTIONS =====
// Make deleteMarker available globally
window.deleteMarker = deleteMarker;
