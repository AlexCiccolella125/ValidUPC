FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the source code
COPY . .

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Build the application
RUN python -m build

# Install the application
RUN pip install --no-cache-dir dist/*.whl

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# # Set the entrypoint
# ENTRYPOINT ["python", "app.py"]