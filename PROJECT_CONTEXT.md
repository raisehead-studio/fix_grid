# Fix Grid - Kaohsiung City Utility Outage Management System

## Project Overview

**Fix Grid** is a **Flask-based web application** designed for **emergency management and utility outage reporting** in Kaohsiung City, Taiwan. It's a comprehensive system for managing power outages, water outages, and disaster reports with role-based access control.

## Core Architecture

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite (`kao_power_water.db`)
- **Frontend**: HTML templates with JavaScript
- **Authentication**: Flask-Login with role-based permissions
- **Deployment**: Docker with Nginx reverse proxy
- **Data Processing**: Excel export functionality using openpyxl

### Application Structure
```
fix_grid/
├── app/                    # Main Flask application
│   ├── __init__.py        # App factory and core routes
│   ├── models.py          # Database models and queries
│   ├── routes/            # Blueprint modules
│   ├── templates/         # HTML templates
│   └── static/           # JavaScript and static files
├── db/                    # SQL initialization scripts
├── districts/            # Geographic data for Kaohsiung
└── Docker configuration
```

## Key Features

### 1. **Role-Based Access Control System**
- **7 User Roles**: 超級管理員, 管理員, 民政局幹事, 里幹事, 台電人員, 台水人員, 上級長官
- **Permission-based access** to different pages and functions
- **Password security** with 90-day expiration policy

### 2. **Power Outage Management**
- **Report Creation**: Users can create power outage reports
- **Status Tracking**: Track restoration status and Taipower support
- **Geographic Data**: Reports linked to districts and villages
- **Excel Export**: Generate comprehensive reports with charts

### 3. **Water Outage Management**
- **Water Station Reports**: Track water supply issues
- **Taiwater Integration**: Status updates from Taiwan Water Corporation
- **Contact Information**: Store affected area contact details

### 4. **Disaster Management**
- **Emergency Reports**: Handle various disaster scenarios
- **Multi-utility Support**: Coordinate power and water issues
- **Real-time Updates**: Status tracking and restoration estimates

### 5. **Geographic Coverage**
- **38 Districts**: Complete coverage of Kaohsiung City
- **Village-level Data**: Detailed geographic breakdown
- **Regional Filtering**: Reports filtered by user's assigned area

## Database Schema

### Core Tables
- **users**: User accounts with role and geographic assignments
- **roles**: User role definitions
- **permissions**: Page and function permissions
- **role_permissions**: Role-permission mappings
- **districts**: Kaohsiung's 38 administrative districts
- **villages**: Sub-district administrative units

### Report Tables
- **power_reports**: Power outage incident reports
- **water_reports**: Water supply issue reports
- **taiwater_power_reports**: Cross-utility coordination
- **user_login_logs**: Authentication tracking

## API Endpoints

### Authentication & User Management
- `/` - Login page
- `/dashboard` - Main dashboard
- `/profile` - User profile management
- `/api/accounts` - User account management

### Report Management
- `/api/power_reports` - Power outage CRUD operations
- `/api/water_reports` - Water outage CRUD operations
- `/api/taipower_reports` - Taipower coordination
- `/api/taiwater_reports` - Taiwan Water coordination

### Data Export
- `/api/export-excel` - Excel report generation
- `/api/power_stats` - Power outage statistics
- `/api/water_stats` - Water outage statistics

## Security Features

### Password Policy
- **Minimum 12 characters**
- **Complexity requirements**: Uppercase, lowercase, numbers, special characters
- **90-day expiration** with forced password change
- **Login tracking** with IP logging

### Access Control
- **Route protection** with `@login_required`
- **Permission validation** before page access
- **Role-based data filtering** (e.g., 里幹事 can only see their village reports)

## Deployment Configuration

### Docker Setup
- **Multi-container**: Flask app + Nginx proxy
- **Volume mounting**: For development and data persistence
- **Port mapping**: 80:80 for web access

### Environment Configuration
- **Development mode** with debug enabled
- **Environment variables** for port configuration
- **Database initialization** on container startup

## Geographic Data

The system includes complete geographic data for Kaohsiung City:
- **38 districts** with individual village listings
- **Hierarchical structure**: District → Village
- **Chinese naming** with proper administrative divisions

## Business Logic

### Report Workflow
1. **Report Creation**: Users create outage reports
2. **Status Updates**: Track restoration progress
3. **Utility Coordination**: Integrate with Taipower/Taiwater
4. **Resolution Tracking**: Monitor until complete restoration
5. **Data Export**: Generate reports for analysis

### User Experience
- **Responsive interface** with modern UI
- **Real-time updates** via JavaScript
- **Excel integration** for data export
- **Mobile-friendly** design

## Installation & Setup

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run application
python app.py
```

### Docker Deployment
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f
```

## Project Characteristics

This is a **production-ready emergency management system** specifically designed for Kaohsiung City's utility infrastructure, with:
- Complete role-based access control
- Geographic data management
- Multi-utility coordination capabilities
- Real-time status tracking
- Comprehensive report generation

## Technical Details

### Dependencies
- Flask: Web framework
- Flask-Login: User authentication
- Flask-WTF: Form handling
- openpyxl: Excel file processing
- python-dotenv: Environment variable management

### Database
- SQLite as primary database
- Automatic initialization scripts
- Backup and recovery mechanisms

### Frontend
- Vanilla JavaScript
- Responsive HTML/CSS
- Real-time data updates
- Interactive charts

## File Structure Analysis

### Core Application Files
- `app.py`: Main application entry point
- `app/__init__.py`: Flask app factory and core configuration
- `app/models.py`: Database models and query functions
- `requirements.txt`: Python dependencies

### Route Modules
- `app/power_routes.py`: Power outage management (444 lines)
- `app/water_routes.py`: Water outage management (186 lines)
- `app/account_routes.py`: User account management (217 lines)
- `app/role_routes.py`: Role and permission management
- `app/taiwater_power_routes.py`: Cross-utility coordination
- `app/disaster_routes.py`: Disaster management

### Database & Initialization
- `init_db.py`: Database schema creation
- `init_permissions.py`: Permission system setup
- `init_districts.py`: Geographic data initialization
- `db/`: SQL scripts for data management

### Deployment
- `docker-compose.yml`: Multi-container orchestration
- `Dockerfile`: Flask application container
- `nginx/`: Reverse proxy configuration

### Geographic Data
- `districts/`: Complete Kaohsiung administrative data
- 38 district files with village listings
- Hierarchical geographic structure

## Security Implementation

### Authentication Flow
1. User login with username/password
2. Password validation against hash
3. Role-based permission checking
4. Session management with Flask-Login
5. IP logging for security audit

### Data Protection
- SQL injection prevention with parameterized queries
- XSS protection through template escaping
- CSRF protection with Flask-WTF
- Input validation and sanitization

## Performance Considerations

### Database Optimization
- Indexed foreign keys for joins
- Connection pooling with timeout settings
- Efficient query patterns for large datasets
- Regular database maintenance scripts

### Frontend Performance
- Minified JavaScript files
- Optimized image assets
- Efficient DOM manipulation
- Responsive design for mobile devices

---

**Version**: 1.0.0  
**Maintainer**: Kaohsiung City Government  
**License**: Internal Use Only  
**Last Updated**: 2024 