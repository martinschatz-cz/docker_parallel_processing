# Use an official Python image
FROM python:3.9-slim

# Set up directories
WORKDIR /app
COPY worker_script.py /app
#COPY data /app/data  # Copy your input data folder (can be mounted as a volume instead)
COPY requirements.txt /app

# Install dependencies
RUN pip install -r requirements.txt

# Run the worker script
CMD ["python", "worker_script.py"]

