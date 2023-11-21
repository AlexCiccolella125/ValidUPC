FROM python:3.10

# Set the working directory
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# # Build the application
# RUN python -m build

# # Install the application
# RUN pip install --no-cache-dir dist/*.whl

