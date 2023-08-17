IMAGE_NAME=msu-backend:dev

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -it --env-file .env -p 8080:8080 $(IMAGE_NAME)

db:
	docker run \
	-e "ACCEPT_EULA=Y" \
	-e "SA_PASSWORD=Z5u7hWqLhQ0gcCP" \
   	-p 1433:1433 --name sql1 --hostname sql1 -d \
   	mcr.microsoft.com/mssql/server:2022-latest

deploy-master:
	fly deploy --config fly.master.toml

deploy-dev:
	fly deploy --config fly.dev.toml
