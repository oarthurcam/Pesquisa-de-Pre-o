import httpx
import json
import re
from bs4 import BeautifulSoup


# Lê o arquivo JSON
def carregar_produtos(caminho_json="lab\\produto.json"):  # ← Mudei o nome da função
    try:
        with open(caminho_json, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados["produtos"]
    except FileNotFoundError:
        print("Arquivo JSON não encontrado.")
        return []
    except KeyError:
        print("Formato do JSON incorreto (faltando chave 'produtos').")
        return []
    

# Pesquisar
def pesquisar(produto: str, max_resultados: int = 5):

    # Inserindo variaveis de ambiente
    API_KEY = "API_KEY"
    ID_SEARCH = "ID_SEARCH"

    if not API_KEY or not ID_SEARCH:
        raise ValueError("Chave da API ou ID de pesquisa não configurados.")

    # Sites bloqueados e exclusão na query
    sites_bloqueados = ["sinetecirurgica.com.br"]
    exclusoes = " ".join([f"-site:{site}" for site in sites_bloqueados])
    query_modificada = f"{produto} {exclusoes}"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": ID_SEARCH,
        "q": query_modificada  # ← Usa a query modificada
    }

    # Realizar procura na web
    response = httpx.get(url, params=params)
    if response.status_code != 200:
        print(f"Erro {response.status_code}: {response.text}")
        return []
    
    data = response.json()
    resultados = []

    for item in data.get("items", []):
        link = item.get("link", "")
        if link and not any(site in link for site in sites_bloqueados):
            resultados.append({
                "link": link,
                "titulo": item.get("title", ""),
                "snippet": item.get("snippet", "")
            })
        
        if len(resultados) >= max_resultados:
            break
    
    return resultados


# Extrair preço
def extrair_preco_da_pagina(url):
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tenta seletores comuns
        seletores_precos = [
            'span[class*="price"]',
            'div[class*="price"]',
            '[itemprop="price"]',
            '.price',
            '#price',
        ]
        
        for seletor in seletores_precos:
            elemento = soup.select_one(seletor)
            if elemento:
                texto = elemento.get_text()
                match = re.search(r"R\$\s*(\d+(?:[.,]\d{3})*[.,]\d{2})", texto)
                if match:
                    return match.group(0)
        
        # Se não encontrou com seletores, busca no texto inteiro
        texto_pagina = soup.get_text()
        matches = re.findall(r"R\$\s*(\d+(?:[.,]\d{3})*[.,]\d{2})", texto_pagina)
        
        if matches:
            return matches[0]
        
        return None
        
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None


# Buscar preços e adicionar ao produto
def processar_produto(produto, max_sites=5):
    print(f"\nProcessando: {produto['nome']}")
    
    # Busca os links
    links = pesquisar(produto['nome'], max_resultados=max_sites)
    
    sites_encontrados = []
    
    # Para cada link, extrai o preço
    for item in links:
        print(f"  Verificando: {item['link']}")
        preco = extrair_preco_da_pagina(item['link'])
        
        sites_encontrados.append({
            "url": item["link"],
            "titulo": item["titulo"],
            "preco": preco if preco else "Não encontrado"
        })
    
    # Adiciona os sites ao produto
    produto['sites'] = sites_encontrados
    return produto


# Processar todos os produtos
def processar_todos_produtos(arquivo_entrada, arquivo_saida, max_sites=5):
    # Carrega o JSON original
    produtos = carregar_produtos(arquivo_entrada)  # ← Corrigido aqui
    
    produtos_atualizados = []
    
    # Processa cada produto
    for prod in produtos:  # ← Mudei o nome da variável para evitar confusão
        produto_atualizado = processar_produto(prod, max_sites)
        produtos_atualizados.append(produto_atualizado)
    
    # Salva o JSON atualizado
    resultado = {"produtos": produtos_atualizados}
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Arquivo salvo em: {arquivo_saida}")


# Executar
if __name__ == "__main__":
    processar_todos_produtos(
        arquivo_entrada="lab\\produto.json",  # ← Ajustei o caminho
        arquivo_saida="lab\\produtos_com_precos.json",
        max_sites=3  # Número de sites por produto
    )