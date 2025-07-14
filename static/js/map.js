// map.js
// Renders all airports on a Leaflet map
// Modular: Extend for advanced visualizations or user input

document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Fetch all airports from API
    fetch('/api/airports/')
    .then(response => response.json())
    .then(data => {
        data.forEach(function(airport) {
            var marker = L.marker([airport.latitude, airport.longitude]).addTo(map);
            marker.bindPopup(`<b>${airport.name}</b><br>Code: ${airport.code}`);
        });
    });
}); 