# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . /app/

# Set environment variables (like SECRET_KEY)
ENV SECRET_KEY="2a4a8665a383d0d2f72e5ddea7cd7c39ab9751bec931dd7b"

# Expose the port the app runs on
EXPOSE 8080

# Run the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
