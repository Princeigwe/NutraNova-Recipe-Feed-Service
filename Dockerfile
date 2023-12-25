
FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# RUN mkdir /tmp/media

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

# create media directory in the working directory. make sure "media" folder does not exist already
RUN mkdir /code/media/

# starting django server on container startup
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:2000"]
CMD ["python3", "manage.py", "runserver"]


