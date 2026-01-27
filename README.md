# Case CatLovers

1. A extração está sendo feita usando o arquivo extracao.py.
O código faz a requisição da API e salva os arquivos em dois locais "/data/raw" os arquivos.json e "/data/processed" os arquivos .CSV já em formato tabular. Os nomes dos arquivos contém a data em que eles foram extraidos ("YYYY-mm-dd").

2. Arquitetura GCP 
  * **Migração inicial**: `data/raw` → GCS 
    Usando partição por data no formato: gs://bucket/raw/facts/date=*/file.json
  * **Extração contínua**: Cloud Scheduler → Cloud Function → API → GCS
    Assim continuamos extraindo os dados automaticamente, com o tempo de agentamento necessário.
  * **Raw layer**: External Table no BigQuery lê GCS particionado
    Aqui, a table pode ser tanto external quanto nativa dependendo do crescimento e consumo.
    A Nativa é mais indicada para volumes grande.
  * **Silver layer**: SQL transforma External Table → insere na tabela Silver
    Filtros necessários, normalização dos nomes de colunas e remoção de duplicados.
  * **Consumo**: Analistas consultam tabela Silver via BigQuery

3. Especificação do Esquema da tabela Silver para Analytics

| Campo | Tipo | Modo | Descrição |
|-------|------|------|-----------|
| `id` | `STRING` | `REQUIRED` | Identificador único |
| `text` | `STRING` | `NULLABLE` | Texto do Fato |
| `updated_at` | `TIMESTAMP` | `REQUIRED` | Timestamp de atualização na API |
| `date` | `DATE` | `REQUIRED` | Data de ingestão |
