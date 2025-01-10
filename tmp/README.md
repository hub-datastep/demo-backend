## Run in Docker
Create .env file in the root of the project and fill it with secrets. 

You need Docker to run locally.

Create a docker image

```bash
make build
```

Run docker image

```bash
make run
```

## Run locally
Create .env file in the root of the project and fill it with secrets.

Install dependencies
```bash
poetry install
```

If you use linux
```bash
bash langchain-with-pydantic-v2/install_linux.sh  
```

If you use mac
```bash
bash langchain-with-pydantic-v2/install_mac.sh  
```

Run app.py in src folder.


## Usage

You can find Swagger on http://0.0.0.0:8080/api/v1/docs

Server will reload on every changes
