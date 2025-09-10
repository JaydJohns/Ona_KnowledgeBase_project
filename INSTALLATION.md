# Installation Guide

This guide provides detailed instructions for setting up the Second Brain Knowledge Repository on different platforms.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space minimum
- **Internet**: Required for initial setup and NLP model downloads

### Recommended Requirements
- **RAM**: 16GB for large document collections
- **Storage**: 10GB+ for extensive document libraries
- **CPU**: Multi-core processor for faster processing

## Installation Methods

### Method 1: Quick Setup (Recommended)

This method gets you up and running quickly with minimal configuration.

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/second-brain-knowledge-repository.git
   cd second-brain-knowledge-repository
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python -c "from app import create_app; app = create_app(); app.app_context().push(); from backend.models.document import db; db.create_all()"
   ```

5. **Start the Application**
   ```bash
   python app.py
   ```

6. **Access the Application**
   - API: http://localhost:5000
   - Test Interface: http://localhost:5000/static/test.html

### Method 2: Development Setup

For developers who want to modify the frontend or contribute to the project.

1. **Follow Quick Setup Steps 1-4**

2. **Install Node.js Dependencies**
   ```bash
   cd frontend
   npm install
   ```


3. **Start Backend Server**
   ```bash
   # In the root directory
   python app.py
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   # Create .env file:
   echo "REACT_APP_API_URL=http://localhost:5000/api" > .env
   npm start
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Method 3: Docker Setup

For containerized deployment and easy distribution.

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["python", "app.py"]
   ```

2. **Build and Run**
   ```bash
   docker build -t second-brain .
   docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads second-brain
   ```

## Platform-Specific Instructions

### Windows

1. **Install Python**
   - Download from https://python.org
   - Ensure "Add Python to PATH" is checked
   - Verify installation: `python --version`

2. **Install Git**
   - Download from https://git-scm.com
   - Use default installation options

3. **Install Visual C++ Build Tools** (if needed)
   - Download from Microsoft website
   - Required for some Python packages

4. **Follow Quick Setup Method**

### macOS

1. **Install Homebrew** (if not installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and Git**
   ```bash
   brew install python git
   ```

3. **Follow Quick Setup Method**

### Linux (Ubuntu/Debian)

1. **Update Package Manager**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Dependencies**
   ```bash
   sudo apt install python3 python3-pip python3-venv git
   ```

3. **Install Additional Libraries**
   ```bash
   sudo apt install python3-dev libmagic1
   ```

4. **Follow Quick Setup Method**

### Linux (CentOS/RHEL)

1. **Install Dependencies**
   ```bash
   sudo yum install python3 python3-pip git
   # or for newer versions
   sudo dnf install python3 python3-pip git
   ```

2. **Follow Quick Setup Method**

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///second_brain.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-very-secure-secret-key-here

# File Upload Settings
MAX_CONTENT_LENGTH=52428800  # 50MB in bytes
UPLOAD_FOLDER=uploads
PROCESSED_FOLDER=processed_docs

# Feature Flags
ENABLE_EMBEDDINGS=true
ENABLE_SPACY=false  # Set to true if spaCy is installed
ENABLE_ADVANCED_NLP=false

# API Settings
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=false

# Frontend Settings (for development)
REACT_APP_API_URL=http://localhost:5000/api
```

### Database Setup

#### SQLite (Default)
No additional setup required. Database file will be created automatically.

#### PostgreSQL (Production)

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows: Download from postgresql.org
   ```

2. **Create Database**
   ```sql
   sudo -u postgres psql
   CREATE DATABASE second_brain;
   CREATE USER second_brain_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE second_brain TO second_brain_user;
   \q
   ```

3. **Update Environment Variables**
   ```env
   DATABASE_URL=postgresql://second_brain_user:your_password@localhost/second_brain
   ```

4. **Install PostgreSQL Python Driver**
   ```bash
   pip install psycopg2-binary
   ```

### NLP Libraries (Optional)

For enhanced concept extraction:

1. **Install spaCy**
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```

2. **Install Sentence Transformers**
   ```bash
   pip install sentence-transformers
   ```

3. **Update Configuration**
   ```env
   ENABLE_SPACY=true
   ENABLE_EMBEDDINGS=true
   ```

## Verification

### Test Installation

1. **Check API Health**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Test Document Upload**
   ```bash
   curl -X POST -F "file=@sample_document.pdf" http://localhost:5000/api/documents/upload
   ```

3. **Test Search**
   ```bash
   curl "http://localhost:5000/api/search?q=test"
   ```

### Performance Test

1. **Upload Multiple Documents**
   - Test with various file sizes
   - Monitor processing time
   - Check memory usage

2. **Search Performance**
   - Test different query types
   - Measure response times
   - Verify result accuracy

## Troubleshooting

### Common Installation Issues

#### Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.9 -m venv venv
```

#### Permission Errors
```bash
# On Linux/macOS, use sudo for system-wide installation
sudo pip install -r requirements.txt

# Or use user installation
pip install --user -r requirements.txt
```

#### Package Installation Failures
```bash
# Update pip
pip install --upgrade pip

# Install packages individually
pip install Flask Flask-CORS Flask-SQLAlchemy

# Use conda instead of pip
conda install flask flask-cors flask-sqlalchemy
```

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process or use different port
export PORT=5001
python app.py
```

#### Database Connection Issues
```bash
# Check database file permissions
ls -la second_brain.db

# Reset database
rm second_brain.db
python -c "from app import create_app; app = create_app(); app.app_context().push(); from backend.models.document import db; db.create_all()"
```

### Performance Issues

#### Slow Document Processing
- Reduce file sizes before upload
- Disable advanced NLP features if not needed
- Use SSD storage for better I/O performance

#### High Memory Usage
- Limit concurrent uploads
- Process documents in batches
- Use PostgreSQL for large datasets

#### Slow Search
- Rebuild search indexes
- Limit result count
- Use more specific queries

## Security Considerations

### Production Deployment

1. **Change Default Secret Key**
   ```env
   SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
   ```

2. **Use HTTPS**
   - Configure reverse proxy (nginx/Apache)
   - Obtain SSL certificate
   - Redirect HTTP to HTTPS

3. **Database Security**
   - Use strong passwords
   - Limit database access
   - Enable connection encryption

4. **File Upload Security**
   - Validate file types
   - Scan for malware
   - Limit file sizes

### Network Security

1. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

2. **Access Control**
   - Implement authentication
   - Use API keys
   - Rate limiting

## Backup and Maintenance

### Database Backup

#### SQLite
```bash
# Backup
cp second_brain.db second_brain_backup_$(date +%Y%m%d).db

# Restore
cp second_brain_backup_20231201.db second_brain.db
```

#### PostgreSQL
```bash
# Backup
pg_dump second_brain > backup_$(date +%Y%m%d).sql

# Restore
psql second_brain < backup_20231201.sql
```

### File Backup
```bash
# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Backup processed documents
tar -czf processed_backup_$(date +%Y%m%d).tar.gz processed_docs/
```

### Regular Maintenance

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **Clean Temporary Files**
   ```bash
   # Remove temporary processing files
   find uploads/ -name "*.tmp" -delete
   
   # Clean old log files
   find logs/ -name "*.log" -mtime +30 -delete
   ```

3. **Optimize Database**
   ```sql
   -- SQLite
   VACUUM;
   ANALYZE;
   
   -- PostgreSQL
   VACUUM ANALYZE;
   ```

## Getting Help

If you encounter issues during installation:

1. **Check the logs** for error messages
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

4. **Join the community** for support and discussions

---

**Next Steps**: After successful installation, see the [Usage Guide](README.md#usage-guide) to start using the system.