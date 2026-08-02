-- Create institutional_requests table
CREATE TABLE IF NOT EXISTS institutional_requests (
    id SERIAL PRIMARY KEY,
    request_number VARCHAR(50) UNIQUE NOT NULL,
    requester_name VARCHAR(255) NOT NULL,
    requester_email VARCHAR(255) NOT NULL,
    institution_name VARCHAR(255) NOT NULL,
    request_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    external_reference_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_request_number ON institutional_requests(request_number);
CREATE INDEX IF NOT EXISTS idx_requester_email ON institutional_requests(requester_email);
CREATE INDEX IF NOT EXISTS idx_status ON institutional_requests(status);
CREATE INDEX IF NOT EXISTS idx_external_reference_id ON institutional_requests(external_reference_id);
CREATE INDEX IF NOT EXISTS idx_created_at ON institutional_requests(created_at);

-- Create trigger to update updated_at automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_institutional_requests_updated_at ON institutional_requests;
CREATE TRIGGER update_institutional_requests_updated_at BEFORE UPDATE ON institutional_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
