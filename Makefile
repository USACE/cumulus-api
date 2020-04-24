.PHONY: build clean deploy

build:
	env GOOS=linux go build -ldflags="-s -w" -o bin/root root/main.go

clean:
	rm -rf ./bin ./vendor Gopkg.lock

local: build
	sls offline --useDocker --printOutput start

package: clean build
	serverless package

deploy: package
	aws lambda update-function-code \
	--function-name corpsmap-cumulus-api \
	--zip-file fileb://.serverless/corpsmap-cumulus-api.zip

docs:
	redoc-cli serve -p 4000 apidoc.yaml
