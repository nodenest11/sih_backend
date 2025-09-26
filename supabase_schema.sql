-- Smart Tourist Safety & Incident Response System
-- Supabase Database Schema

-- Create the tables for the Tourist Safety System

-- 1. Tourists table
CREATE TABLE IF NOT EXISTS public.tourists (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    trip_info TEXT,
    emergency_contact VARCHAR(20) NOT NULL,
    safety_score INTEGER DEFAULT 100 CHECK (safety_score >= 0 AND safety_score <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Locations table  
CREATE TABLE IF NOT EXISTS public.locations (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    tourist_id BIGINT NOT NULL REFERENCES public.tourists(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
    longitude DECIMAL(11, 8) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Alerts table
CREATE TABLE IF NOT EXISTS public.alerts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    tourist_id BIGINT NOT NULL REFERENCES public.tourists(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('panic', 'geofence')),
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved')),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8)
);

-- 4. Restricted zones table
CREATE TABLE IF NOT EXISTS public.restricted_zones (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    coordinates JSONB NOT NULL, -- Array of [lat, lon] coordinates forming a polygon
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_locations_tourist_timestamp ON public.locations(tourist_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_tourist_status ON public.alerts(tourist_id, status);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON public.alerts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tourists_contact ON public.tourists(contact);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for tourists table
DROP TRIGGER IF EXISTS update_tourists_updated_at ON public.tourists;
CREATE TRIGGER update_tourists_updated_at
    BEFORE UPDATE ON public.tourists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Optional
-- ALTER TABLE public.tourists ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.locations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.restricted_zones ENABLE ROW LEVEL SECURITY;

-- Insert sample restricted zones
INSERT INTO public.restricted_zones (name, coordinates) VALUES 
('Delhi Red Fort Restricted Area', '[[28.6562, 77.2410], [28.6580, 77.2410], [28.6580, 77.2440], [28.6562, 77.2440], [28.6562, 77.2410]]'),
('Goa Beach Danger Zone', '[[15.2993, 74.1240], [15.3010, 74.1240], [15.3010, 74.1260], [15.2993, 74.1260], [15.2993, 74.1240]]'),
('Shillong Restricted Military Zone', '[[25.5788, 91.8933], [25.5800, 91.8933], [25.5800, 91.8950], [25.5788, 91.8950], [25.5788, 91.8933]]')
ON CONFLICT DO NOTHING;