FROM python:3.8-slim

LABEL base_image="python:3.8-slim"
LABEL about.home="https://github.com/Clinical-Genomics/NIPTool"
LABEL about.tags="NIPT,statistics,Non Invasive Prenatal Test,python"

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install app requirements
RUN pip install -r requirements.txt

# Install app
RUN pip install -e .

# Create and switch to a new non-root user
RUN useradd worker
RUN chown worker:worker -R /home/worker
USER worker
