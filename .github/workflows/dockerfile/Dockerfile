# This Dockerfile is used to build an handles vnc image based on Debian
From python:3.12

ENV REFRESHED_AT 2023-11-28
RUN apt-get update && apt-get upgrade -y
# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && ./aqs/Install
RUN apt-get install git -y
RUN pip install pyyaml
RUN pip install jsonpath-ng
RUN apt-get install zip -y
RUN pip install boto3