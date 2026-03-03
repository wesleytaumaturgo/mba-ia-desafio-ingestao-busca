# 01 — Pipeline RAG: Explicacao Completa

## A Ideia Central (Big Picture)

Imagine que voce tem um livro de 34 paginas. Voce quer fazer perguntas sobre ele e receber respostas precisas. O problema: LLMs como o GPT nao leram seu livro. Eles sabem coisas do treinamento deles, nao do seu PDF.

**RAG resolve isso em 3 passos:**

```
+----------------------------------------------------------------+
|                     FASE UNICA (Ingestao)                      |
|                                                                |
|  PDF --> Texto --> Chunks --> Vetores --> PostgreSQL/pgVector   |
|                                                                |
+----------------------------------------------------------------+

+----------------------------------------------------------------+
|                  CADA PERGUNTA (Busca + Chat)                  |
|                                                                |
|  Pergunta --> Vetor --> Busca no banco --> Top 10 chunks        |
|                              |                                 |
|                              v                                 |
|              Prompt(contexto + regras + pergunta) --> LLM       |
|                                                  --> Resposta   |
+----------------------------------------------------------------+
```

A ingestao acontece **uma vez**. A busca acontece **a cada pergunta**.

---

## FASE 2 — Pipeline de Ingestao

### Passo 1: PyPDFLoader le o PDF e extrai texto por pagina

**O que acontece tecnicamente:**
O `document.pdf` e um arquivo binario — nao e texto puro. O `PyPDFLoader` do LangChain usa a biblioteca `pypdf` para abrir o PDF, decodificar cada pagina e extrair o texto legivel. Cada pagina vira um objeto `Document` com dois campos: `.page_content` (o texto) e `.metadata` (numero da pagina, caminho do arquivo).

```python
# Resultado conceitual:
Document(page_content="Capitulo 1: Introducao a ...", metadata={"page": 0, "source": "document.pdf"})
Document(page_content="A arquitetura de software ...", metadata={"page": 1, "source": "document.pdf"})
# ... 34 documentos (1 por pagina)
```

**Por que PyPDFLoader e nao outra alternativa:**

| Alternativa | Problema |
|---|---|
| Ler o PDF manualmente com `open()` | PDF e binario, nao texto. Voce veria bytes ilegiveis |
| `pdfminer` | Mais poderoso mas complexo demais para texto simples |
| `unstructured` | Excelente para PDFs com tabelas/imagens, mas dependencia pesada |
| OCR (`tesseract`) | Necessario so se o PDF for imagem escaneada, nao texto digital |

PyPDFLoader e a escolha certa aqui: leve, integrado ao LangChain, e suficiente para PDFs com texto digital.

**Impacto se pular ou fizer errado:**
Sem extracao de texto, nao existe pipeline. Se o PDF tiver problemas (escaneado, encoding quebrado), o texto extraido vem lixo e **todo o resto do pipeline herda esse lixo**. E o principio garbage in, garbage out.

---

### Passo 2: RecursiveCharacterTextSplitter divide o texto em chunks

**O que acontece tecnicamente:**
Uma pagina inteira de texto e grande demais para ser util na busca. Se alguem pergunta "o que e microsservico?", voce nao quer retornar 10 paginas inteiras — quer o **paragrafo** que fala sobre isso.

O `RecursiveCharacterTextSplitter` pega o texto de cada pagina e fatia em pedacos menores (chunks) de **1000 caracteres**, com **150 de overlap** (sobreposicao).

O "Recursive" significa que ele tenta cortar nos separadores mais naturais, nesta ordem de prioridade:

```
1.  "\n\n"  -->  Quebra de paragrafo (melhor)
2.  "\n"    -->  Quebra de linha
3.  " "     -->  Espaco entre palavras
4.  ""      -->  Caractere individual (ultimo recurso)
```

**Exemplo visual do overlap:**

```
Chunk 1: [==========1000 chars==========]
Chunk 2:              [====150====][==========1000 chars==========]
                      ^ overlap  ^
```

Os ultimos 150 caracteres do chunk 1 se repetem no inicio do chunk 2. Isso garante que uma frase que cai na fronteira entre dois chunks nao perca contexto.

**Por que 1000 chars / 150 overlap e nao outros valores:**

| Parametro | Valor menor | Valor escolhido | Valor maior |
|---|---|---|---|
| **chunk_size** | 300: chunks pequenos demais, perdem contexto | **1000**: bom equilibrio entre precisao e contexto | 3000: chunks grandes, busca imprecisa, gasta tokens |
| **overlap** | 0: frases cortadas no meio perdem sentido | **150**: ~1-2 frases de continuidade | 500: duplicacao excessiva, desperdicio de storage |

1000 chars equivale a aproximadamente **200-250 tokens** — bem dentro do que o embedding model consegue representar com qualidade.

**Impacto se pular ou fizer errado:**
- **Sem chunking**: embedding de pagina inteira mistura muitos assuntos. A busca retorna "mais ou menos relevante" em vez de "exatamente relevante"
- **Chunks muito pequenos** (100 chars): frases soltas sem contexto. O LLM nao consegue montar uma resposta coerente
- **Chunks muito grandes** (5000 chars): volta ao problema da pagina inteira — a busca perde precisao
- **Sem overlap**: "A arquitetura de micro" | "servicos distribui..." — a frase quebrada perde significado nos dois chunks

---

### Passo 3: OpenAIEmbeddings converte cada chunk em vetor

**O que acontece tecnicamente:**
Aqui esta o coracao do RAG. Cada chunk de texto precisa virar algo que o computador consiga comparar matematicamente. Texto em si nao e comparavel — "cachorro" e "cao" sao strings completamente diferentes, mas significam a mesma coisa.

Um **embedding** e uma lista de numeros (vetor) que representa o **significado** de um texto. O modelo `text-embedding-3-small` da OpenAI converte qualquer texto em um vetor de **1536 dimensoes** — ou seja, uma lista de 1536 numeros decimais.

```python
# Conceitual:
"microsservicos sao componentes independentes" -> [0.023, -0.841, 0.112, ..., 0.445]
#                                                  ^     1536 numeros                ^
```

A magica: textos com **significado parecido** produzem vetores **proximos no espaco**. Textos com significado diferente ficam distantes.

```
"microsservicos sao independentes"  -> vetor A  --+
"servicos autonomos e desacoplados" -> vetor B  --| PROXIMOS (mesma regiao)
                                                  |
"receita de bolo de chocolate"      -> vetor C  --+ DISTANTE (outra regiao)
```

**Por que `text-embedding-3-small` e nao outro modelo:**

| Modelo | Dimensoes | Custo | Qualidade |
|---|---|---|---|
| `text-embedding-3-small` | 1536 | ~$0.02/1M tokens | Boa para a maioria dos casos |
| `text-embedding-3-large` | 3072 | ~$0.13/1M tokens | Melhor, mas 6.5x mais caro |
| Gemini embedding | 768 | Gratis (com limites) | Boa, mas menor dimensionalidade |
| Modelos locais (sentence-transformers) | Varia | Gratis | Precisa de GPU, mais complexo |

Para um projeto academico com 34 paginas, `text-embedding-3-small` e custo-beneficio ideal: barato, rapido e com qualidade suficiente.

**Impacto se pular ou fizer errado:**
- **Sem embedding**: impossivel fazer busca semantica. Voce so teria busca por palavra-chave (CTRL+F glorificado)
- **Modelo diferente na ingestao vs na busca**: os vetores ficam em "espacos" diferentes. E como comparar coordenadas GPS com CEP — nao sao compativeis. **A busca retorna lixo**
- **Modelo muito pequeno (poucas dimensoes)**: perde nuances semanticas, trata textos diferentes como iguais

---

### Passo 4: PGVector.from_documents() armazena tudo no PostgreSQL

**O que acontece tecnicamente:**
O `PGVector.from_documents()` faz tres coisas de uma vez:

1. Cria uma tabela no PostgreSQL com a extensao `pgvector` habilitada
2. Insere cada chunk como uma linha: texto original + vetor de 1536 dimensoes + metadata
3. Cria um indice vetorial para buscas rapidas

```
+--------------------------------------------------------------+
|  Tabela: langchain_pg_embedding                              |
+----------+----------------------+------------+---------------+
| id       | embedding            | document   | cmetadata     |
+----------+----------------------+------------+---------------+
| uuid-1   | [0.023, -0.841, ...] | "Capit..." | {"page": 0}  |
| uuid-2   | [0.117, 0.553, ...]  | "A arq..." | {"page": 0}  |
| uuid-3   | [-0.334, 0.091, ...] | "Micro..." | {"page": 1}  |
| ...      | ...                  | ...        | ...           |
+----------+----------------------+------------+---------------+
```

O banco roda via Docker (`docker-compose.yml`) com a imagem `pgvector/pgvector:pg17`.

**Por que PostgreSQL + pgVector e nao outro banco vetorial:**

| Alternativa | Vantagem | Desvantagem para este projeto |
|---|---|---|
| **pgVector** | Banco relacional que voce ja conhece, com extensao vetorial | Menos otimizado que bancos nativos para bilhoes de vetores |
| Pinecone | SaaS, zero config | Dependencia externa, custo, vendor lock-in |
| ChromaDB | Simples, in-memory | Sem persistencia robusta, escala limitada |
| FAISS | Extremamente rapido | Nao e banco de dados, e so indice em memoria |
| Weaviate/Qdrant | Nativamente vetorial | Infraestrutura extra, complexidade desnecessaria |

Para ~100-200 chunks de um PDF de 34 paginas, pgVector e perfeito: simples, persistente, e roda localmente via Docker.

**Impacto se pular ou fizer errado:**
- **Sem persistencia**: teria que re-embedar o PDF inteiro a cada sessao. Lento e caro (chamadas a API da OpenAI)
- **Sem indice vetorial**: busca por forca bruta — compara a query contra TODOS os vetores. Funciona para 200 chunks, mas nao escala
- **Rodar ingest.py duas vezes sem limpar**: chunks duplicados no banco, respostas com contexto repetido

---

## FASE 3 — Pipeline de Busca + Chat

### Passo 5: Pergunta do usuario e convertida em embedding

**O que acontece tecnicamente:**
Quando o usuario digita "O que sao microsservicos?" no terminal, essa string e enviada para o **mesmo modelo** `text-embedding-3-small` que foi usado na ingestao. O resultado e um vetor de 1536 dimensoes que representa o significado da pergunta.

```python
"O que sao microsservicos?" -> [0.045, -0.782, 0.234, ..., 0.118]
```

Esse vetor da pergunta agora esta no **mesmo espaco matematico** que os vetores dos chunks. Podemos compara-los.

**Por que usar o mesmo modelo:**
Cada modelo de embedding tem seu proprio "idioma numerico". Se voce embeda os chunks com modelo A e a pergunta com modelo B, e como procurar um endereco de Sao Paulo num mapa do Rio de Janeiro. Os numeros nao significam a mesma coisa.

**Impacto se fizer errado:**
- **Modelo diferente**: busca retorna resultados aleatorios. O sistema parece funcionar mas as respostas nao fazem sentido
- **Nao converter a pergunta em embedding**: sem vetor de query, nao existe busca vetorial

---

### Passo 6: similarity_search_with_score busca os k=10 chunks mais proximos

**O que acontece tecnicamente:**
O pgVector calcula a **distancia cosseno** entre o vetor da pergunta e cada vetor armazenado. Distancia cosseno mede o angulo entre dois vetores — quanto menor o angulo, mais parecidos os significados.

```
Query: "O que sao microsservicos?"

Chunk 47: "Microsservicos sao componentes..."      -> score: 0.92  TOP 1
Chunk 12: "A arquitetura de servicos distribui..."  -> score: 0.87  TOP 2
Chunk 51: "Cada servico roda independente..."       -> score: 0.84  TOP 3
...
Chunk 03: "Receita de bolo..."                      -> score: 0.12  IGNORADO
```

Os **10 chunks com maior score** (mais similares) sao retornados.

**Por que k=10 e nao outro numero:**

| Valor de k | Efeito |
|---|---|
| k=1 | Muito pouco contexto. Se o chunk certo ficar em 2o lugar, perde |
| k=3 | Bom para perguntas simples e diretas |
| **k=10** | Cobertura ampla. Captura nuances e multiplas secoes relevantes |
| k=50 | Contexto demais. Gasta tokens, dilui relevancia, confunde o LLM |

10 chunks de ~1000 chars = ~10.000 chars = ~2.500 tokens de contexto. Dentro do budget de um prompt sem desperdicar.

**Por que similaridade cosseno e nao outra metrica:**

| Metrica | Como funciona | Quando usar |
|---|---|---|
| **Cosseno** | Angulo entre vetores (ignora magnitude) | Textos de tamanhos variados — chunks tem tamanhos diferentes |
| Euclidiana | Distancia reta no espaco | Quando magnitude importa |
| Produto interno | Combinacao de angulo + magnitude | Modelos treinados para isso |

Cosseno e o padrao para RAG porque chunks tem tamanhos diferentes e queremos comparar **direcao** (significado), nao **comprimento**.

**Impacto se pular ou fizer errado:**
- **Sem busca vetorial**: teria que passar o PDF inteiro como contexto. Nao cabe no prompt (34 paginas > context window)
- **k muito baixo**: perde informacao relevante, respostas incompletas
- **k muito alto**: contexto poluido com chunks irrelevantes, LLM fica confuso e pode alucinar

---

### Passo 7: Chunks concatenados como CONTEXTO no Prompt Template

**O que acontece tecnicamente:**
Os 10 chunks retornados sao concatenados em uma string e inseridos no template de `src/search.py`:

```
CONTEXTO:
[chunk 1 texto] [chunk 2 texto] ... [chunk 10 texto]

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informacao nao estiver explicitamente no CONTEXTO, responda:
  "Nao tenho informacoes necessarias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
...

PERGUNTA DO USUARIO:
O que sao microsservicos?

RESPONDA A "PERGUNTA DO USUARIO"
```

**Por que essa estrutura de prompt:**

O template tem 3 secoes com papeis distintos:

| Secao | Funcao |
|---|---|
| `CONTEXTO` | A "cola" da prova — o LLM so pode consultar isso |
| `REGRAS` | Grounding — impede alucinacao |
| `EXEMPLOS` | Few-shot — mostra ao LLM como se comportar quando nao sabe |
| `PERGUNTA` | O que o usuario quer saber |

Os exemplos de perguntas fora do contexto ("capital da Franca", "quantos clientes") sao **few-shot examples** — ensinam o modelo a reconhecer e recusar perguntas que o contexto nao cobre.

**Impacto se fizer errado:**
- **Sem regras de grounding**: o LLM inventa respostas usando seu conhecimento de treinamento. Parece correto mas pode ser alucinacao
- **Sem exemplos**: o LLM entende a regra mas nao sabe como aplicar na pratica
- **Contexto antes das regras**: ordem importa. Colocar as regras primeiro pode fazer o LLM "esquecer" elas depois de ler muito contexto

---

### Passo 8: LLM gera resposta (gpt-5-nano, temperature=0)

**O que acontece tecnicamente:**
O prompt montado e enviado ao `gpt-5-nano` com `temperature=0`. O modelo le o contexto, aplica as regras, e gera uma resposta textual.

**Temperature=0** significa que o modelo sempre escolhe o token mais provavel. Sem criatividade, sem variacao. A mesma pergunta com o mesmo contexto produz a **mesma resposta** toda vez.

```
temperature=0.0  -->  Deterministico. Ideal para RAG factual.
temperature=0.7  -->  Criativo. Bom para escrita, ruim para fatos.
temperature=1.0  -->  Muito variavel. Respostas diferentes cada vez.
```

**Por que gpt-5-nano:**

| Modelo | Custo | Velocidade | Qualidade para RAG |
|---|---|---|---|
| **gpt-5-nano** | Muito barato | Muito rapido | Suficiente — o contexto ja traz a resposta |
| gpt-4o | Medio | Rapido | Melhor raciocinio, mas desnecessario aqui |
| gpt-4.5 | Caro | Mais lento | Overkill para extrair informacao de contexto |

Em RAG, o trabalho pesado e do **retrieval**, nao da geracao. O LLM so precisa ler o contexto e formular uma resposta. Um modelo menor e mais barato faz isso bem.

**Impacto se fizer errado:**
- **Temperature alta**: respostas variam entre execucoes. Inconsistente e propenso a alucinacao
- **Modelo muito fraco**: nao segue as regras de grounding, inventa coisas
- **Modelo muito caro**: funciona perfeitamente, mas gasta dinheiro sem necessidade

---

## Resumo Visual do Fluxo Completo

```
                        INGESTAO (uma vez)
                        =================

  document.pdf --> PyPDFLoader --> 34 Documents (1/pagina)
                                        |
                                        v
                               RecursiveCharTextSplitter
                               (1000 chars, 150 overlap)
                                        |
                                        v
                                 ~100-200 chunks
                                        |
                                        v
                              OpenAIEmbeddings
                            (text-embedding-3-small)
                                        |
                                        v
                              ~100-200 vetores [1536d]
                                        |
                                        v
                         +--------------------------+
                         |  PostgreSQL + pgVector   |
                         |  (docker-compose up)     |
                         +--------------------------+

                     BUSCA + CHAT (cada pergunta)
                     ============================

  "O que sao microsservicos?" --> OpenAIEmbeddings --> vetor query [1536d]
                                                            |
                                                            v
                                                   similarity_search
                                                     (cosine, k=10)
                                                            |
                                                            v
                                                     10 chunks mais
                                                      relevantes
                                                            |
                                                            v
                                              +-------------------------+
                                              |   PROMPT TEMPLATE       |
                                              |  CONTEXTO: [10 chunks]  |
                                              |  REGRAS: [grounding]    |
                                              |  PERGUNTA: [user input] |
                                              +-------------------------+
                                                            |
                                                            v
                                                   gpt-5-nano (t=0)
                                                            |
                                                            v
                                                    Resposta no CLI
```
