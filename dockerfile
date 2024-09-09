# Use Python 3.10-slim base image (optimized for size)
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for Poetry and Streamlit
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry directly from the official repository
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false

# Copy only the necessary files to the container
COPY poetry.lock pyproject.toml /app/

# Install Python dependencies in a single layer
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Expose the default port Streamlit runs on
EXPOSE 8501

# Set environment variables for Streamlit (this avoids adding a config file)
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]