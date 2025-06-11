# Recipe Analysis

This project aims to provide methodology and tools for statistical analysis in recipe datasets. Recipes are represented as directed acyclic graphs (DAGs) and are stored as JSON documents using MongoDB. Most terms (actions, ingredients, equipment, etc.) in a recipe are stored as symbols that the system either does (canonical) or does not recognize. These symbols, their relationships, and metadata for use in categorization are stored in relational database tables using MariaDB.

View the project [roadmap](https://www.notion.so/1e3e91240bdd80c5ae30d3a007e170f9?v=1e3e91240bdd80b89d09000c1a8d5990&source=copy_link)

## Prerequisites

Before using this project, ensure you have the following installed on your system:
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/ColeTPeterson/recipe-analysis.git
cd recipe-analysis
```

### 2. Set Up Environmental Variables
This project uses environmental variables to configure services within Docker:
1. Copy the example .env file to create the development environment:
```bash
cp .env.example .env.dev
```
2. (Optional) Open .env.dev in a text editor to customize any values.

### 3. Running the Project
```bash
docker compose --env-file .env.dev --profile dev up -d
```

This command:
- Uses environmental variables from .env.dev
- Activates the development profile (includes database management tools)
- Runs containers in the background -d

### 4. Accessing Database Management Tools
With the development profile running, you can access the following WebUIs:
- phpMyAdmin (MariaDB WebUI):
    - Open your browser and navigate to http://localhost:8080
    - Username: admin
    - Password: password (or the value in .env.dev)
- Mongo Express (MongoDB WebUI):
    - Open your browser and navigate to http://localhost:8081
    - Username: admin
    - Password: pass (or the value in .env.dev)

### 5. Stopping the Project
When you are done working, stop all Docker services:
```bash
docker compose --env-file .env.dev down
```

## Project Structure

### Core Directories
- **dataset/** - Source files for database population and sample recipe datasets
- **docs/** - Internal project documentation including UML diagrams and database schemas
- **models/** - Python classes representing recipe components (ingredients, equipment, instructions, etc.)
- **tests/** - Unit and integration tests for Python implementation

### Configuration Files
- **.env.example** - Template for environmental variables used with Docker Compose
- **compose.yml** - Docker Compose configuration defining all project services

### Helper Files
- **README.md** - Project documentation and setup instructions
- **.dockerignore** - Specifies files to exclude from docker builds
- **.gitignore** - Specifies files to exclude from Git version control