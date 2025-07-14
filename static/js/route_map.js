// route_map.js
// Renders the optimized route on a Leaflet map
// Modular: Extend for advanced visualizations or user input

document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('route-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Example: Fetch route data from API (replace with actual API call)
    fetch('/api/optimize/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            airport_ids: [1, 2, 3], // Replace with dynamic IDs
            weights: { distance: 1.0, safety: 0.5, fuel: 0.2 }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.path) {
            var latlngs = data.path.map(a => [a.latitude, a.longitude]);
            L.polyline(latlngs, {color: 'blue'}).addTo(map);
            latlngs.forEach((latlng, idx) => {
                L.marker(latlng).addTo(map).bindPopup(data.path[idx].name);
            });
            map.fitBounds(latlngs);
            // Fill route summary
            var summary = document.getElementById('route-summary');
            summary.innerHTML = `<li>Distance: ${data.distance} units</li><li>Method: ${data.method}</li>`;
        }
    });
}); 