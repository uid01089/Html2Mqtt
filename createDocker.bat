pip freeze > requirements.txt
docker build -t htmltomqtt -f Dockerfile .
docker tag htmltomqtt:latest docker.diskstation/htmltomqtt
docker push docker.diskstation/htmltomqtt:latest