FROM postgres:13

RUN apt-get update -y \
    &&  apt install -y curl unzip glibc-doc groff less \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip && ./aws/install

RUN mkdir /app
WORKDIR /app