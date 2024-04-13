# 🤳🏼 PhotoShare

Welcome to PhotoShare - a REST API project built using FastAPI by The Magnificient 7 Team

## 🌟 Introduction

There are 10 kinds of people in the world. Those who understand binary and those who don’t. 😺
PhotoShare is a versatile REST API application designed to facilitate photo sharing and commenting among users. Extremely leveraging the power of FastAPI, it provides robust functionality for managing images, adding comments, and ensuring secure user authentication.

## 🔧 Technologies we use

- 🐍 Python
- ☁️ AWS
- 🐳 Docker
- ☁️ Cloudinary
- 🐘 RDS
- 🐘 Postgres
- 🐘 SQLAlchemy
- 🐘 Alembic
- 🔄 Redis
- 📚 Poetry
- 📧 MailGun

## 🔐 Registration and Authentication

During the registration process, users are required to confirm their email address by clicking on the activation link sent to the provided email. The login mechanism is secured using JWT pairs, comprising an access token and a refresh token. This ensures a secure and authenticated experience for users.

## 🚀 Features

- JWT token-based authentication with user roles.
- User actions: upload, delete, and edit photos with descriptions.
- Unique links for retrieving and transforming photos.
- Ability to add up to 5 tags per photo.
- Commenting system with edit capabilities.
- Moderators and administrators can delete comments.
- User profiles with editable information.
- Administrator can deactivate (ban) users.
- Search functionalities for photos, users, and special one for moderators/administrators only.
- Timestamps for photos and comments.

## 🛠️ PhotoShare Application Setup Guide

This guide will walk you through the steps required to set up and run the PhotoShare application.
You can choose to set up the application manually or use Docker for containerization.

## 📝 Manual Setup

### Prerequisites

Before you begin, make sure you have the following installed on your system:

- Git
- Python 3.11 or later
- pip and poetry (Python package manager)
- Docker (for Docker setup)
- You should you should be acquainted with these websites: aws.amazon.com/rds, docker.com, cloudinary.com, redis.io

### How We Are Doing it?

- We use AWS EC2 - a virtual machine on which the project runs in Docker
- we use secret-manager to keep all variables in our code
- We create users on IAM - Identity and Access Management (IAM) on AWS

#### Clone the Repository

Clone the PhotoShare repository to your local machine using the following command:

```bash
git clone https://github.com/sebastianLedzianowski/photo_share`
```

#### Install Dependencies

Navigate to the cloned repository's directory and install the required dependencies using poetry:

```bash
cd photoshare
poetry update
```

or you can use our requirements.txt

```bash
pip install -r requirements.txt

```

#### Set Up Environment Variables

You need to set up environment variables for the database connection, Cloudinary API, and JWT secret key. This can be done by creating a `.env` file in the root directory of the project and populating it with the necessary values:

```bash
SECRET_NAME=your_secret_name
REGION_NAME=your_region_name
AWS_ACCESS_KEY_ID=aws_access_key
AWS_SECRET_ACCESS_KEY=aws_secret_key
```

Additionally here are the environment variables for secret manager:

```bash
SQLALCHEMY_DATABASE_URL - Used to connect to your SQLAlchemy Database
SECRET_KEY - Key Used to connect to your SQLAlchemy Database
ALGORITHM - Script used to download Environment variables
REDIS_HOST - Redis DB variable
REDIS_PORT - Redis DB variable
REDIS_PASSWORD - Redis DB variable
CLOUDINARY_NAME - API of Cloudinary
CLOUDINARY_API_KEY - API of Cloudinary
CLOUDINARY_API_SECRET - API of Cloudinary
MAILGUN_API_KEY - API used to send emails (mailgun.com)
MAILGUN_DOMAIN - API used to send emails (mailgun.com)
```

**Note:** Ensure to keep your `.env` file secure and never commit it to the repository to protect sensitive information.

#### Run the Application

Run the PhotoShare application using uvicorn with the following command:

```bash
uvicorn main:app --host localhost --port 8000 --reload
```

The application will be accessible at `http://localhost:8000`

### 🐳 Docker Setup

#### Build the Docker Image

You can also run the PhotoShare application using Docker. First, build the Docker image using the following command:

```bash
docker build -t photo-share .
```

This command builds a Docker image named `photo-share` based on the instructions in the `Dockerfile`.

#### Run the Container

Once the image is built, you can run the application inside a Docker container using the following command:

```bash
docker run -dp 80:80 photo-share
```

This command runs the `photo-share` image in a detached mode (`-d`) and maps port 80 of the container to port 80
on the host machine (`-p 80:80`), making the application accessible at `http://localhost`.

### Docker Compose Integration (Optional)

If you prefer to use Docker Compose, you can also run the application using the provided docker-compose.yaml file. Simply run:

```bash
docker-compose up -d
```

This command starts the application defined in the docker-compose.yaml file, running in detached mode (-d).

Environment Variables
The docker-compose.yaml file sets the ENVIRONMENT environment variable to development. This variable can be used within the application if needed.

### Conclusion

You can now access the PhotoShare application either through your local setup at
`http://localhost:8000` or through Docker at `http://localhost`. Enjoy sharing photos with PhotoShare!

## 💡 Usage

- Register an account and obtain JWT token for authentication.
- Explore endpoints for uploading, managing, and commenting on photos.
- Utilize Cloudinary transformations for image operations.
- Leverage QR code generation for sharing transformed images.
- Administrators can perform CRUD operations on user photos and comments.

## 🧑🏻‍🤝‍🧑🏽 Creators

- [Project Manager - Sebastian Ledzianowski](https://github.com/sebastianLedzianowski)
- [Scrum Master - Kamil "Camilleus" Truszkowski](https://github.com/Camilleus)
- [Developer - Oktawian Czakiert](https://github.com/OktawianCzakiert)
- [Developer - Tomasz Heese](https://github.com/Heesej)
- [Developer - Bartek Goźliński](https://github.com/bgozlinski)
- [Developer - Julia](https://github.com/julotec)
- [Developer - Krzysztof Kazimierczak](https://github.com/KrzysztofKazimierczak)

## 🤝 Contributing

Contributions are welcome! Please follow the Commonly Recognized Contribution Guidelines 😺

## 📄 License

This project should be licensed under the MIT License.

## 🧪 Testing

```bash
Name                                                        Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------------------
main.py                                                        31      3    90%   49-56, 59
src/__init__.py                                                 0      0   100%
src/conf/__init__.py                                            0      0   100%
src/conf/cloudinary.py                                         13      0   100%
src/database/__init__.py                                        0      0   100%
src/database/db.py                                             11      4    64%   22-26
src/database/models.py                                         91      1    99%   79
src/repository/__init__.py                                      0      0   100%
src/repository/comments.py                                     28      0   100%
src/repository/descriptions.py                                 26      0   100%
src/repository/messages.py                                     13      7    46%   30-36, 59-62
src/repository/pictures.py                                     83      4    95%   211, 215-217
src/repository/rating.py                                       35      1    97%   68
src/repository/reactions.py                                    62      5    92%   23-24, 47, 49, 104
src/repository/search.py                                       24      9    62%   45, 48, 65-82
src/repository/tags.py                                         30      1    97%   56
src/repository/users.py                                        58     12    79%   63-66, 111, 138-146
src/routes/__init__.py                                          0      0   100%
src/routes/auth.py                                             98      2    98%   73, 201
src/routes/comments.py                                         36      0   100%
src/routes/descriptions.py                                     48      0   100%
src/routes/main_router.py                                       0      0   100%
src/routes/messages.py                                         20      6    70%   38-46, 70-71
src/routes/pictures.py                                         77      2    97%   225, 228
src/routes/rating.py                                           31      1    97%   75
src/routes/reactions.py                                        22      0   100%
src/routes/search.py                                           11      1    91%   36
src/routes/tags.py                                             13      1    92%   39
src/routes/users.py                                            59     14    76%   124-128, 145-152, 171, 191-192
src/schemas.py                                                137      0   100%
src/services/__init__.py                                        0      0   100%
src/services/auth.py                                          114     26    77%   100, 120, 145-147, 181, 184-187, 196, 202, 208-214, 253, 258, 301-307
src/services/auth_roles.py                                     19      9    53%   19-27, 33-36
src/services/email.py                                          21      0   100%
src/services/qr.py                                             31      2    94%   39-40
src/services/secrets_manager.py                                33      5    85%   57-61
src/tests/__init__.py                                           0      0   100%
src/tests/conftest.py                                         147      2    99%   173, 186
src/tests/repository/__init__.py                                0      0   100%
src/tests/repository/test_repository_tags.py                   59      0   100%
src/tests/repository/test_unit_repository_comments.py          55      0   100%
src/tests/repository/test_unit_repository_descriptions.py      63      0   100%
src/tests/repository/test_unit_repository_pictures.py         148      0   100%
src/tests/repository/test_unit_repository_reactions.py         47      0   100%
src/tests/repository/test_unit_repository_user.py              60      0   100%
src/tests/routes/__init__.py                                    0      0   100%
src/tests/routes/test_routes_auth.py                          151      0   100%
src/tests/routes/test_routes_comments.py                       76      0   100%
src/tests/routes/test_routes_descriptions.py                  168      0   100%
src/tests/routes/test_routes_messages.py                       11      0   100%
src/tests/routes/test_routes_pictures.py                      178      0   100%
src/tests/routes/test_routes_rating.py                         41      0   100%
src/tests/routes/test_routes_reactions.py                      33      0   100%
src/tests/routes/test_routes_search.py                         13      0   100%
src/tests/routes/test_routes_tags.py                           25      0   100%
src/tests/routes/test_routes_users.py                          47      0   100%
src/tests/test_services_qr.py                                  24      0   100%
-----------------------------------------------------------------------------------------
TOTAL                                                        2621    118    95%
```

## 📁 Project Structure

```bash
photo_share
├─ .gitignore
├─ alembic
│  ├─ env.py
│  ├─ README
│  ├─ script.py.mako
│  └─ versions
│     └─ There was a lot of them.py
├─ alembic.ini
├─ docker-compose.yml
├─ Dockerfile
├─ main.py
├─ poetry.lock
├─ Procfile
├─ pyproject.toml
├─ README.md
├─ src
│  ├─ conf
│  │  ├─ cloudinary.py
│  │  ├─ config.py
│  │  └─ __init__.py
│  ├─ database
│  │  ├─ db.py
│  │  ├─ models.py
│  │  └─ __init__.py
│  ├─ repository
│  │  ├─ admin.py
│  │  ├─ comments.py
│  │  ├─ descriptions.py
│  │  ├─ messages.py
│  │  ├─ pictures.py
│  │  ├─ rating.py
│  │  ├─ reactions.py
│  │  ├─ tags.py
│  │  ├─ users.py
│  │  └─ __init__.py
│  ├─ routes
│  │  ├─ admin.py
│  │  ├─ auth.py
│  │  ├─ comments.py
│  │  ├─ descriptions.py
│  │  ├─ main_router.py
│  │  ├─ messages.py
│  │  ├─ pictures.py
│  │  ├─ rating.py
│  │  ├─ reactions.py
│  │  ├─ search.py
│  │  ├─ tags.py
│  │  ├─ users.py
│  │  └─ __init__.py
│  ├─ schemas.py
│  ├─ services
│  │  ├─ auth.py
│  │  ├─ auth_roles.py
│  │  ├─ email.py
│  │  ├─ qr.py
│  │  ├─ search.py
│  │  ├─ secrets_manager.py
│  │  └─ __init__.py
│  ├─ tests
│  │  ├─ conftest.py
│  │  ├─ repository
│  │  │  ├─ test_repository_tags.py
│  │  │  ├─ test_unit_repository_comments.py
│  │  │  ├─ test_unit_repository_descriptions.py
│  │  │  ├─ test_unit_repository_pictures.py
│  │  │  ├─ test_unit_repository_reactions.py
│  │  │  ├─ test_unit_repository_user.py
│  │  │  └─ __init__.py
│  │  ├─ routes
│  │  │  ├─ test_routes_admin.py
│  │  │  ├─ test_routes_auth.py
│  │  │  ├─ test_routes_comments.py
│  │  │  ├─ test_routes_descriptions.py
│  │  │  ├─ test_routes_messages.py
│  │  │  ├─ test_routes_pictures.py
│  │  │  ├─ test_routes_rating.py
│  │  │  ├─ test_routes_search.py
│  │  │  ├─ test_routes_users.py
│  │  │  └─ __init__.py
│  │  ├─ test_access_required.py
│  │  ├─ test_services_qr.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ static
│  └─ photo
│     ├─ css
│     │  ├─ base.css
│     │  └─ bootstrap.css
│     └─ js
│        ├─ bootstrap.js
│        ├─ jquery-slim.js
│        └─ popper.js
└─ templates
   ├─ base.html
   ├─ home.html
   ├─ layout.html
   ├─ login.html
   ├─ navbar.html
   ├─ picture.html
   ├─ register.html
   ├─ resetPassword.js
   ├─ reset_password.html
   ├─ users.html
   ├─ user_details.html
   └─ __init__.py
```

Thank you for reading it! 😺
