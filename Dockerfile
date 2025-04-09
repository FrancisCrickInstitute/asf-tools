FROM python:3.11

LABEL authors="chris.cheshire@crick.ac.uk"

# Install system dependencies required for psycopg2 and general builds
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        build-essential \
        && pip install --upgrade pip \
        && rm -rf /var/lib/apt/lists/*

# Copy source files
COPY . /usr/src/asf_tools
WORKDIR /usr/src/asf_tools

# Update version
RUN pip install toml && python update_version.py

# Install package (build + deps)
RUN pip install .

CMD ["bash"]
