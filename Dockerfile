FROM ubuntu:14.04

# Update packages
RUN apt-get update -y

# Install Python Setuptools
RUN apt-get install -y python-setuptools

# Install pip
RUN easy_install pip

# Add and install Python modules
ADD requirements.pip /src/requirements.pip
RUN cd /src; pip install -r requirements.pip

# Bundle app source
ADD . /src

# Expose
EXPOSE 80

# Run
CMD ["python", "/src/application.py"]
