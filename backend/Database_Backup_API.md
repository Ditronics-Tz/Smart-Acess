# Database Backup API Endpoints

This document outlines the API endpoints for database backup, restore, and listing available backups in the Smart-Access system. All endpoints require administrator permissions.

## Endpoints

### 1. Create Database Backup
- **Method**: POST
- **URL**: `/api/administrator/backup/`
- **Description**: Triggers a database backup using `pg_dump`. Creates a timestamped SQL file in the `backups/` directory.
- **Request Body**: None
- **Response**:
  - Success: `{"status": "success", "backup_file": "/path/to/backup_YYYYMMDD_HHMMSS.sql"}`
  - Error: `{"status": "error", "message": "Error details"}`
- **Permissions**: Administrator only

### 2. Restore Database
- **Method**: POST
- **URL**: `/api/administrator/restore/<str:backup_filename>/`
- **Description**: Restores the database from a specified backup file using `psql`.
- **Request Body**: None
- **Response**:
  - Success: `{"status": "success", "message": "Database restored"}`
  - Error: `{"status": "error", "message": "Error details"}` (e.g., if backup not found)
- **Permissions**: Administrator only
- **Notes**: Replace `<backup_filename>` with the actual filename (e.g., `backup_20230830_120000.sql`).

### 3. List Available Backups
- **Method**: GET
- **URL**: `/api/administrator/backups/`
- **Description**: Returns a list of available backup files in the `backups/` directory.
- **Request Body**: None
- **Response**:
  - Success: `{"backups": ["backup_20230830_120000.sql", "backup_20230829_110000.sql"]}`
  - If no backups: `{"backups": []}`
- **Permissions**: Administrator only

## Notes
- All endpoints are under the `/api/administrator/` prefix.
- Backups are stored in `backend/adminstrator/backups/`.
- Ensure PostgreSQL is installed and configured with the correct credentials in your `.env` file (`DB_NAME`, `DB_USER`).
- Test in a development environment to avoid data loss.
- For production, consider adding authentication, logging, and cloud storage for backups.
