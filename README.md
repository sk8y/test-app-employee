# test-app-hello
load test microservices


# develop

```bash
python3 -m venv  venv
source venv/bin/activate
pip install -r requirements.txt

```

# build

Using docker

```bash
# build image
docker buildx build --platform linux/amd64 -t docker.io/hihellobolke/test-app-employee:latest .

# push to docker hub
docker push docker.io/hihellobolke/test-app-employee:latest


# run docker image
docker pull shubham4444/test-app-employee:build-test
docker run -ti -p 8000:8000 docker.io/shubham4444/test-app-employee:build-test
```
