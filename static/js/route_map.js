// route_map.js
// Renders the optimized route on a Leaflet map
// Modular: Extend for advanced visualizations or user input

document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('route-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch multiple routes from API (should return array of routes)
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
        // Expecting data.routes to be an array of route objects
        // Each route: { path: [{latitude, longitude, name}], method, distance }
        let routes = Array.isArray(data.routes) ? data.routes.slice(0, 3) : [];
        routes.forEach((route, idx) => {
            let color = idx === 0 ? 'blue' : 'red';
            if (route.path && route.path.length > 1) {
                var latlngs = route.path.map(a => [a.latitude, a.longitude]);
                L.polyline(latlngs, {color: color, weight: 5, opacity: 0.8}).addTo(map);
                // Add markers for start/end
                L.marker(latlngs[0]).addTo(map).bindPopup(route.path[0].name);
                L.marker(latlngs[latlngs.length-1]).addTo(map).bindPopup(route.path[latlngs.length-1].name);
                if (idx === 0) {
                    map.fitBounds(latlngs);
                }
            }
        });
        // Fill route summary for first route
        if (routes.length > 0) {
            var route = routes[0];
            var summary = document.getElementById('route-summary');
            summary.innerHTML = `<li>Distance: ${route.distance} units</li><li>Method: ${route.method}</li>`;
        }
    });
}); 