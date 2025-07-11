# fastapi-template

It is a template for creating a FastAPI project with a clean architecture. It contains a proper directory structure and a few example files. It is initialised with poetry, alembic, sqlalchemy and few other commonlly used libraries.

## Features

- **FastAPI**: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

- **Pydantic**: Data validation and settings management using python type annotations.

- **SQLAlchemy**: SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.

- **Alembic**: Alembic is a lightweight database migration tool for SQLAlchemy.

- **Poetry**: Poetry is a tool for dependency management and packaging in Python.

- **Docker**: Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers.

# Note: This project is created for template purpose only. Any piece of code can be modified as per the requirement. All the dependencies added in the pyproject.toml file are for the template purpose only. You can add or remove any dependencies as per the requirement.

I have added few sample files in the project to maintain the directory structure and give an idea of how to use the template. You can remove them and add your own files as per the requirement.

## Code Formatting

This template includes automatic code formatting setup:

- **Black** & **isort** for Python formatting (configured in `pyproject.toml`)
- **Flake8** for linting (configured in `.flake8`)
- **Pre-commit hooks** for automatic formatting on commit

After cloning, run: `poetry install` and `poetry run pre-commit install`
