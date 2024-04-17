FROM 861698843696.dkr.ecr.eu-west-1.amazonaws.com/build-aws-ng:python-3.11_node-18

RUN python -m pip install --upgrade pip

USER jenkins

ARG BUILD_DATE
ARG GIT_URL
ARG GIT_COMMIT

LABEL org.opencontainers.image.vendor="People's Postcode Lottery" \
    org.opencontainers.image.description="Account Service Python CI Build Image" \
    org.opencontainers.image.authors="Player Team<BIPPlayerTeam@postcodelottery.co.uk" \
    org.opencontainers.image.version="v1.0.0" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.source="${GIT_URL}" \
    org.opencontainers.image.revision="${GIT_COMMIT}"
