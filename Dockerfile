FROM node:latest
 
# Create app directory
RUN mkdir -p ./src
WORKDIR ./src

# Copy files
COPY . .
 
RUN npm install -g npm
RUN apt update && apt upgrade -y
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python 3.10.6