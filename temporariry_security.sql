CREATE TABLE security_personnel (
    security_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    badge_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    hire_date DATE NULL,
    termination_date DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    INDEX idx_security_employee_id (employee_id),
    INDEX idx_security_badge (badge_number),
    INDEX idx_security_active (is_active),
    INDEX idx_security_deleted (deleted_at),

    CONSTRAINT check_security_termination_after_hire 
        CHECK (termination_date IS NULL OR hire_date IS NULL OR termination_date >= hire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
