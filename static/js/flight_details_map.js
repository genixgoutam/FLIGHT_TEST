// flight_details_map.js
// Renders the flight details on a Leaflet map
// Modular: Extend for advanced visualizations or user input

function setupAirportAutocomplete(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);

    input.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        fetch('/api/airports-json/')
            .then(response => response.json())
            .then(airports => {
                const filtered = airports.filter(a =>
                    a.city.toLowerCase().includes(query) ||
                    a.country.toLowerCase().includes(query) ||
                    a.iata_code.toLowerCase().includes(query) ||
                    a.airport_name.toLowerCase().includes(query)
                );
                list.innerHTML = '';
                filtered.slice(0, 10).forEach(a => {
                    const item = document.createElement('div');
                    item.className = 'dropdown-item';
                    item.innerHTML = `<strong>${a.city}, ${a.country}</strong> (${a.iata_code})<br><small>${a.airport_name}</small>`;
                    item.onclick = () => {
                        input.value = `${a.city}, ${a.country} (${a.iata_code})`;
                        list.innerHTML = '';
                    };
                    list.appendChild(item);
                });
            });
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !list.contains(e.target)) {
            list.innerHTML = '';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('flight-details-map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch routes from API and show only QAOA, Dijkstra, Alternative
    fetch('/api/flights/')
    .then(response => response.json())
    .then(data => {
        // Filter and order routes: QAOA (blue), Dijkstra (red), Alternative (red)
        function getFirstRouteByMethod(routes, methodName) {
            return routes.find(r => r.method && r.method.toLowerCase() === methodName);
        }
        function getFirstAlternative(routes) {
            return routes.find(r => r.method && r.method.toLowerCase().includes('alternative'));
        }
        const qaoaRoute = getFirstRouteByMethod(data, 'qaoa');
        const dijkstraRoute = getFirstRouteByMethod(data, 'dijkstra');
        const altRoute = getFirstAlternative(data);
        const routes = [qaoaRoute, dijkstraRoute, altRoute].filter(Boolean);
        routes.forEach((route, idx) => {
            let color = idx === 0 ? 'blue' : 'red';
            if (route.coordinates && route.coordinates.length > 1) {
                const polyline = L.polyline(route.coordinates, {color: color, weight: 5, opacity: 0.8}).addTo(map);
                // Add markers for start/end
                const startMarker = L.marker(route.coordinates[0]).addTo(map).bindPopup(route.origin_name || 'Origin');
                const endMarker = L.marker(route.coordinates[route.coordinates.length-1]).addTo(map).bindPopup(route.destination_name || 'Destination');
                if (idx === 0) {
                    map.fitBounds(route.coordinates);
                }
            }
        });
        // Fill flight summary and cost breakdown for first route
        if (routes.length > 0) {
            var route = routes[0];
            var summary = document.getElementById('flight-summary');
            summary.innerHTML = `<li>Route: ${route.method || 'QAOA'}</li><li>From: ${route.origin_code || ''}</li><li>To: ${route.destination_code || ''}</li>`;
            var cost = document.getElementById('cost-breakdown');
            cost.innerHTML = `<li>Price: $${route.price || ''}</li><li>Currency: ${route.currency || ''}</li>`;
        }
    });

    setupAirportAutocomplete('from-airport', 'from-airport-list');
    setupAirportAutocomplete('to-airport', 'to-airport-list');
}); 