# Use an official Ubuntu runtime as a parent image
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.9 and pip
RUN apt-get update && apt-get install -y python3.9 python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use pip3 to be explicit
RUN pip3 install --no-cache-dir -r requirements.txt

# Download the spacy model
RUN python3 -m spacy download en_core_web_sm


# Copy the rest of the application's code
COPY . .

# Add the app directory to the Python path
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
