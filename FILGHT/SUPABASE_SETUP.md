# Supabase Setup Guide

This guide will help you set up Supabase to work with the Flight Optimization Report system using table-based data storage.

## Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. Python packages: `supabase` and `python-dotenv`

## Installation

```bash
pip install supabase python-dotenv
```

## Configuration

### 1. Environment Variables

Create a `.env` file in your project root with the following variables:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

You can find these values in your Supabase project dashboard under Settings > API.

### 2. Database Setup

The system expects the following tables in your Supabase database:

#### Flights Table
```sql
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    airline VARCHAR(100),
    origin_code VARCHAR(10),
    destination_code VARCHAR(10),
    departure_time TIME,
    arrival_time TIME,
    status VARCHAR(50),
    gate VARCHAR(10),
    terminal VARCHAR(10),
    aircraft VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Weather Table
```sql
CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),
    severity VARCHAR(20),
    visibility VARCHAR(20),
    wind_speed VARCHAR(20),
    temperature VARCHAR(20),
    humidity VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Air Table (Air Traffic/Operational Constraints)
```sql
CREATE TABLE air (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100),
    status VARCHAR(50),
    level VARCHAR(20),
    description TEXT,
    duration VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Fuel Table (Fuel Efficiency)
```sql
CREATE TABLE fuel (
    id SERIAL PRIMARY KEY,
    aircraft_type VARCHAR(100),
    efficiency VARCHAR(20),
    fuel_consumption VARCHAR(20),
    emissions VARCHAR(50),
    optimization_potential VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Safety Table (Safety Factors)
```sql
CREATE TABLE safety (
    id SERIAL PRIMARY KEY,
    factor VARCHAR(100),
    value VARCHAR(50),
    score VARCHAR(20),
    risk_level VARCHAR(20),
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing the Connection

Use the Django management command to test your Supabase connection:

```bash
python manage.py init_supabase --test-only
```

## Initializing Sample Data

To populate Supabase with sample report data:

```bash
python manage.py init_supabase
```

This will create sample data for:
- Weather conditions (in `weather` table)
- Air traffic/operational constraints (in `air` table)
- Fuel efficiency metrics (in `fuel` table)
- Safety factors (in `safety` table)

## Usage

Once configured, the report system will:

1. **Automatically detect Supabase**: The system will try to fetch data from Supabase tables first
2. **Fallback to local data**: If Supabase is not available, it will use local file data
3. **Show data source**: The report page will display whether data is coming from Supabase or local files
4. **Initialize button**: If using local data, a button will appear to initialize Supabase data

## API Endpoints

- `/api/report/` - Fetches report data (Supabase or local)
- `/api/init-supabase/` - Initializes Supabase with sample data
- `/api/flights/dynamic/` - Fetches flight data (includes Supabase integration)

### Fetching Data by ID

The system provides API endpoints to fetch specific records by their ID:

- `/api/air/<id>/` - Fetch air traffic data by ID
- `/api/weather/<id>/` - Fetch weather data by ID
- `/api/fuel/<id>/` - Fetch fuel efficiency data by ID
- `/api/safety/<id>/` - Fetch safety data by ID
- `/api/flight/<id>/` - Fetch flight data by ID

#### Example Usage

**Direct Supabase Function:**
```python
from FILGHT.supabase_utils import fetch_air_data_by_id

# Fetch air data with ID 1
air_data = fetch_air_data_by_id(1)
if air_data:
    print(f"Type: {air_data.get('type')}")
    print(f"Status: {air_data.get('status')}")
    print(f"Level: {air_data.get('level')}")
```

**API Endpoint:**
```javascript
// Fetch air data with ID 1 via API
fetch('/api/air/1/')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(data.data);
            // data.data contains the air record
        }
    });
```

**Django View:**
```python
from .supabase_utils import fetch_air_data_by_id

def my_view(request, air_id):
    air_data = fetch_air_data_by_id(air_id)
    if air_data:
        return JsonResponse({
            'success': True,
            'data': air_data
        })
    else:
        return JsonResponse({
            'success': False,
            'error': f'No air record found with ID {air_id}'
        }, status=404)
```

## Data Mapping

The system maps Supabase tables to report sections as follows:

| Supabase Table | Report Section | Description |
|----------------|----------------|-------------|
| `weather` | Weather Report | Weather conditions and forecasts |
| `air` | Air Traffic | Operational constraints and air traffic data |
| `fuel` | Fuel Efficiency | Aircraft fuel efficiency metrics |
| `safety` | Safety Factor | Safety assessments and risk factors |

## Testing

### Test ID Fetching

Run the test script to verify ID-based data fetching:

```bash
python FILGHT/test_fetch_by_id.py
```

### Test Examples

Run the example script to see practical usage:

```bash
python FILGHT/air_id_example.py
```

## Troubleshooting

### Connection Issues
- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that your Supabase project is active
- Ensure your IP is not blocked by Supabase

### Table Issues
- Verify all required tables exist in your Supabase database
- Check table permissions (RLS policies)
- Ensure the tables have the correct column structure

### Data Issues
- Run the initialization command to populate sample data
- Check the browser console for JavaScript errors
- Verify the API endpoints are working

### ID Fetching Issues
- Ensure the record with the specified ID exists in the table
- Check that RLS policies allow reading the specific record
- Verify the ID parameter is a valid integer

## Security Notes

- Keep your Supabase keys secure
- Use environment variables, never hardcode credentials
- Consider using Row Level Security (RLS) in Supabase for production
- Set appropriate table permissions for your use case

## Running Tests

Use the test script to verify your setup:

```bash
python FILGHT/test_supabase.py
```

This will test:
- Connection to Supabase
- Access to all required tables
- Data initialization
- Data fetching functionality
- ID-based data fetching 