# GitHub Pages e atualização de dados | GitHub Pages and data refresh

## Português

Este site apresenta um snapshot JSON, com pesquisa e ordenação locais. O campo `status` determina se os registros são **fictícios** (`sample`) ou oriundos de uma coleta oficial validada (`official`).

### Publicação

Configure **Settings → Pages → Deploy from a branch → main → / (root)** depois de integrar a branch `feature/pages-public-data-dashboard`.

### Dados oficiais (opcional)

1. Solicite sua chave em https://portaldatransparencia.gov.br/api-de-dados (não a inclua no código).
2. Em **Settings → Secrets and variables → Actions**, crie um *repository secret* chamado **CGU_API_KEY**.
3. Confira em `.github/workflows/refresh-public-data.yml` os filtros `CGU_YEAR`, `CGU_ORGAOS` e `CGU_MAX_PAGES`. O exemplo é intencionalmente restrito a um órgão, um ano e uma página.
4. Execute manualmente **Actions → Refresh public expenditure snapshot → Run workflow**. O workflow também é agendado semanalmente, mas sem a chave apenas mantém a amostra.
5. Revise a execução e o JSON gerado. **Não é um total nacional** nem uma consulta em tempo real.

A API oficial pode alterar seu esquema. O script falha sem publicar caso não encontre nome, empenhado, liquidado e pago nos campos esperados. O primeiro teste com token pode demandar ajuste do mapeamento do retorno oficial. Não existe validação de integração executada contra a CGU neste commit.

A aplicação Flask/MySQL/Selenium existente é independente do dashboard Pages. Este projeto não representa a CGU.

## English

This static dashboard reads a JSON snapshot and provides local search and sorting. `status: sample` indicates fictional data; `status: official` indicates a validated API snapshot.

After merging the feature branch, enable **Settings → Pages → Deploy from a branch → main → / (root)**.

To fetch official data, register for a token via the CGU Transparency Portal, save it as the **CGU_API_KEY** Actions secret, review the bounded year/agency/page filters in the workflow, and manually run **Refresh public expenditure snapshot**. It also has a weekly schedule; without a configured key, the sample stays untouched.

The API's response fields have not yet been integration-tested; publishing fails safely if expected values are absent. The sample never masquerades as official data. This is a selected subset, not live nationwide statistics.

The original Python/Flask/MySQL/Selenium application is preserved.
