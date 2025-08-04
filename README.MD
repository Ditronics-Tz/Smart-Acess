# Smart-Access Backend

A RESTful API backend built with Django and Django REST Framework using `uv` for fast dependency management 🚀

---

## 🔧 Prerequisites

Make sure you have:

- **Python 3.11+** installed (Download from [python.org](https://www.python.org/downloads/))
- **PowerShell** (comes with Windows)
- **PostgreSQL** (if using PostgreSQL database)

---

## ⚡ Step 1: Install `uv` (Fast Python Package Manager)

### For Windows PowerShell:

```powershell
# Install uv using the official installer
irm https://astral.sh/uv/install.ps1 | iex
```

### Alternative installation via pip:

```powershell
pip install uv
```

**Note:** After installation, restart your PowerShell terminal to ensure `uv` is available in your PATH.

---

## 🚀 Step 2: Project Setup

### Clone and Navigate to Project:

```powershell
# Navigate to your project directory
cd "C:\Users\Daddy\Desktop\projects\Smart-Acess"
```

### Create Virtual Environment:

```powershell
# Create virtual environment using uv
uv venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📦 Step 3: Install Dependencies

```powershell
# Install all project dependencies
uv pip install -r requirements.txt
```

---

## 🗃️ Step 4: Database Setup

### For PostgreSQL (Recommended):

1. **Install PostgreSQL** from [postgresql.org](https://www.postgresql.org/download/windows/)

2. **Create Database:**

```powershell
# Connect to PostgreSQL (adjust path if needed)
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres

# In PostgreSQL shell:
CREATE DATABASE smart_access_db;
CREATE USER smart_access_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE smart_access_db TO smart_access_user;
\q
```

3. **Update Database Settings:**

Create a `.env` file in the project root:

```env
DB_NAME=smart_access_db
DB_USER=smart_access_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### For SQLite (Development Only):

No additional setup required - Django will create the database automatically.

---

## 🔄 Step 5: Django Setup

```powershell
# Navigate to backend directory
cd backend

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files (if needed)
python manage.py collectstatic --noinput
```

---

## 🏃‍♂️ Step 6: Run the Development Server

```powershell
# Start the Django development server
python manage.py runserver

# Or specify a custom port
python manage.py runserver 8080
```

The API will be available at: `http://localhost:8000` (or your specified port)

---

## 🧪 Step 7: Testing

```powershell
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test authenication

# Run tests with verbose output
python manage.py test --verbosity=2
```

---

## 📝 Common Windows Commands

### Virtual Environment Management:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Check if virtual environment is active
echo $env:VIRTUAL_ENV
```

### Package Management:

```powershell
# Install new package
uv pip install package_name

# Install package and add to requirements
uv pip install package_name; uv pip freeze > requirements.txt

# Upgrade all packages
uv pip install --upgrade -r requirements.txt
```

### Django Management:

```powershell
# Create new Django app
python manage.py startapp app_name

# Make migrations for specific app
python manage.py makemigrations app_name

# Check migration status
python manage.py showmigrations

# Run Django shell
python manage.py shell
```

---

## 🐛 Troubleshooting

### Common Issues:

1. **PowerShell Execution Policy Error:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Port Already in Use:**
   ```powershell
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

3. **PostgreSQL Connection Issues:**
   - Ensure PostgreSQL service is running:
   ```powershell
   Get-Service postgresql*
   ```
   - Check if port 5432 is open:
   ```powershell
   netstat -an | findstr :5432
   ```

4. **Python Path Issues:**
   ```powershell
   # Check Python installation
   python --version
   
   # Check pip installation
   pip --version
   
   # Check uv installation
   uv --version
   ```

---

## 🔧 Environment Variables

Create a `.env` file in your project root with:

```env
# Database Configuration
DB_NAME=smart_access_db
DB_USER=smart_access_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📚 API Documentation

Once the server is running, you can access:

- **Admin Panel:** `http://localhost:8000/admin/`
- **API Root:** `http://localhost:8000/api/`
- **Authentication Endpoints:** `http://localhost:8000/api/auth/`

---

## 🚀 Production Deployment

For Windows Server deployment:

```powershell
# Install production dependencies
uv pip install gunicorn psycopg2-binary

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python manage.py test`
5. Commit changes: `git commit -m "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.
