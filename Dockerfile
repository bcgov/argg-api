FROM python:3.6.1

ENV APP_DIR /app

# Create the group and user to be used in this container
RUN groupadd appgroup && useradd -m -g appgroup -s /bin/bash appuser
 
# Create the working directory (and set it as the working directory)
RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

#Install a WSGI server
RUN pip install gunicorn 

# Install the package dependencies (this step is separated
# from copying all the source code to avoid having to
# re-install all python packages defined in requirements.txt
# whenever any source code change is made)
COPY requirements.txt ${APP_DIR}
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the source code into the container
COPY . ${APP_DIR}
 
RUN chown -R appuser:appgroup ${APP_DIR}

USER appuser

ENTRYPOINT ["/usr/local/bin/gunicorn", "-w", "2", "-b", ":8000", "argg_api.main:app"]