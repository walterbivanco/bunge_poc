from google.cloud import bigquery

# Crear cliente de BigQuery
client = bigquery.Client(project="bunge-de-poc-insumos")

# Hacer una query simple de test
query = "SELECT 1 AS ok, 'BigQuery funciona!' AS mensaje"
rows = list(client.query(query).result())

print("✅ Respuesta de BigQuery:")
for row in rows:
    print(f"  ok: {row.ok}, mensaje: {row.mensaje}")
