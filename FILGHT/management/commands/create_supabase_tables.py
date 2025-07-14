from django.core.management.base import BaseCommand
from django.conf import settings
from FILGHT.supabase_utils import get_supabase_client


class Command(BaseCommand):
    help = 'Create required tables in Supabase database'

    def handle(self, *args, **options):
        client = get_supabase_client()
        if not client:
            self.stdout.write(
                self.style.ERROR('❌ Supabase client not initialized. Please check your credentials.')
            )
            return

        self.stdout.write('🏗️  Creating Supabase tables...')

        # SQL commands to create tables
        create_tables_sql = """
        -- Create weather table
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            type VARCHAR(50),
            severity VARCHAR(20),
            visibility VARCHAR(20),
            wind_speed VARCHAR(20),
            temperature VARCHAR(20),
            humidity VARCHAR(20),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Create air table (for air traffic and operational constraints)
        CREATE TABLE IF NOT EXISTS air (
            id SERIAL PRIMARY KEY,
            type VARCHAR(100),
            status VARCHAR(50),
            level VARCHAR(20),
            description TEXT,
            duration VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Create fuel table (for fuel efficiency data)
        CREATE TABLE IF NOT EXISTS fuel (
            id SERIAL PRIMARY KEY,
            aircraft_type VARCHAR(100),
            efficiency VARCHAR(20),
            fuel_consumption VARCHAR(20),
            emissions VARCHAR(50),
            optimization_potential VARCHAR(20),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Create safety table (for safety factors)
        CREATE TABLE IF NOT EXISTS safety (
            id SERIAL PRIMARY KEY,
            factor VARCHAR(100),
            value VARCHAR(50),
            score VARCHAR(20),
            risk_level VARCHAR(20),
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Create flights table (if not already exists)
        CREATE TABLE IF NOT EXISTS flights (
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
        """

        # Enable RLS and create policies
        rls_policies_sql = """
        -- Enable Row Level Security (RLS) for all tables
        ALTER TABLE weather ENABLE ROW LEVEL SECURITY;
        ALTER TABLE air ENABLE ROW LEVEL SECURITY;
        ALTER TABLE fuel ENABLE ROW LEVEL SECURITY;
        ALTER TABLE safety ENABLE ROW LEVEL SECURITY;
        ALTER TABLE flights ENABLE ROW LEVEL SECURITY;

        -- Create policies to allow read access for all users
        CREATE POLICY "Allow read access to weather" ON weather
            FOR SELECT USING (true);

        CREATE POLICY "Allow read access to air" ON air
            FOR SELECT USING (true);

        CREATE POLICY "Allow read access to fuel" ON fuel
            FOR SELECT USING (true);

        CREATE POLICY "Allow read access to safety" ON safety
            FOR SELECT USING (true);

        CREATE POLICY "Allow read access to flights" ON flights
            FOR SELECT USING (true);

        -- Create policies for insert/update
        CREATE POLICY "Allow insert to weather" ON weather
            FOR INSERT WITH CHECK (true);

        CREATE POLICY "Allow insert to air" ON air
            FOR INSERT WITH CHECK (true);

        CREATE POLICY "Allow insert to fuel" ON fuel
            FOR INSERT WITH CHECK (true);

        CREATE POLICY "Allow insert to safety" ON safety
            FOR INSERT WITH CHECK (true);

        CREATE POLICY "Allow insert to flights" ON flights
            FOR INSERT WITH CHECK (true);
        """

        # Create indexes
        indexes_sql = """
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_weather_type ON weather(type);
        CREATE INDEX IF NOT EXISTS idx_air_type ON air(type);
        CREATE INDEX IF NOT EXISTS idx_fuel_aircraft_type ON fuel(aircraft_type);
        CREATE INDEX IF NOT EXISTS idx_safety_factor ON safety(factor);
        CREATE INDEX IF NOT EXISTS idx_flights_origin ON flights(origin_code);
        CREATE INDEX IF NOT EXISTS idx_flights_destination ON flights(destination_code);
        """

        try:
            # Execute table creation
            self.stdout.write('📋 Creating tables...')
            result = client.rpc('exec_sql', {'sql': create_tables_sql}).execute()
            self.stdout.write(self.style.SUCCESS('✅ Tables created successfully!'))

            # Execute RLS policies
            self.stdout.write('🔒 Setting up RLS policies...')
            result = client.rpc('exec_sql', {'sql': rls_policies_sql}).execute()
            self.stdout.write(self.style.SUCCESS('✅ RLS policies created successfully!'))

            # Execute indexes
            self.stdout.write('📊 Creating indexes...')
            result = client.rpc('exec_sql', {'sql': indexes_sql}).execute()
            self.stdout.write(self.style.SUCCESS('✅ Indexes created successfully!'))

            self.stdout.write(
                self.style.SUCCESS('🎉 All tables and policies created successfully!')
            )
            self.stdout.write('You can now run: python manage.py init_supabase')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating tables: {e}')
            )
            self.stdout.write(
                self.style.WARNING('💡 Try running the SQL script manually in Supabase SQL Editor')
            ) 