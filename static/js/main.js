const map = L.map('map').setView([18.55, 76.15], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let cropLayer = null;
let stressLayer = null;

const cropStyle = {
    color: 'green',
    weight: 2,
    fillColor: 'green',
    fillOpacity: 0.35
};

const stressStyle = {
    color: 'red',
    weight: 2,
    fillColor: 'red',
    fillOpacity: 0.35
};

function removeLayers() {
    if (cropLayer) map.removeLayer(cropLayer);
    if (stressLayer) map.removeLayer(stressLayer);
}

function loadGeoJSON(url, style, type) {
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            return L.geoJSON(data, {
                style: style,
                onEachFeature: function (feature, layer) {
                    let popupText = 'No data';
                    if (type === 'crop') {
                        popupText = 'Crop: ' + (feature.properties.crop || 'Unknown');
                    } else if (type === 'stress') {
                        popupText = 'Stress: ' + (feature.properties.stress || 'Unknown');
                    }
                    layer.bindPopup(popupText);
                }
            });
        });
}

function loadCropMap() {
    removeLayers();
    loadGeoJSON('/data/crop_map.geojson', cropStyle, 'crop')
        .then(layer => {
            cropLayer = layer.addTo(map);
            map.fitBounds(cropLayer.getBounds());
        });
}

function loadStressMap() {
    removeLayers();
    loadGeoJSON('/data/stress_map.geojson', stressStyle, 'stress')
        .then(layer => {
            stressLayer = layer.addTo(map);
            map.fitBounds(stressLayer.getBounds());
        });
}

function loadBothMaps() {
    removeLayers();

    Promise.all([
        loadGeoJSON('/data/crop_map.geojson', cropStyle, 'crop'),
        loadGeoJSON('/data/stress_map.geojson', stressStyle, 'stress')
    ]).then(([cropL, stressL]) => {
        cropLayer = cropL.addTo(map);
        stressLayer = stressL.addTo(map);
        map.fitBounds(cropLayer.getBounds());
    });
}

L.marker([18.55, 76.15]).addTo(map)
    .bindPopup('Pilot area placeholder')
    .openPopup();

const ctx = document.getElementById('trendChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        datasets: [{
            label: 'NDVI',
            data: [0.3, 0.45, 0.62, 0.58],
            borderColor: '#1f4e79',
            backgroundColor: 'rgba(31, 78, 121, 0.2)',
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: true, max: 1 }
        }
    }
});

document.getElementById('cropBtn').addEventListener('click', loadCropMap);
document.getElementById('stressBtn').addEventListener('click', loadStressMap);
document.getElementById('bothBtn').addEventListener('click', loadBothMaps);

document.getElementById('loadBtn').addEventListener('click', async () => {
    const res = await fetch('/api/advisory');
    const data = await res.json();

    if (data.length > 0) {
        document.getElementById('cropName').textContent = data[0].crop || 'Unknown';
        document.getElementById('stressName').textContent = data[0].stress || 'Unknown';
        document.getElementById('advisoryName').textContent = data[0].advisory || 'Unknown';
    }
});