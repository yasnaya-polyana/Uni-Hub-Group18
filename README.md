# Uni Hub - Campus Community Engagement Platform

Uni Hub is a web-based platform designed to enhance campus community engagement. Built with Django, this platform enables students to connect, join communities, manage events, and stay updated with campus activities.

## 🚀 Features

- **User Profiles**: Registration, authentication, and profile management
- **Communities**: Create and join interest-based communities
- **Event Management**: Create, modify, and manage campus events
- **Post System**: Share and filter posts within communities
- **Real-time Notifications**: Stay updated with community activities

## 🛠️ Tech Stack

- **Backend**: Python Django (MVT Architecture)
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Web Server**: Nginx
- **Development Tools**: VS Code

## 📋 Prerequisites

- Docker and Docker Compose
- Git

## 🔧 Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/uni-hub.git
   cd uni-hub
   ```

2. Create a `.env` file in the project root (replace with your values):
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   POSTGRES_DB=uni_hub_db
   POSTGRES_USER=uni_hub_user
   POSTGRES_PASSWORD=password123
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

 http://localhost:8000


## 👥 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Authors

Oscar Linehan 21015730
Write ur name here
