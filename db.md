```bash
docker compose down -v
docker compose up -d
```

Criar o segundo banco (`db_aghu`) manualmente.

```bash
docker compose exec db psql -U user -d postgres -c "CREATE DATABASE db_aghu;"
```

Deve aparecer `CREATE DATABASE`.

Verificar se os dois bancos existem:

```bash
docker compose exec db psql -U user -l
```
Deve aparecer `db_quimio` e `db_aghu` na lista.
