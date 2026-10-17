## Ampliação controlada de cobertura (PT / EN)

A atualização automática usa a API oficial da CGU para um **subconjunto** de órgãos e páginas, não um total nacional.

- `CGU_ORGAOS`: lista de códigos de órgão superior (atualmente `26000,25000`).
- `CGU_MAX_PAGES`: até duas páginas por código; a coleta interrompe a sequência quando a API retorna lista vazia.
- `CGU_REQUEST_DELAY_SECONDS`: pausa de 1,5 segundo entre requisições.
- Resposta inesperada, campo monetário inválido ou registro duplicado causa falha, sem substituir o snapshot anterior.
- O JSON publica `coverage`, com os códigos consultados, limites, número de requisições e `complete: false`.
- O workflow executa testes Python antes de acessar a API.

**Atenção:** repetir os valores de duas consultas sobre órgãos com agregações sobrepostas pode causar dupla contagem. Os indicadores do dashboard representam apenas a soma dos registros exibidos, não os gastos totais nacionais. A cobertura deve ser revista antes de quaisquer inferências estatísticas.

English: The pipeline queries a limited set of superior-agency codes and pages, rate-limits requests, fails closed on unexpected data, and publishes coverage metadata. Dashboard totals apply **only to displayed records**, never to all federal expenditure.
