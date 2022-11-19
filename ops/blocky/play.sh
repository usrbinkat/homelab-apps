#!/bin/bash -x

#run --name blocky -v /path/to/config.yml:/app/config.yml -p 4000:4000 -p 53:53/udp spx01/blocky

podman pod create \
           --replace \
           --cpus 2 \
           --memory 256m \
           --name blocky \
           --hostname blocky \
           --publish 53:53/udp \
           --publish 53:53/tcp \
           --publish 4000:4000 \
	   --volume ./config.yaml:/app/config.yml \
	&& echo
#       --volume ./config.yaml:/app/config.yaml

podman run \
           --detach \
           --replace \
           --name dns \
           --pod blocky \
           --restart always \
           --label app=blocky \
           --pull IfNotPresent \
           --annotation app=blocky \
           --tz="America/Los_Angeles" \
           --env TZ="America/Los Angeles" \
         docker.io/spx01/blocky \
	&& echo
