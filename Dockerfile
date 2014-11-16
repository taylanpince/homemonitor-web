FROM ubuntu:14.04

# Update packages
RUN apt-get update -y

# Install Python Setuptools
RUN apt-get install -y python python-pip nginx gunicorn supervisor

# Bundle app source
ADD . /src

# Setup nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /src/conf/nginx.conf /etc/nginx/sites-enabled/homemonitor.conf
run ln -s /src/conf/supervisor.conf /etc/supervisor/conf.d/homemonitor.conf

# Add and install Python modules
RUN pip install -r /src/conf/requirements.pip

# Expose
EXPOSE 80

# Run
CMD ["supervisord", "-n"]
