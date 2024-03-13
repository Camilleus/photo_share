# PhotoShare REST API

Welcome to PhotoShare - a REST API project built using FastAPI.

## Introduction

PhotoShare is a versatile REST API application designed to facilitate photo sharing and commenting among users. Leveraging the power of FastAPI, it provides robust functionality for managing images, adding comments, and ensuring secure user authentication.

## Technologies we use

Python, Poetry, Postgres, SQLAlchemy, Alembic, Redis

## Features

- JWT token-based authentication.
- Supports three user roles: standard user, moderator, and administrator.
- The first user registered is always assigned the administrator role.
- Users can upload photos with descriptions.
- Users can delete their uploaded photos.
- Users can edit photo descriptions.
- Users can retrieve photos using a unique link.
- Ability to add up to 5 tags per photo and optional Tags.
- Users can generate links for transformed images to display as URLs and QR codes.
- Users can comment on photos uploaded by other users.
- Users can edit their comments but cannot delete them.
- Moderators and administrators have the privilege to delete comments.
- Comments are stored in the database with creation and update timestamps.
- Route to a user's profile based on their unique username.
- You can edit your information and view information about yourself.
- The administrator can deactivate (ban) users.
- The user can search for photos by keywords or tags. After searching, the user can filter the results by rating or date added.
- Moderators and administrators can search and filter by users who have added photos.

## PhotoShare Application Setup Guide

This guide will walk you through the steps required to set up and run the PhotoShare application. 
You can choose to set up the application manually or use Docker for containerization.

### Prerequisites

Before you begin, make sure you have the following installed on your system:

- Git
- Python 3.11 or later
- pip (Python package manager)
- Docker (for Docker setup)

### Manual Setup

#### Clone the Repository

Clone the PhotoShare repository to your local machine using the following command:
```bash
git clone https://github.com/yourusername/photoshare.git`
```

#### Install Dependencies
Navigate to the cloned repository's directory and install the required dependencies using pip:

```bash
cd photoshare
pip install -r requirements.txt
```

#### Set Up Environment Variables

You need to set up environment variables for the database connection, Cloudinary API, and JWT secret key. This can be done by creating a `.env` file in the root directory of the project and populating it with the necessary values:

```
SECRET_NAME=your_secret_name
REGION_NAME=your_region_name
AWS_ACCESS_KEY_ID=aws_access_key
AWS_SECRET_ACCESS_KEY=aws_secret_key
```

#### Run the Application

Run the PhotoShare application using uvicorn with the following command:

```bash
uvicorn main:app --host localhost --port 8000 --reload
```

The application will be accessible at `http://localhost:8000`

### Docker Setup

#### Build the Docker Image

You can also run the PhotoShare application using Docker. First, build the Docker image using the following command:

```bash
sudo docker build -t photo-share .
```

This command builds a Docker image named `photo-share` based on the instructions in the `Dockerfile`.

#### Run the Container

Once the image is built, you can run the application inside a Docker container using the following command:

```bash
sudo docker run -dp 80:80 photo-share
```

This command runs the `photo-share` image in a detached mode (`-d`) and maps port 80 of the container to port 80 
on the host machine (`-p 80:80`), making the application accessible at `http://localhost`.

### Conclusion

You can now access the PhotoShare application either through your local setup at 
`http://localhost:8000` or through Docker at `http://localhost`. Enjoy sharing photos with PhotoShare!


## Usage

- Register an account and obtain JWT token for authentication.
- Explore endpoints for uploading, managing, and commenting on photos.
- Utilize Cloudinary transformations for image operations.
- Leverage QR code generation for sharing transformed images.
- Administrators can perform CRUD operations on user photos and comments.

## TODO

In future we will deploy this project somewhere in order to make it more avialable to a typical user of internet

## Contributing

Contributions are welcome! Please follow the Contribution Guidelines.

## License

This project should be licensed under the MIT License.

## Project Structure

```
photo_share
├─ .gitignore
├─ alembic
│  ├─ env.py
│  ├─ README
│  ├─ script.py.mako
│  └─ versions
│     └─ not your problem :D
├─ alembic.ini
├─ main.py
├─ poetry.lock
├─ pyproject.toml
├─ README.md
├─ src
│  ├─ conf
│  │  ├─ config.py
│  │  └─ __init__.py
│  ├─ database
│  │  ├─ db.py
│  │  ├─ models.py
│  │  └─ __init__.py
│  ├─ repository
│  │  ├─ comments.py
│  │  ├─ messages.py
│  │  ├─ pictures.py
│  │  ├─ pictures_oktawian.py
│  │  ├─ tags.py
│  │  ├─ users.py
│  │  └─ __init__.py
│  ├─ routes
│  │  ├─ auth.py
│  │  ├─ comments.py
│  │  ├─ messages.py
│  │  ├─ pictures.py
│  │  ├─ pictures_oktawian.py
│  │  ├─ search.py
│  │  ├─ tags.py
│  │  ├─ users.py
│  │  ├─ users_role.py
│  │  └─ __init__.py
│  ├─ schemas.py
│  ├─ services
│  │  ├─ auth.py
│  │  ├─ auth_admin.py
│  │  ├─ auth_moderator.py
│  │  ├─ email.py
│  │  ├─ secrets_manager.py
│  │  ├─ templates
│  │  │  ├─ email_verification_template.html
│  │  │  ├─ password_reset_template.html
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ static
│  │  ├─ modern-normalize-min.css
│  │  └─ styles.css
│  ├─ tests
│  │  ├─ conftest.py
│  │  ├─ test_access_required.py
│  │  ├─ test_repository_tags.py
│  │  ├─ test_routes_auth.py
│  │  ├─ test_routes_messages.py
│  │  ├─ test_routes_pictures.py
│  │  ├─ test_routes_search.py
│  │  ├─ test_routes_users.py
│  │  ├─ test_unit_repository_comments.py
│  │  ├─ test_unit_repository_pictures.py
│  │  ├─ test_unit_repository_pictures_oktawian.py
│  │  ├─ test_unit_repository_user.py
│  │  ├─ test_user_validate.py
│  │  └─ __init__.py
│  └─ __init__.py
└─ templates
   ├─ base.html
   ├─ index.html
   ├─ pictures.html
   ├─ resetPassword.js
   ├─ reset_password.html
   ├─ users.html
   ├─ user_details.html
   └─ __init__.py
```
