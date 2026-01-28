# Case UOL CatLovers

Esse repositório contém a solução proposta para o case Cat Lovers, abordando desde a extração inicial dos dados pela API até sua disponibilização para consumo no BigQuery.

---
## 1. Extração dos dados usando python

A extração inicial é feita pelo script "extracao.py"

### Funcionamento
- O script faz a requisição get a API Cat Facts (no momento do desenvolvimento a API estava fora do ar)
- Os dados brutos são armazenados em formado JSON na pasta "data/raw"
- Em seguida os dados são salvos em formato tabular no arquivo CSV na pasta "data/processed"

### Organização dos arquivos

- Os arquivos seguem o padrão de nomenclatura: YYYY-mm-dd_fact.json e YYYY-mm-dd_fact.csv
- Essa nomenclatura permite versionamento simples, rastreabilidade e reprocessamento quando necessário.

## 2. Arquitetura na Google Cloud Platform (GCP)

Solução em GCP proposta:

### Ingestão
- **Cloud Scheduler**:
  Responsável por disparar a extração na periodissidade necessária.
- **Cloud Functions**:
  Executa a lógica de extração da API.
- **Google Cloud Storage**:
  Armazena os dados brutos em formato JSON.

Estrutura do bucket: gs://bucket/raw/facts/date=YYYY-MM-DD/file.json

### Camada Raw
- Os arquivos no bucket são lidos no BigQuery por meio de External Table.
- Essa abordagem inicial reduz custos e permite rápida disponibilização.
- Com o aumento de fatos, a camada raw passa a ser nativa, para evitar lentidão de leitura.
- E os incrementos são feitos sempre usando o último dia de atualização.

### Camada Silver
-Tabelas nativas no BigQuery
- Responsáveis por:
    - Normalização de colunas
    - Conversão de tipos
    - Remoção de duplicidades
    - Padronização de Timestamp

### Orquestação e atualizações
- **Pub/Sub** é utilizado para disparar as cargas incrementais sempre que novos arquivos são adicionados ao bucket.
- Uma Cloud Function consome esses eventos e realiza os INSERTS e UPDATES necessários.

### Consumo
- Time de analytics tem acesso direto a tabela Silver via BigQuery

---

## 3. Especificação do esquema da tabela Silver

Tabela: facts_silver

### Esquema

| Campo | Tipo | Modo | Descrição |
|-------|------|------|-----------|
| `id` | `STRING` | `REQUIRED` | Identificador único |
| `text` | `STRING` | `REQUIRED` | Texto do Fato |
| `updated_at` | `TIMESTAMP` | `NULLABLE` | Timestamp de atualização na API |
| `ingestion_date` | `DATE` | `REQUIRED` | Data de ingestão |
| `sent_count` | `INT` | `NULLABLE` | Número de vezes que o fato foi enviado |

### Considerações adicionais
- A tabela será particionada por `ingestion_date`
- O campo `id` pode ser utilizado para deduplicação.

--- 

## 4. Consulta: Fatos atualizados em agosto de 2020

```
SELECT
    id,
    text,
    updated_at,
    ingestion_date
  FROM project.dataset.facts_silver
  WHERE updated_at >= TIMESTAMP("2020-08-01")
    AND updated_at < TIMESTAMP("2020-09-01");
```

## 5. Consulta: Amostra aleatória de 10% dos dados

```
EXPORT DATA OPTIONS (
  uri = 'gs://qa-bucket/facts_qa_*.csv',
  format = 'CSV',
  overwrite = true,
  header = true,
  field_delimiter = ','
)
AS
SELECT
  text,
  updated_at,
  ingestion_date
FROM `project.dataset.facts_silver`
WHERE RAND() < 0.10;
```
