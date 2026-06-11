set dotenv-load := true

dev:
    uv run fastapi dev src/main.py

db:
    docker run -d \
        --name postgres-pos \
        -e POSTGRES_DB={{env_var("DB_NAME")}} \
        -e POSTGRES_USER={{env_var("DB_USER")}} \
        -e POSTGRES_PASSWORD={{env_var("DB_PASS")}} \
        -p {{env_var("DB_PORT")}}:5432 \
        postgres:16-alpine
