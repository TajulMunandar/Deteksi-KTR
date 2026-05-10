# Redesigned UI/UX: Dashboard Monitoring Filter & Heatmap System

## 1. UI Layout Description

### Layout Structure (Mobile-First)
```
┌─────────────────────────────────────────┐
│  Header                                 │
├─────────────────────────────────────────┤
│  Heatmap Toggle (Standalone, Prominent) │
├─────────────────────────────────────────┤
│  Filter Status (Segmented Control)      │
├─────────────────────────────────────────┤
│  Filter Waktu (Horizontal Chip Row)     │
├─────────────────────────────────────────┤
│  Map Visualization                      │
├─────────────────────────────────────────┤
│  Legend & Stats                         │
└─────────────────────────────────────────┘
```

### Desktop Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header                                                 │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────────────┬───────────────────────┐ │
│  │  Heatmap Toggle           │  Filter Status        │ │
│  │  (centered)               │  (segmented)          │ │
│  ├───────────────────────────┼───────────────────────┤ │
│  │  Filter Waktu             │                       │ │
│  │  (full width chips)       │  Map Visualization    │ │
│  └───────────────────────────┴───────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 2. UX Interaction Flow

### Filter Interaction Sequence

```
User Action Flow:
1. User melihat Heatmap Toggle → klik untuk ON
   → Heatmap ON state: icon hilang, teks "Heatmap Active" muncul, warna toggle berubah
   
2. User memilih Filter Status "Patuh"
   → Heatmap otomatis update (smooth transition 300ms)
   → Marker berubah menjadi heatmap layer dengan data Patuh
   
3. User memilih Filter Waktu "Pagi"
   → Heatmap langsung update kombinasi: Patuh + Pagi
   → Data ditampilkan real-time tanpa reload
   
4. User beralih ke "Pelanggaran Berat" + "Sore"
   → Heatmap menampilkan konsentrasi pelanggaran berat jam sore
```

### Filter Combination Logic
| Heatmap | Status Filter | Time Filter | Visualization |
|---------|---------------|-------------|---------------|
| OFF | any | any | Normal markers |
| ON | all | all | All violation heatmap |
| ON | Patuh | all | Patuh locations heatmap |
| ON | Ringan | all | Ringan violation heatmap |
| ON | Berat | all | Berat violation heatmap (default) |
| ON | Patuh | Pagi | Patuh locations, morning only |
| ON | Berat | Sore | Berat violations, afternoon only |

---

## 3. Design System

### Color Palette
```css
/* Primary Colors */
--color-primary-500: #3b82f6;  /* Accent biru modern */
--color-primary-600: #2563eb;
--color-primary-700: #1d4ed8;

/* Status Colors */
--color-patuh: #22c55e;        /* Hijau */
--color-ringan: #eab308;      /* Kuning/Orange */
--color-berat: #ef4444;       /* Merah */

/* Neutrals */
--color-navy-900: #0f172a;     /* Dark navy */
--color-slate-50: #f8fafc;
--color-slate-100: #f1f5f9;
--color-slate-200: #e2e8f0;
--color-white: #ffffff;

/* Heatmap Active Accent */
--color-heatmap-active: #f59e0b;  /* Orange mencolok */
```

### Typography
- Font: Plus Jakarta Sans
- Sizes: 
  - Status labels: 14px medium
  - Filter chips: 13px
  - Count badges: 11px bold

### Spacing
- Section gap: 16px (mobile), 24px (desktop)
- Filter chips padding: 10px 16px
- Toggle padding: 8px 20px

---

## 4. Component States

### 4.1 Heatmap Toggle States

**OFF State:**
```
[☀️ Heatmap] ← icon + teks
┌─────────────────────────────┐
│  Icon: fa-fire-flame-curved │
│  Color: slate-300           │
│  Background: white          │
│  Border: slate-200          │
└─────────────────────────────┘
```

**ON State:**
```
[Heatmap Active] ← tanpa icon, teks berwarna
┌─────────────────────────────┐
│  Icon: hidden               │
│  Color: white               │
│  Background: orange-500     │
│  Shadow: 0 4px 12px rgba(...)│
└─────────────────────────────┘
```

### 4.2 Filter Status States (Segmented Control)

**Inactive Button:**
```
┌─────────────────┐
│  Semua         │
└─────────────────┘
- Background: white
- Border: slate-200
- Text: slate-600
```

**Active Button:**
```
┌─────────────────┐
│  Patuh   ✓     │
└─────────────────┘
- Background: green-500
- Text: white
- Shadow: 0 2px 8px rgba(34, 197, 94, 0.3)
- Border: green-400 (highlight)
- Badge count: (optional)
```

### 4.3 Filter Waktu States (Chip)

**Inactive Chip:**
```
┌─────────────────┐
│  🕐 Pagi       │
└─────────────────┘
- Background: white
- Border: slate-200
- Text: slate-600
- Icon: slate-400
```

**Active Chip:**
```
┌─────────────────┐
│  🕐 Pagi       │
└─────────────────┘
- Background: blue-50
- Border: blue-300
- Text: blue-700
- Icon: blue-500
- Rounded: full
```

---

## 5. Responsive Behavior

### Mobile (< 768px)
```css
.filter-container {
  flex-direction: column;
  gap: 12px;
}

.filter-chips {
  overflow-x: auto;
  padding-bottom: 4px;
}

.segmented-control {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
}
```

### Tablet (768px - 1024px)
```css
.filter-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.segmented-control {
  flex: 1;
}
```

### Desktop (> 1024px)
```css
.dashboard-filters {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 24px;
  align-items: start;
}
```

---

## 6. Recommended Components

### 6.1 Heatmap Toggle Component
```html
<button id="heatmapToggle" class="heatmap-toggle heatmap-off">
  <span class="toggle-icon">
    <i class="fas fa-fire-flame-curved"></i>
  </span>
  <span class="toggle-text">Heatmap</span>
</button>

<!-- ON State -->
<button id="heatmapToggle" class="heatmap-toggle heatmap-active">
  <span class="toggle-text">Heatmap Active</span>
</button>
```

### 6.2 Status Segmented Control
```html
<div class="segmented-control" role="radiogroup">
  <button class="segment inactive" data-filter="all">
    Semua
    <span class="count">(120)</span>
  </button>
  <button class="segment active" data-filter="patuh">
    Patuh
    <span class="count green">(45)</span>
  </button>
  <button class="segment inactive" data-filter="ringan">
    Ringan
    <span class="count orange">(35)</span>
  </button>
  <button class="segment inactive" data-filter="berat">
    Berat
    <span class="count red">(40)</span>
  </button>
</div>
```

### 6.3 Time Chip Filter
```html
<div class="time-chips" role="radiogroup">
  <button class="chip inactive" data-time="all">
    <i class="fas fa-infinity"></i>
    <span>Semua Waktu</span>
  </button>
  <button class="chip active" data-time="pagi">
    <i class="fas fa-sun"></i>
    <span>Pagi (07-11)</span>
  </button>
  <button class="chip inactive" data-time="siang">
    <i class="fas fa-cloud-sun"></i>
    <span>Siang (12-14)</span>
  </button>
  <button class="chip inactive" data-time="sore">
    <i class="fas fa-cloud"></i>
    <span>Sore (15-18)</span>
  </button>
</div>
```

---

## 7. Animation & Transitions

### Transition Timing
```css
:root {
  --transition-fast: 150ms ease;
  --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 500ms ease;
}

/* Heatmap toggle */
.heatmap-toggle {
  transition: all var(--transition-normal);
}

/* Heatmap layer fade */
.leaflet-heatmap-layer {
  animation: fadeIn 300ms ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### Filter Change Sequence
1. User click filter → 50ms visual feedback (scale 0.95)
2. Filter applied → 300ms heatmap transition
3. Data update → 100ms count badge update

---

## 8. Implementation Notes

### JavaScript State Management
```javascript
// Unified filter state
const filterState = {
  heatmap: false,
  status: 'all',
  time: 'all'
};

// Update all visualization on any filter change
function updateAllVisualization() {
  const filteredData = violationData.filter(v => {
    const categoryMatch = filterState.status === 'all' || v.category === filterState.status;
    const timeMatch = filterState.time === 'all' || getTimePeriod(v.timestamp) === filterState.time;
    return categoryMatch && timeMatch;
  });
  
  if (filterState.heatmap) {
    updateHeatmap(filteredData);
  } else {
    updateMarkers(filteredData);
  }
  
  updateStatistics(filteredData);
}
```

### Count Badge Logic
```javascript
// Display count and percentage in badges
const stats = {
  all: { count: 120, percentage: 100 },
  patuh: { count: 45, percentage: 37.5 },
  ringan: { count: 35, percentage: 29.2 },
  berat: { count: 40, percentage: 33.3 }
};
```

---

## 9. User Experience Enhancements

### Visual Hierarchy
1. **Primary Action**: Heatmap Toggle (most prominent, centered)
2. **Secondary**: Status Filter (segmented, clear hierarchy)
3. **Tertiary**: Time Filter (chips, supplementary)

### Feedback States
- Loading: Show skeleton animation on heatmap
- Empty: Display "Tidak ada data" message
- Error: Toast notification with retry option

### Accessibility
- All interactive elements keyboard navigable
- ARIA labels for screen readers
- Sufficient color contrast (WCAG AA compliant)