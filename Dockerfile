FROM ubuntu:16.10

RUN apt-get update -y
RUN apt-get install -y python-cryptography python-protobuf

# only needed for dev
# RUN apt-get install -y protobuf-compiler
