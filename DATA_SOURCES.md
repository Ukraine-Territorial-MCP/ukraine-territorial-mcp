# Data sources / Джерела даних

## Overview / Загальна інформація

Ukraine Territorial MCP combines territorial classification
data and structured information about Ukrainian local
self-government bodies.

The included JSON files are processed datasets, not
real-time connections to the original registries.

Дані у цьому репозиторії є підготовленими наборами.
Вони не оновлюються автоматично під час кожного запиту MCP.

## Main sources / Основні джерела

### KATOTTG — КАТОТТГ

Official classification of administrative-territorial units
and territories of territorial communities of Ukraine.

- https://www.minregion.gov.ua/
- https://data.gov.ua/

File: `data/official/ukraine-katottg.json`

### Unified State Register — ЄДР

Information used to identify local self-government
legal entities, including names and ЄДРПОУ codes.

- https://usr.minjust.gov.ua/

Files:
- `data/official/edr/katottg-oms-oblast.json`
- `data/official/edr/verified-community-councils.json`
- `data/official/district-councils.json`

Verification status reflects dataset processing,
not a guarantee of current legal status.

### Other public sources / Інші відкриті джерела

Some council records include references to:

- https://openbudget.gov.ua/
- https://data.gov.ua/
- https://tax.gov.ua/

Consult each record's `sources` field for its supporting
references where available.

### Geographic data / Географічні дані

Community geodata may include information from
OpenStreetMap and its related services.

- https://www.openstreetmap.org/copyright

File: `data/official/ivanivska-geodata.json`

OpenStreetMap attribution and ODbL obligations
must be respected when using derived geographic data.

## Limitations / Обмеження

- Datasets represent a prepared snapshot and may become outdated.
- Some records were matched automatically.
- The absence of a record does not establish that an
  institution or council does not exist.
- Always verify critical facts with authoritative sources.
- The legal terms and attribution requirements of the
  original data providers should be checked before reuse.

## Updates / Оновлення

The project aims to improve coverage, source traceability,
data quality and update procedures over time.
