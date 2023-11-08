FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the source code
COPY . .

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Build the application
RUN python -m build

# Install the application
RUN pip install --no-cache-dir dist/*.whl

# Copy the rest of the application code
COPY . .
