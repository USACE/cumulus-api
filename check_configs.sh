# Scan repo for possible misconfigurations
docker run -v $PWD:/myapp aquasec/trivy config /myapp