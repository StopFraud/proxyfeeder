# proxyfeeder

docker pull ghcr.io/stopfraud/proxyfeeder:main


docker run -it --rm -e RABBITMQ_PASSWORD=password -e RABBITMQ_SERVER=serverip -e RABBITMQ_USER=guest ghcr.io/stopfraud/proxyfeeder:main

(specify your RABBITMQ server, plain text auth so far) or specifying above in file

docker run -it --rm --env-file=rabbit.txt ghcr.io/stopfraud/proxyfeeder:main

or without env viariables to output to stdout

docker run -it --rm  ghcr.io/stopfraud/proxyfeeder:main
