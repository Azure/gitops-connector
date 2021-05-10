FROM python:3.7-slim

ENV APP_HOME /app
ENV WORKERS 1
ENV THREADS 1
ENV PREDICTIVE_UNIT_SERVICE_PORT 8080
WORKDIR $APP_HOME
COPY . ./
ENV PYTHONUNBUFFERED=1

# FLUX or ARGOCD
env GITOPS_OPERATOR_TYPE=FLUX

# AZDO or GITHUB
env GIT_REPOSITORY_TYPE=AZDO

# Required if either Git repository or CI/CD orchestrator is Azure DevOps
ENV AZDO_ORG_URL=
ENV AZDO_GITOPS_REPO_NAME=

ENV PAT=
ENV GITOPS_APP_URL=

RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["sh","-c","gunicorn --bind 0.0.0.0:$PREDICTIVE_UNIT_SERVICE_PORT --workers $WORKERS --threads $THREADS gitops_event_handler"]