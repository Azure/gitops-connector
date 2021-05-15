FROM python:3.9-slim

ENV APP_HOME /app
ENV WORKERS 1
ENV THREADS 1
ENV PREDICTIVE_UNIT_SERVICE_PORT 8080
WORKDIR $APP_HOME
COPY . ./
ENV PYTHONUNBUFFERED=1


RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["sh","-c","gunicorn --bind 0.0.0.0:$PREDICTIVE_UNIT_SERVICE_PORT --workers $WORKERS --threads $THREADS gitops_event_handler"]