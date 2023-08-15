IMAGE_NAME=msu-backend:dev

build:
	docker build -t $(IMAGE_NAME) .

run:
	#docker run --rm --env-file .env -p 8080:8080 -v $(shell pwd)/src:/app/src $(IMAGE_NAME)
	docker run --rm -it --env-file .env -p 8080:8080 $(IMAGE_NAME)
