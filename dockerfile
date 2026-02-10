FROM python:3.10

# Install system dependency for pyzbar
RUN apt-get update && apt-get install -y libzbar0 && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Install the application in editable mode
RUN pip install -e .
