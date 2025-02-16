# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR

# Copy dependencies file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files into the container
COPY . .

# Expose the FastAPI port
EXPOSE 8080

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
