# 🌱 GreenBridge

<div align="center">
  <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/django-4.2-green.svg" alt="Django">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker">
</div>

<div align="center">
  <h3>Connecting Brands, Recyclers, and Charities for a Sustainable Future</h3>
  <p>A comprehensive platform that bridges the gap between waste producers, recyclers, and charitable organizations</p>
</div>

---

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [🎯 Key Features](#-key-features)
- [🏗️ Project Architecture](#️-project-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation with Docker](#installation-with-docker)
  - [Manual Installation](#manual-installation)
- [🔧 Development](#-development)
  - [Environment Setup](#environment-setup)
  - [Database Configuration](#database-configuration)
  - [Running Tests](#running-tests)
- [📊 API Documentation](#-api-documentation)
- [🌍 Deployment](#-deployment)
- [🔒 Security Features](#-security-features)
- [🔌 Extensions & Integrations](#-extensions--integrations)
- [🧩 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [🔄 Project Roadmap](#-project-roadmap)
- [📜 License](#-license)
- [📞 Contact](#-contact)

## 🌟 Overview

GreenBridge is an innovative platform designed to revolutionize waste management by creating a sustainable ecosystem that connects key stakeholders: brands generating waste, recycling facilities processing materials, and charitable organizations benefiting from reclaimed resources.

The platform employs advanced geospatial tracking, comprehensive material management, and role-specific functionalities to streamline the entire waste management lifecycle - from collection and sorting to recycling and repurposing.

## 🎯 Key Features

- **🔄 Multi-stakeholder Ecosystem**: Seamlessly connects brands, recyclers, charities, and consumers with tailored interfaces
- **🗺️ Advanced Geospatial Services**: Real-time tracking of collection routes, service areas, and dropoff points
- **📊 Comprehensive Material Management**: Detailed categorization, tracking, and analytics for all waste materials
- **📱 Responsive Web Interface**: Modern, mobile-friendly design using HTMX and Alpine.js
- **🔄 Complete RESTful API**: Well-documented endpoints for integration with external systems
- **📈 Real-time Analytics**: Customizable dashboards providing insights into waste management performance
- **🔐 Role-based Access Control**: Secure, permission-based access to features and data
- **📡 Real-time Communications**: WebSocket integration for live updates and notifications
- **🌐 Geospatial Optimization**: Route planning and optimization for efficient waste collection
- **📦 Batch Processing**: Streamlined handling of recycling processes with detailed tracking

## 🏗️ Project Architecture

GreenBridge follows a modular architecture designed for scalability and maintainability:

![Architecture Diagram](https://via.placeholder.com/800x400?text=GreenBridge+Architecture+Diagram)

- **Client Layer**: Web browsers, mobile devices, API consumers
- **Presentation Layer**: Django templates, HTMX, Alpine.js, DRF API endpoints
- **Application Layer**: Django views, services, serializers
- **Domain Layer**: Core business logic and models
- **Infrastructure Layer**: Database adapters, caching, external services
- **Data Storage**: PostgreSQL with PostGIS, Redis, file storage

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2.10 with Django REST Framework 3.14.0
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Caching**: Redis 5.0+
- **Task Queue**: Celery 5.3.6 with Redis broker
- **Asynchronous**: Django Channels with ASGI
- **Search**: PostgreSQL full-text search, vector database integration

### Frontend
- **Templates**: Django Templates
- **Interactive UI**: HTMX for AJAX, Alpine.js for interactivity
- **Styling**: TailwindCSS with custom components
- **Maps**: Leaflet.js with OpenStreetMap/Google Maps

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Monitoring**: Prometheus & Grafana
- **CI/CD**: GitHub Actions
- **Storage**: AWS S3 compatible storage (optional)

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- Git
- PostgreSQL with PostGIS extension (for local development without Docker)
- Python 3.10+ (for local development without Docker)

### Installation with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/Danchouvzv/greenbridge.git
   cd greenbridge
   ```

2. **Create environment variables file**
   ```bash
   cp .env.example .env
   # Edit the .env file with your configuration
   ```

3. **Build and start the containers**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations and create superuser**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/docs

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Danchouvzv/greenbridge.git
   cd greenbridge
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   
   Create a PostgreSQL database with PostGIS extension and update `greenbridge/settings/local.py` with your database settings.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Development

### Environment Setup

The project uses a multi-environment settings structure:

- `base.py`: Common settings for all environments
- `development.py`: Development-specific settings
- `production.py`: Production-specific settings 
- `local.py`: Local overrides (not tracked in git)

Create a `local.py` file to override settings for your development environment:

```python
from .development import *

# Override settings for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'greenbridge',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Database Configuration

#### Setting up PostGIS

For GeoDjango functionality, you'll need PostgreSQL with the PostGIS extension:

**macOS (with Homebrew)**:
```bash
brew install postgresql postgis gdal
brew services start postgresql
psql postgres -c "CREATE DATABASE greenbridge;"
psql greenbridge -c "CREATE EXTENSION postgis;"
```

**Ubuntu/Debian**:
```bash
sudo apt install postgresql postgresql-contrib postgis gdal-bin
sudo -u postgres psql -c "CREATE DATABASE greenbridge;"
sudo -u postgres psql -c "CREATE USER greenbridge WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE greenbridge TO greenbridge;"
sudo -u postgres psql -d greenbridge -c "CREATE EXTENSION postgis;"
```

**Windows**:
Use the [OSGeo4W installer](https://trac.osgeo.org/osgeo4w/) which bundles PostgreSQL, PostGIS and GDAL.

### Running Tests

The project includes comprehensive tests for all main components:

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test greenbridge.waste

# Run with coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # For detailed HTML report
```

## 📊 API Documentation

GreenBridge provides comprehensive API documentation through Swagger UI:

- **Development**: http://localhost:8000/docs/
- **Production**: https://your-domain.com/docs/

The API follows RESTful principles and uses JWT for authentication:

### Authentication

```bash
# Obtain token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"your_password"}'

# Use token
curl -X GET http://localhost:8000/waste/api/materials/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLC..."
```

### Key API Endpoints

- **Authentication**: `/api/token/`, `/api/token/refresh/`
- **User Management**: `/accounts/api/users/`, `/accounts/api/profile/`
- **Waste Management**: `/waste/api/collections/`, `/waste/api/materials/`
- **Geospatial**: `/geo/api/locations/`, `/geo/api/routes/`

## 🌍 Deployment

### Production Deployment with Docker

1. **Configure production environment**
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod with production settings
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Apply migrations and collect static files**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic --no-input
   ```

### Cloud Deployment Options

The platform can be deployed to various cloud providers:

- **AWS**: Using ECS with Fargate, RDS for PostgreSQL, ElastiCache for Redis
- **Google Cloud**: Using GKE, Cloud SQL, Memorystore
- **Azure**: Using AKS, Azure Database for PostgreSQL, Azure Cache for Redis
- **Digital Ocean**: Using Kubernetes or Droplets with managed databases

## 🔒 Security Features

GreenBridge implements comprehensive security measures:

- **Authentication**: JWT-based authentication with token refresh
- **Authorization**: Fine-grained permission system for object-level access control
- **Data Protection**: PII encryption for sensitive data
- **API Security**: Rate limiting, CORS protection, CSRF protection
- **Content Security**: CSP headers to prevent XSS attacks
- **Database**: Parameterized queries to prevent SQL injection
- **Validation**: Strict input validation for all user inputs
- **Auditing**: Comprehensive audit logging for sensitive operations
- **HTTPS**: Enforced SSL/TLS for all communications in production

## 🔌 Extensions & Integrations

GreenBridge is designed to integrate with various external services:

- **Payment Gateways**: Stripe, PayPal
- **Email Services**: SendGrid, Mailgun
- **SMS Services**: Twilio
- **Maps & Geocoding**: Google Maps, OpenStreetMap
- **Analytics**: Google Analytics, Matomo
- **File Storage**: AWS S3, Google Cloud Storage
- **AI & ML**: OpenAI, TensorFlow

## 🧩 Project Structure

Detailed structure of the GreenBridge codebase:

```
greenbridge/
├── accounts/             # User authentication & profiles
│   ├── api/              # API endpoints for account management
│   ├── migrations/       # Database migrations
│   ├── models.py         # User and profile models
│   └── ...
├── waste/                # Waste management functionality
│   ├── api/              # API endpoints for waste operations
│   ├── migrations/       # Database migrations 
│   ├── models.py         # Waste, material, collection models
│   └── ...
├── geospatial/           # Location-based services
│   ├── api/              # API endpoints for geospatial data
│   ├── migrations/       # Database migrations
│   ├── models.py         # Location, route, service area models
│   └── ...
├── utils/                # Shared utilities
│   ├── management/       # Custom management commands
│   ├── middleware.py     # Custom middleware
│   ├── permissions.py    # Custom permissions
│   └── ...
├── templates/            # HTML templates
│   ├── index.html        # Homepage template
│   ├── swagger-ui.html   # API documentation
│   └── ...
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Image assets
├── media/                # User-uploaded content
├── greenbridge/          # Project configuration
│   ├── settings/         # Settings for different environments
│   ├── urls.py           # URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── docker/               # Docker configuration files
├── .github/              # GitHub Actions CI/CD
├── requirements.txt      # Python dependencies
└── manage.py             # Django management script
```

## 🤝 Contributing

We welcome contributions to GreenBridge! Here's how you can help:

1. **Fork the repository**
   ```bash
   git clone https://github.com/Danchouvzv/greenbridge.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Write tests for new functionality
   - Update documentation as needed

4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Provide a clear description of the changes
   - Link any related issues

## 🔄 Project Roadmap

- **Q2 2023**
  - Core waste management functionality
  - Basic geospatial services
  - User authentication and roles

- **Q3 2023**
  - Advanced route optimization
  - Mobile-optimized interfaces
  - Reporting and analytics

- **Q4 2023**
  - AI-powered waste classification
  - Blockchain integration for material tracking
  - Public API for third-party integration

- **Q1 2024**
  - Marketplace for recycled materials
  - Carbon footprint calculation
  - Advanced analytics dashboard

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Project Link: [https://github.com/Danchouvzv/greenbridge](https://github.com/Danchouvzv/greenbridge)

---

<div align="center">
  <p>Made with ❤️ for a sustainable future</p>
  
  <a href="#-greenbridge">Back to top ⬆️</a>
</div> 