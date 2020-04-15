FROM tensorflow/tensorflow:latest-py3

# Copy over required files for our web api
COPY ["Web App", "Web App"]
COPY ["ML Model", "ML Model"]
COPY ["Database", "Database"]
COPY ["requirements.txt", "requirements.txt"]

# Install dependencies
RUN pip install -U pip
RUN pip3 install -r "requirements.txt"

# Set working directory
WORKDIR "Web App"

# Create port 5000 for our web api
EXPOSE 5000

# Create port 5432 for our local instance of postgresql
EXPOSE 5432

# Run the web api at runtime
CMD gunicorn --bind 0.0.0.0:$PORT wsgi
