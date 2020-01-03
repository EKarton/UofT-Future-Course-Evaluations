FROM tensorflow/tensorflow:latest-py3

# copy over required files for our web api
COPY ["Web Api", "/app/Web Api"]
COPY ["ML Model", "/app/ML Model"]
COPY ["Database", "/app/Database"]
COPY ["requirements.txt", "/app/requirements.txt"]

# install dependencies
RUN pip install -U pip
RUN pip3 install -r "/app/requirements.txt"

# set working directory
WORKDIR "/app/Web Api"

# create port 5000 for our web api
EXPOSE 5000

# create port 5432 for our local instance of postgresql
EXPOSE 5432

# run the web api at runtime
CMD ["python3", "app.py"]
