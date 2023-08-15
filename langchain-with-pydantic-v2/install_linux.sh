pip uninstall -y langchain langsmith openapi-schema-pydantic langchain_experimental

tar -xzvf langchain-with-pydantic-v2/lib/langsmith-0.0.20.tar.gz -C langchain-with-pydantic-v2/lib/
tar -xzvf langchain-with-pydantic-v2/lib/langchain-0.0.261.tar.gz -C langchain-with-pydantic-v2/lib/
tar -xzvf langchain-with-pydantic-v2/lib/openapi-schema-pydantic-1.2.4.tar.gz -C langchain-with-pydantic-v2/lib/
tar -xzvf langchain-with-pydantic-v2/lib/langchain_experimental-0.0.8.tar.gz -C langchain-with-pydantic-v2/lib/

find ./langchain-with-pydantic-v2/lib/ -type f -exec sed -i 's/from pydantic/from pydantic.v1/g' {} \;
sed -i 's/pydantic = "^1"/pydantic = "^2"/g' ./langchain-with-pydantic-v2/lib/langsmith-0.0.20/pyproject.toml
sed -i 's/pydantic = "^1"/pydantic = "^2"/g' ./langchain-with-pydantic-v2/lib/langchain-0.0.261/pyproject.toml

pip install langchain-with-pydantic-v2/lib/langsmith-0.0.20 \
  langchain-with-pydantic-v2/lib/langchain-0.0.261 \
  langchain-with-pydantic-v2/lib/openapi-schema-pydantic-1.2.4 \
  langchain-with-pydantic-v2/lib/langchain_experimental-0.0.8

rm -rf langchain-with-pydantic-v2/lib/langsmith-0.0.20 \
  langchain-with-pydantic-v2/lib/langchain-0.0.261 \
  langchain-with-pydantic-v2/lib/openapi-schema-pydantic-1.2.4 \
  langchain-with-pydantic-v2/lib/langchain_experimental-0.0.8

