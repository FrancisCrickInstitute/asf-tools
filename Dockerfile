FROM python:3.11-slim
LABEL authors="chris.cheshire@crick.ac.uk" \
    description="Docker image containing requirements for FrancisCrickInstitute/asf-tools"

# Update pip to latest version
RUN python -m pip install --upgrade pip

# Install dependencies
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

# Add thesource files to the image
COPY . /usr/src/asf_tools
WORKDIR /usr/src/asf_tools

# Install program
RUN python -m pip install .

ENTRYPOINT ["/bin/bash"]
