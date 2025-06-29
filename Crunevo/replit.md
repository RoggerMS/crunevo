# CRUNEVO - Educational Social Platform

## Overview

CRUNEVO is a social educational platform designed for university students in Latin America. The platform allows students to share academic notes, connect with peers, participate in discussions, earn virtual currency (Crolars), and build their academic identity. Built with Flask, it features a modern interface with dark mode support and gamification elements.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Authentication**: Flask-Login with session management
- **File Storage**: Cloudinary integration for document and image uploads
- **Security**: CSRF protection, password hashing with Werkzeug, ProxyFix middleware

### Frontend Architecture
- **Styling**: Tailwind CSS with custom theme variables
- **Icons**: Feather Icons
- **JavaScript**: Vanilla JS with modular approach
- **Templates**: Jinja2 templating engine
- **Responsive Design**: Mobile-first approach with dark mode support

### Key Components

1. **User Management System**
   - User registration/login with form validation
   - Profile management with career and university information
   - Avatar system with initials-based fallback
   - Virtual currency (Crolars) and points system

2. **Content Management**
   - Note/document upload system with Cloudinary integration
   - Social feed for posts and discussions
   - Forum functionality for Q&A and discussions
   - Comment system for user interactions

3. **Gamification System**
   - Crolars (virtual currency) reward system
   - Achievement tracking
   - Mission system for daily challenges
   - User level progression

4. **Communication Features**
   - Direct messaging system between users
   - Post interactions (likes, comments)
   - User profiles with academic information

5. **Marketplace Integration**
   - Virtual marketplace for educational resources
   - Crolars-based transactions
   - Item categorization system

## Data Flow

1. **User Registration Flow**
   - Form validation → User creation → Welcome Crolars award → Auto-login → Redirect to feed

2. **Content Upload Flow**
   - File selection → Cloudinary upload → Database record creation → Crolars reward → Feed publication

3. **Social Interaction Flow**
   - User action → Database update → Crolars/points calculation → Achievement check → Notification

## External Dependencies

### Required Services
- **Cloudinary**: File storage and CDN for documents and images
- **PostgreSQL**: Primary database for all application data

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session encryption key
- `CLOUDINARY_CLOUD_NAME`: Cloudinary account identifier
- `CLOUDINARY_API_KEY`: Cloudinary API authentication
- `CLOUDINARY_API_SECRET`: Cloudinary API secret

### Frontend Libraries
- **Tailwind CSS**: Utility-first CSS framework (CDN)
- **Feather Icons**: Icon library (CDN)

## Deployment Strategy

### Current Setup
- **Platform**: Configured for Fly.io deployment
- **WSGI**: Flask application with ProxyFix middleware
- **Database**: PostgreSQL with connection pooling (pool_recycle: 300s, pool_pre_ping: True)
- **Static Files**: Served through Flask with Cloudinary for uploads

### Production Considerations
- Database connection pooling configured for cloud deployment
- Environment-based configuration management
- HTTPS proxy handling with ProxyFix
- Session management with secure secrets

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 29, 2025. Initial setup