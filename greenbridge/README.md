# GreenBridge - Sustainable Waste Management Platform

GreenBridge is a comprehensive platform connecting brands, recyclers, and charities to create a sustainable ecosystem for waste management.

## Overview

The GreenBridge platform features:

- **Multi-role Support**: Tailored interfaces for brands, recyclers, charities, and consumers
- **Geospatial Services**: Location-based waste collection and recycling facility management
- **Material Tracking**: Comprehensive categorization and tracking of waste materials
- **Mobile-Friendly Interface**: Using HTMX and Alpine.js for responsive behavior
- **REST API**: Complete API for integration with external systems
- **Analytics Dashboard**: Insights into waste management performance

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, PostGIS
- **Frontend**: Django Templates with HTMX, Alpine.js, TailwindCSS
- **Database**: PostgreSQL with PostGIS extension
- **Cache & Queue**: Redis, Celery
- **Deployment**: Docker, Docker Compose, Nginx

## Project Structure

```
greenbridge/
├── accounts/          # User management and authentication
├── waste/             # Waste management and tracking
├── geospatial/        # Location-based services and maps
├── utils/             # Shared utilities
├── templates/         # HTML templates
├── static/            # Static assets (CSS, JS, images)
├── media/             # User-uploaded content
└── greenbridge/       # Project configuration
    ├── settings/      # Settings for different environments
    ├── urls.py        # URL routing configuration
    ├── wsgi.py        # WSGI application entry point
    └── asgi.py        # ASGI application entry point
```

## Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/greenbridge.git
   cd greenbridge
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

4. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Access the application at http://localhost:8000

## Development

### Running Locally without Docker

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Database Setup for GeoDjango

For GeoDjango functionality, you'll need PostGIS:

#### macOS
```bash
brew install postgresql postgis gdal
```

#### Ubuntu
```bash
sudo apt install postgresql postgresql-contrib postgis gdal-bin
```

#### Windows
Use the OSGeo4W installer from https://trac.osgeo.org/osgeo4w/

## API Documentation

API documentation is available at `/docs/` when the server is running.

## Testing

Run the test suite:

```bash
python manage.py test
```

## Deployment

The project is configured for deployment with Docker Compose:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - your.email@example.com

Project Link: https://github.com/yourusername/greenbridge 