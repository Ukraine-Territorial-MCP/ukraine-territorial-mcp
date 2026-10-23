# Ukraine Territorial MCP 🇺🇦

**The primary repository and official entry point for the Ukraine Territorial MCP project.**

[Українською](#українською) · [English](#english) · [MCP endpoint](https://community.ukrdigital.org/mcp/ukraine/mcp)

> **Main project / Головний проєкт**
> Core development, documentation, integrations, and future releases are coordinated here. The other repositories in the [Ukraine-Territorial-MCP organization](https://github.com/Ukraine-Territorial-MCP)—many named by KATOTTG codes—represent derived territorial components, experiments, or works in progress. **Start here**, not from an individual territorial repository.

## Українською

**Ukraine Territorial MCP** — відкритий проєкт для доступу ШІ-асистентів і розробників до адміністративно-територіального устрою України та структурованих даних про органи місцевого самоврядування через [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

### Поточний стан (жовтень 2026)

- **31 744** територіальні записи каталогу КАТОТТГ.
- **19** інструментів, перевірених через публічне HTTPS-підключення MCP.
- **1 556** зіставлених місцевих рад: назва, ЄДРПОУ, код КАТОТТГ відповідного населеного пункту. Статус зіставлення визначений за наявними даними; повнота й актуальність окремих записів можуть відрізнятися.
- Підтримка даних про області, райони, громади, населені пункти, обласні й районні ради.
- Подальше наповнення реєстрів і тематичних модулів триває.

### Підключення

Публічна MCP-адреса:

```text
https://community.ukrdigital.org/mcp/ukraine/mcp
```

Використовуйте її у MCP-клієнті з підтримкою віддалених серверів **Streamable HTTP**. Доступність окремих інструментів залежить також від оновлення списку інструментів у клієнті.

Приклади інструментів:

- `search_local_councils` — пошук місцевої ради за назвою, ЄДРПОУ чи КАТОТТГ;
- `get_local_council` — дані про конкретну місцеву раду;
- `list_local_councils` — список рад із пагінацією;
- `search_district_councils`, `get_district_council`, `list_district_councils` — районні ради.

### Структура проєкту

Цей репозиторій є **центральним джерелом документації та майбутніх релізів**. Багато інших репозиторіїв організації названі за кодами КАТОТТГ і є похідними територіальними компонентами або прототипами. Вони **не є альтернативними головними версіями** національного сервера. Для інтеграції використовуйте посилання на MCP вище.

**Статус цього GitHub-репозиторію:** документація створена; синхронізація вихідного коду з робочим сервером та інструкції локального розгортання готуються. Наявність публічного MCP endpoint не означає, що повний серверний код уже опубліковано тут.

### Джерела та відповідальність

Проєкт використовує КАТОТТГ і зіставлені дані відкритих державних реєстрів. Записи можуть мати різні методи підтвердження. Дані надаються для пошуку й аналізу; для юридично значущих рішень перевіряйте актуальні першоджерела.

## English

Ukraine Territorial MCP gives AI agents and developers structured access to Ukrainian administrative geography and local-government information through the Model Context Protocol.

### Project status (October 2026)

- **31,744** territorial catalog records (KATOTTG).
- **19** MCP tools verified through the public HTTPS endpoint.
- **1,556** mapped local councils, with council names, EDRPOU identifiers, and KATOTTG settlement identifiers.
- Regional and district council data, with ongoing expansion to additional official open-data sources.

### Connect

**Remote MCP server (Streamable HTTP):**

```text
https://community.ukrdigital.org/mcp/ukraine/mcp
```

For discovery, integration, documentation, and contributions, **use this repository as the primary entry point**. Other KATOTTG-named repositories in the organization are derived components or under development. Server source publication and self-hosting instructions are being prepared; this repository currently serves as the official project landing page.

### Roadmap

- Publish reviewed server source and deployment instructions without credentials or private data.
- Improve data provenance, validation, and source freshness.
- Expand local-government coverage, contacts, budgets, procurements, and related public datasets.
- Improve MCP tool discovery and documentation.

---

**Organization:** [Ukraine-Territorial-MCP](https://github.com/Ukraine-Territorial-MCP) · **Live MCP:** [community.ukrdigital.org](https://community.ukrdigital.org/mcp/ukraine/mcp)
