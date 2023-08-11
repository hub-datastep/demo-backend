FROM python:3

RUN pip install poetry
ENV PATH="${PATH}:/root/.local/bin"

# Updates packages list for the image
RUN apt-get update

# Installs transport HTTPS
RUN apt-get install -y curl apt-transport-https

# Retrieves packages from Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Updates packages for the image
RUN apt-get update

# Installs SQL drivers and tools
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Installs MS SQL Tools
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools

# Adds paths to the $PATH environment variable within the .bash_profile and .bashrc files
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Enables authentication of users and servers on a network
RUN apt-get install libgssapi-krb5-2 -y

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY langchain-with-pydantic-v2 ./langchain-with-pydantic-v2
RUN chmod +x langchain-with-pydantic-v2/install.sh \
    && ./langchain-with-pydantic-v2/install.sh

CMD ["python3", "src/app.py"]