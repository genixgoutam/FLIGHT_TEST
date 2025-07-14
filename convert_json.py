import json

# Input and output file paths
input_file = "airports_locations.json"
output_file = "airports_cleaned.json"

with open(input_file, "r", encoding="utf-8") as f:
    airports = json.load(f)

cleaned = []
for airport in airports:
    # Use IATA code as 'code', skip if missing
    code = airport.get("iata") or airport.get("code")
    if not code or not airport.get("name") or not airport.get("latitude") or not airport.get("longitude"):
        continue
    # Determine type
    name = airport["name"]
    place = airport["country"]
    city = airport["city"]
    airport_type = "international" if "international" in name.lower() else "domestic"
    cleaned.append({
        "name": name,
        "code": code,
        "latitude": float(airport["latitude"]),
        "longitude": float(airport["longitude"]),
        "type": airport_type,
        "location": {   
            "country": place,
            "city": city,
        },
    })

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)

print(f"Converted {len(cleaned)} airports to {output_file}")