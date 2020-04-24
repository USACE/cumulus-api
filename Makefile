packagename = corpsmap-cumulus-api

.PHONY: build clean deploy

build:
	env GOOS=linux go build -ldflags="-s -w" -o bin/root root/main.go

clean:
	rm -rf ./bin ./vendor $(packagename).zip Gopkg.lock

package: clean build
	zip -r $(packagename).zip bin

deploy: package
	aws lambda update-function-code \
	--function-name corpsmap-cumulus-api \
	--zip-file fileb://$(packagename).zip

docs:
	redoc-cli serve -p 4000 apidoc.yaml
