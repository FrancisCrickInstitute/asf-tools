FROM python:3.11
LABEL authors="chris.cheshire@crick.ac.uk"

# Update pip to latest version
RUN python -m pip install --upgrade pip

# Add thesource files to the image
COPY . /usr/src/asf_tools
WORKDIR /usr/src/asf_tools

# Install program
RUN pip install .

CMD ["bash"]
