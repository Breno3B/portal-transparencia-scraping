# Web Scraping — Portal da Transparência

🇧🇷 **Português** | [🇺🇸 English](README.en.md)

🌐 **[Dashboard bilíngue no GitHub Pages](https://breno3b.github.io/portal-transparencia-scraping/)** — pesquisa e ordenação sobre dados publicados em JSON. Inicialmente, os valores são fictícios; a atualização oficial exige um token CGU e validação do esquema de resposta. [Configuração](docs/pages-setup.md).

Projeto Python de coleta e consulta de dados públicos de despesas federais, desenvolvido originalmente como **desafio técnico da Agilize**. A implementação foi posteriormente revisada como exercício de manutenção e boas práticas de backend.

## Visão geral

- **Selenium** acessa a página de despesas no Portal da Transparência.
- **Pandas** interpreta uma tabela HTML renderizada.
- **MySQL** armazena os registros de despesa.
- **Flask** disponibiliza `GET /api/dados`, retornando JSON.

**Tecnologias:** Python, Selenium, Pandas, MySQL, Flask, `unittest` (testes).

## Início rápido

Requer Python compatível com as dependências, MySQL e Chrome/ChromeDriver disponíveis.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure as variáveis do arquivo `.env` e crie um banco acessível com o usuário configurado. Em dois terminais:

```bash
python -m backend.crawler
python -m api.app
```

Consulte `http://127.0.0.1:5000/api/dados`.

**Testes:**

```bash
python -m unittest discover -s tests -v
```

## Limitações importantes

Este é um projeto de estudo, **não um serviço em produção**. O HTML do Portal pode mudar; o seletor `TABLE_SELECTOR` e o mapeamento das colunas no código precisam ser conferidos com a página atual. A extração captura a primeira tabela HTML encontrada e **não implementa paginação completa**. A execução depende de navegador, driver e acesso ao MySQL. Testes de integração contra o portal não fazem parte da suíte unitária.

Os valores monetários da API são serializados como strings decimais para evitar perdas de precisão.

## Evolução

A solução original foi preservada em [`archive/original-challenge-2022`](https://github.com/Breno3B/portal-transparencia-scraping/tree/archive/original-challenge-2022). As melhorias incluem consultas SQL parametrizadas para os valores, validação de identificadores, transação para gravação em lote, ciclo de vida dos recursos, rota Flask correspondente ao desafio, e testes unitários.

Leia também [a descrição original do projeto](PROJETO.md) e [o enunciado do desafio](https://github.com/Debora1Allen/backend-challenge). O código permanece identificado como um fork.

## Autor

[Breno Rodrigues Magalhães](https://github.com/Breno3B)
