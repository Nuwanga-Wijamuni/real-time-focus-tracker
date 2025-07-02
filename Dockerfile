# --- Stage 1: Build Environment ---
# This stage remains the same. It's an efficient way to build our dependencies.
FROM python:3.9-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential

RUN python -m venv /opt/venv

COPY requirements.txt .

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Production Image ---
# We switch to the 'buster' image, which is more comprehensive than 'slim'.
# This provides better support for shared libraries needed by packages like OpenCV.
FROM python:3.9-buster

# Install the specific system dependencies required by OpenCV at runtime.
# This prevents the "cannot open shared object file" errors.
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the virtual environment with all the installed dependencies
# from the 'builder' stage.
COPY --from=builder /opt/venv /opt/venv

# Copy the application code into the container
COPY ./app /app/app

# Expose the port that the application will run on.
EXPOSE 8000

# Define the command to run the application when the container starts.
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]