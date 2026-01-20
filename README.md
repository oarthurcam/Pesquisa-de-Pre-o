# Coletor de Preços com Google Custom Search

Projeto em Python focado na **pesquisa automática de produtos na web**
e **extração de preços**, utilizando a API do Google Custom Search
e scraping básico de páginas de e-commerce.

--------------------------------------------------

🎯 OBJETIVO
- Ler uma lista de produtos a partir de um arquivo JSON
- Pesquisar páginas de venda relevantes na web
- Extrair preços diretamente dos sites encontrados
- Consolidar os resultados em um novo arquivo JSON

--------------------------------------------------

🛠️ TECNOLOGIAS
- Python
- Google Custom Search API
- HTTPX
- BeautifulSoup (bs4)
- JSON
- Expressões Regulares (Regex)

--------------------------------------------------

📌 FUNCIONALIDADES
- Leitura estruturada do arquivo `produto.json`
- Busca inteligente via Google Custom Search
- Filtro de URLs irrelevantes (redes sociais, Wikipedia, etc.)
- Priorização de sites de venda e marketplaces
- Extração de preços no formato brasileiro (R$)
- Controle de delays para evitar bloqueios
- Geração automática de arquivo final com os preços coletados

--------------------------------------------------

📂 ESTRUTURA DOS ARQUIVOS

Entrada (`produto.json`):
{
  "produtos": [
    { "nome": "Nome do produto" }
  ]
}

Saída (`produtos_com_precos.json`):
{
  "produtos": [
    {
      "nome": "Nome do produto",
      "sites": [
        {
          "url": "https://...",
          "titulo": "...",
          "preco": "R$ 99,90"
        }
      ]
    }
  ]
}

--------------------------------------------------

🔍 CONCEITOS APLICADOS
- Consumo de APIs REST
- Web scraping controlado
- Expressões regulares para extração de valores
- Normalização e filtragem de dados
- Automação de coleta de informações

--------------------------------------------------

🚀 STATUS
Projeto funcional, pronto para uso em:
- Pesquisa de preços
- Comparação de valores
- Análises de mercado
- Automação comercial

--------------------------------------------------
