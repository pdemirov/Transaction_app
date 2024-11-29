# Dockerfile

# Use Python base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install -r requirements.txt

# Copy the app code into the container
COPY . /app

# Expose the port Flask will use
EXPOSE 5000

# Run the Flask application
CMD ["python", "-i", "app.py"]