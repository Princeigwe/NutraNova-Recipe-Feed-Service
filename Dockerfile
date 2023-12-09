# FROM python:3
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# WORKDIR /code
# COPY requirements.txt /code/
# RUN pip install -r requirements.txt
# COPY . /code/
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:2000"]


FROM python:3 AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt


# commented out the "copy from builder stage because images could not find celery module from it"


FROM python:3 AS web
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# RUN mkdir /tmp/media

WORKDIR /code
# copy from builder stage
# COPY --from=builder /code /code  

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

# create media directory in the working directory. make sure "media" folder does not exist already
RUN mkdir /code/media/

# starting django server on container startup
CMD ["python3", "manage.py", "runserver", "0.0.0.0:2000"]



# FROM python:3 AS celery
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# WORKDIR /code
# # copy from builder stage
# # COPY --from=builder /code /code 
# COPY requirements.txt /code/
# RUN pip install -r requirements.txt 
# COPY . /code/
# CMD ["python3", "-m", "celery", "-A", "core",  "worker", "--loglevel=info", "--concurrency=3"]
