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
- **Cloud Scheduler**
  Responsável por disparar a extração na periodissidade necessária.
- **Cloud Functions**
  Executa a lógica de extração da API.
- **Google Cloud Storage**
  Armazena os dados brutos em formato JSON.

2. Arquitetura GCP 
    * **Migração inicial**: `data/raw` > GCS 
        Usando partição por data no formato: gs://bucket/raw/facts/date=*/file.json
    * **Extração contínua**: Cloud Scheduler > Cloud Function > API > GCS
        Assim continuamos extraindo os dados automaticamente, com o tempo de agentamento necessário.
    * **Raw layer**: External Table no BigQuery lê GCS particionado
        Aqui, a table pode ser tanto external quanto nativa dependendo do crescimento e consumo.
        A Nativa é mais indicada para volumes grande.
    * **Silver layer**: SQL transforma External Table → insere na tabela Silver
        Filtros necessários, normalização dos nomes de colunas e remoção de duplicados.
    * **Consumo**: Analistas consultam tabela Silver via BigQuery
    * **Updates**: PUB/SUB > Cloud Function > BigQuery

        Os updates podem ser orquestrados usando PUB/SUB para serem ativados quando novos arquivos forem salvos no passo da extração

3. Especificação do Esquema da tabela Silver para Analytics

| Campo | Tipo | Modo | Descrição |
|-------|------|------|-----------|
| `id` | `STRING` | `REQUIRED` | Identificador único |
| `text` | `STRING` | `REQUIRED` | Texto do Fato |
| `updated_at` | `TIMESTAMP` | `NULLABLE` | Timestamp de atualização na API |
| `date` | `DATE` | `REQUIRED` | Data de ingestão |

4. Fatos de Agosto de 2020

´´´
  SELECT
    id,
    text,
    updated_at,
    date
  FROM project.dataset.facts_silver
  WHERE EXTRACT(YEAR FROM updated_at) = 2020
    AND EXTRACT(MONTH FROM updated_at) = 8;

´´´

5. Consulta Aleatória (10%)
´´´
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
  date
FROM `project.dataset.facts_silver`
WHERE RAND() < 0.10;

´´´
