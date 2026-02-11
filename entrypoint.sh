#!/bin/sh

set -e

echo "Aguardando o banco de dados iniciar em $db_app:5432..."

DB_HOST="db_app"
DB_PORT="5432"

i=0
while ! nc -z $DB_HOST $DB_PORT; do
  i=$((i+1))
  if [ $i -ge 30 ]; then
    echo "Erro: Timeout aguardando banco de dados!"
    exit 1
  fi
  echo "Aguardando banco de dados... ($i/30)"
  sleep 1
done

echo "Banco de dados está pronto!"

echo "Executando seed de produção..."
python -m src.scripts.seed_prod

echo "Iniciando servidor..."
exec "$@"
