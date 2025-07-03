FROM nodered/node-red:3.1

USER root

COPY certs/kainos-chain.pem /usr/local/share/ca-certificates/kainos-chain.crt

RUN apk add --no-cache ca-certificates && update-ca-certificates

ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/kainos-chain.crt

RUN npm install --unsafe-perm --omit=dev \
        node-red-contrib-kafka-node@^0.1 \
        node-red-contrib-kafkajs@0.0.7 \
        node-red-contrib-moment@5

COPY flow.json /data/flows.json

USER node-red
