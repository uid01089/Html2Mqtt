#! /bin/bash

CONTAINER_NAME=html2Mqtt
REG_NAME=docker.diskstation/htmltomqtt:latest
DIR_NAME=Html2Mqtt
#CONFIG_NAME=mqtt2influx.json
PORT=8099

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME



case "$1" in
    "test")
        docker rmi $REG_NAME
        docker run \
        -p $PORT:8000 \
        -v /etc/timezone:/etc/timezone:ro \
        -v /etc/localtime:/etc/localtime:ro \
        -e "TZ=Europe/Berlin" \
        --name $CONTAINER_NAME \
        $REG_NAME
        ;;
    "run")
        docker run -id\
        -p $PORT:8000 \
        -v /etc/timezone:/etc/timezone:ro \
        -v /etc/localtime:/etc/localtime:ro \
        -e "TZ=Europe/Berlin" \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        $REG_NAME
        ;;
    *)
        echo "Invalid option. Supported options: test, run"
        exit 1
        ;;
esac
