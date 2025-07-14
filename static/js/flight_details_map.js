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

    // Example: Fetch flight details from API (replace with actual API call)
    fetch('/api/flights/')
    .then(response => response.json())
    .then(data => {
        if (data.length > 0) {
            var flight = data[0]; // Replace with selected flight
            var latlngs = [
                [flight.origin.latitude, flight.origin.longitude],
                [flight.destination.latitude, flight.destination.longitude]
            ];
            L.polyline(latlngs, {color: 'green'}).addTo(map);
            L.marker(latlngs[0]).addTo(map).bindPopup(flight.origin.name);
            L.marker(latlngs[1]).addTo(map).bindPopup(flight.destination.name);
            map.fitBounds(latlngs);
            // Fill flight summary
            var summary = document.getElementById('flight-summary');
            summary.innerHTML = `<li>Flight: ${flight.flight_number}</li><li>From: ${flight.origin.code}</li><li>To: ${flight.destination.code}</li>`;
            // Fill cost breakdown
            var cost = document.getElementById('cost-breakdown');
            cost.innerHTML = `<li>Price: $${flight.price}</li><li>Currency: ${flight.currency}</li>`;
        }
    });

    setupAirportAutocomplete('from-airport', 'from-airport-list');
    setupAirportAutocomplete('to-airport', 'to-airport-list');
}); 