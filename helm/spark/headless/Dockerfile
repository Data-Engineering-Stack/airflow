FROM python:3.9-slim

RUN apt-get update && apt-get install -y curl

RUN pip install --no-cache-dir kubernetes==26.1.0

# install kubectl and put the binary to a location in PATH
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN chmod +x kubectl
RUN mkdir -p usr/local/bin
RUN mv ./kubectl usr/local/bin/kubectl