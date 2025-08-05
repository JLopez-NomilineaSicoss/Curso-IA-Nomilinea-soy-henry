-- Script de inicialización de la base de datos
-- Este script se ejecuta automáticamente cuando se inicia el contenedor de PostgreSQL

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Crear esquemas
CREATE SCHEMA IF NOT EXISTS hotel_system;

-- Configurar zona horaria
SET timezone = 'UTC';

-- Crear índices para optimización
-- Los índices específicos se crearán cuando las tablas se creen via SQLAlchemy

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Función para generar IDs únicos
CREATE OR REPLACE FUNCTION generate_booking_id()
RETURNS TEXT AS $$
BEGIN
    RETURN 'HTL-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 6));
END;
$$ language 'plpgsql';

-- Crear usuario de aplicación con permisos limitados
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'hotel_app') THEN
        CREATE ROLE hotel_app WITH LOGIN PASSWORD 'hotel_app_password';
    END IF;
END
$$;

-- Otorgar permisos
GRANT USAGE ON SCHEMA hotel_system TO hotel_app;
GRANT CREATE ON SCHEMA hotel_system TO hotel_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hotel_system TO hotel_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hotel_system TO hotel_app;

-- Configuraciones de rendimiento
ALTER DATABASE hotel_reservations SET shared_preload_libraries = 'pg_stat_statements';
ALTER DATABASE hotel_reservations SET log_statement = 'all';
ALTER DATABASE hotel_reservations SET log_min_duration_statement = 1000;

-- Insertar datos de ejemplo para testing
INSERT INTO hotel_system.users (id, email, password_hash, first_name, last_name, role, is_active, created_at, updated_at)
VALUES 
    (uuid_generate_v4(), 'admin@hotel.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewVyVR7hn7VmXWbW', 'Admin', 'User', 'admin', true, NOW(), NOW()),
    (uuid_generate_v4(), 'manager@hotel.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewVyVR7hn7VmXWbW', 'Manager', 'User', 'manager', true, NOW(), NOW()),
    (uuid_generate_v4(), 'guest@hotel.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewVyVR7hn7VmXWbW', 'Guest', 'User', 'guest', true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Log de inicialización
INSERT INTO hotel_system.system_logs (message, level, timestamp)
VALUES ('Database initialized successfully', 'INFO', NOW())
ON CONFLICT DO NOTHING;
