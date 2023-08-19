IMAGE_NAME=msu-backend:dev

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -it --env-file .env -p 8080:8080 -v "$$(pwd)"/src:/app/src $(IMAGE_NAME)

deploy-master:
	fly deploy --config fly.master.toml

deploy-dev:
	fly deploy --config fly.dev.toml
