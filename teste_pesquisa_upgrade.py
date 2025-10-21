import httpx
import json
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote

# Lê o arquivo JSON
def carregar_produtos(caminho_json="lab\\produto.json"):
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

# Pesquisar usando API do Google Custom Search
def pesquisar(produto: str, max_resultados: int = 5):
    """Busca usando Google Custom Search API"""
    
    API_KEY = "API_KEY"
    ID_SEARCH = "ID_SEARCH"
    
    if not API_KEY or not ID_SEARCH:
        print("  ⚠ Chave da API ou ID de pesquisa não configurados")
        return []
    
    try:
        # Query melhorada
        query = f'{produto} (preço OR comprar OR venda)'
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": API_KEY,
            "cx": ID_SEARCH,
            "q": query,
            "num": 10
        }
        
        response = httpx.get(url, params=params, timeout=10)
        
        if response.status_code == 429:
            print("  ⚠ Cota de requisições excedida (100/dia)")
            return []
        
        if response.status_code != 200:
            print(f"  ⚠ Erro {response.status_code}")
            return []
        
        data = response.json()
        resultados = []
        
        for item in data.get("items", []):
            link = item.get("link", "")
            titulo = item.get("title", "")
            snippet = item.get("snippet", "")
            
            if link and validar_relevancia_url(link, titulo, produto):
                resultados.append({
                    'link': link,
                    'titulo': titulo,
                    'snippet': snippet
                })
                
                if len(resultados) >= max_resultados:
                    break
        
        return resultados
        
    except Exception as e:
        print(f"  ⚠ Erro na busca: {str(e)[:50]}")
        return []

# Validar relevância da URL
def validar_relevancia_url(url, titulo, termo_busca):
    """Filtra URLs irrelevantes"""
    
    sites_bloqueados = ["wikipedia", "instagram", "facebook", "youtube", "linkedin", "reclameaqui"]
    
    url_lower = url.lower()
    titulo_lower = titulo.lower()
    termo_lower = termo_busca.lower()
    
    # Bloqueia certos sites
    if any(site in url_lower for site in sites_bloqueados):
        return False
    
    # Prioriza sites de vendas
    sites_vendas = ["amazon", "mercadolivre", "shopee", "magazine", "carrefour", "walmart", "extra"]
    eh_vendas = any(site in url_lower for site in sites_vendas)
    
    # Verifica se o termo aparece no título
    primeira_palavra = termo_busca.split()[0].lower()
    tem_termo = primeira_palavra in titulo_lower or primeira_palavra in url_lower
    
    return tem_termo or eh_vendas

# Extrair preço
def extrair_preco_da_pagina(url):
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True, 
                            headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seletores comuns de preço
        seletores_precos = [
            'span[class*="price"]',
            'span[class*="preco"]',
            'div[class*="price"]',
            'div[class*="preco"]',
            '[itemprop="price"]',
            '.price',
            '.preco',
            '#price',
            'p[class*="valor"]',
            'strong[class*="price"]',
        ]
        
        precos_encontrados = []
        
        for seletor in seletores_precos:
            elementos = soup.select(seletor)
            for elemento in elementos:
                texto = elemento.get_text().strip()
                matches = re.findall(r"R\$\s*(\d+(?:[.,]\d{3})*[.,]\d{2})", texto)
                precos_encontrados.extend(matches)
        
        # Se não encontrou, busca no texto inteiro
        if not precos_encontrados:
            texto_pagina = soup.get_text()
            precos_encontrados = re.findall(r"R\$\s*(\d+(?:[.,]\d{3})*[.,]\d{2})", texto_pagina)
        
        if precos_encontrados:
            return precos_encontrados[0]
        
        return None
        
    except Exception as e:
        print(f"    ✗ Erro: {str(e)[:40]}")
        return None

# Processar produto
def processar_produto(produto, max_sites=3):
    print(f"\n📦 {produto['nome']}")
    
    links = pesquisar(produto['nome'], max_resultados=max_sites * 2)
    
    if not links:
        print("  ⚠ Sem resultados")
        produto['sites'] = []
        return produto
    
    sites_encontrados = []
    
    for item in links:
        # Extrai domínio
        dominio = item['link'].replace('https://', '').replace('http://', '').split('/')[0]
        print(f"  🔍 {dominio}", end=" ")
        
        preco = extrair_preco_da_pagina(item['link'])
        
        if preco:
            print(f"→ R$ {preco}")
        else:
            print("→ ✗")
        
        sites_encontrados.append({
            "url": item["link"],
            "titulo": item["titulo"],
            "preco": preco if preco else "Não encontrado"
        })
        
        # Para quando tem suficientes preços
        if len([s for s in sites_encontrados if s["preco"] != "Não encontrado"]) >= max_sites:
            break
        
        # Pequeno delay para não sobrecarregar
        time.sleep(0.5)
    
    produto['sites'] = sites_encontrados
    return produto

# Processar todos
def processar_todos_produtos(arquivo_entrada, arquivo_saida, max_sites=3):
    produtos = carregar_produtos(arquivo_entrada)
    
    if not produtos:
        print("❌ Nenhum produto para processar")
        return
    
    produtos_atualizados = []
    
    print(f"🚀 Processando {len(produtos)} produtos (SEM LIMITE DE COTA)\n")
    
    for idx, prod in enumerate(produtos, 1):
        print(f"[{idx}/{len(produtos)}]", end="")
        produto_atualizado = processar_produto(prod, max_sites)
        produtos_atualizados.append(produto_atualizado)
        
        # Delay entre produtos para não sobrecarregar
        time.sleep(1)
    
    resultado = {"produtos": produtos_atualizados}
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ Arquivo salvo em: {arquivo_saida}")
    print(f"✅ {len(produtos_atualizados)} produtos processados")

# Executar
if __name__ == "__main__":
    processar_todos_produtos(
        arquivo_entrada="lab\\produto.json",
        arquivo_saida="lab\\produtos_com_precos.json",
        max_sites=3
    )
