# --- Stage 1: Build Environment ---
# We use a specific version of Python for reproducibility.
# The 'slim' variant is smaller than the full version.
FROM python:3.9-slim as builder

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies that might be needed by some Python packages
# (e.g., for compiling C extensions). This is good practice for robustness.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Create a virtual environment to isolate our dependencies
RUN python -m venv /opt/venv

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies into the virtual environment
# Using the venv's pip ensures they are installed in the right place.
# --no-cache-dir reduces the image size.
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Production Image ---
# Start from the same slim base image for the final stage
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# --- FIX: Install OpenCV's runtime dependency ---
# The libgl1-mesa-glx package provides the missing libGL.so.1 library.
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copy the virtual environment with all the installed dependencies
# from the 'builder' stage. This is the key to a small final image,
# as we don't bring along the build tools.
COPY --from=builder /opt/venv /opt/venv

# Copy the application code into the container
# This includes your 'app' directory with all the Python files.
COPY ./app /app/app

# Expose the port that the application will run on.
# This must match the port specified in your uvicorn command.
EXPOSE 8000

# Define the command to run the application when the container starts.
# We use the python from our virtual environment to run uvicorn.
# --host 0.0.0.0 is crucial to make the server accessible from outside the container.
# "app.main:app" tells uvicorn where to find the FastAPI app instance.
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]