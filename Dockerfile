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

# create media directory in the working directory
RUN mkdir /code/media/

# give execution rights to the script that will be executed
RUN chmod +x /code/scripts/clear_media_dir.sh

# install Cron
RUN apt-get update && apt-get -y install cron
# RUN apt-get -y install cron

# add cron job script to cron tab and schedule execution. job to be excuted every 5 minutes
RUN echo "5 * * * * /code/scripts/clear_media_dir.sh" | crontab -

# starting django server and cron on container startup
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:2000"]
CMD ["sh", "-c",  "python3 manage.py runserver 0.0.0.0:2000 ; cron"]



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
