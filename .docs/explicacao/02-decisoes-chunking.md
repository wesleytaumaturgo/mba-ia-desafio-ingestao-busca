# 02 — Decisoes de Chunking: Documento de Referencia

> Documento de decisao tecnica (ADR) para consulta futura.
> Projeto: MBA IA — Desafio Ingestao e Busca

---

## Parametros Definidos

| Parametro | Valor | Unidade |
|---|---|---|
| `chunk_size` | 1000 | caracteres |
| `chunk_overlap` | 150 | caracteres |
| `splitter` | `RecursiveCharacterTextSplitter` | langchain-text-splitters |

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)
```

---

## 1. chunk_size = 1000 — Por que 1000 e nao 500 ou 2000?

### O Trade-off Central

Chunking e um equilibrio entre **precisao de busca** e **contexto suficiente para o LLM**. Chunks menores sao mais precisos na busca, mas podem nao ter informacao suficiente para o LLM gerar uma boa resposta. Chunks maiores dao mais contexto, mas misturam assuntos e a busca perde foco.

```
                    PRECISAO DE BUSCA
                         ^
                         |
              500 chars  *  <-- alta precisao, pouco contexto
                         |
             1000 chars  |  *  <-- equilibrio
                         |
             2000 chars  |        *  <-- baixa precisao, muito contexto
                         +-------------------> CONTEXTO DISPONIVEL
```

### Comparacao Detalhada

| chunk_size | Tokens (~) | Precisao de busca | Contexto para LLM | Custo de embedding | Uso ideal |
|---|---|---|---|---|---|
| **300** | ~75 | Muito alta | Insuficiente — frases soltas | Alto (muitos chunks) | Busca de fatos atomicos |
| **500** | ~125 | Alta | Limitado — paragrafos curtos | Medio-alto | PDFs tecnicos densos |
| **1000** | ~250 | **Boa** | **Suficiente — 1-3 paragrafos** | **Medio** | **Uso geral (nosso caso)** |
| **1500** | ~375 | Media | Amplo — secoes parciais | Medio-baixo | Textos narrativos |
| **2000** | ~500 | Baixa | Excessivo — mistura assuntos | Baixo (poucos chunks) | Documentos curtos |

### Por que 1000 e o certo para este projeto

**Sobre o documento**: `document.pdf` tem 34 paginas de conteudo tecnico academico (MBA). Textos academicos tem paragrafos de tamanho medio (~200-400 chars), com conceitos que se explicam em 1-3 paragrafos.

**1000 caracteres (~250 tokens) permite:**
- Capturar um conceito completo com sua explicacao
- Caber confortavelmente no embedding model (text-embedding-3-small suporta ate 8191 tokens)
- Retornar 10 chunks (k=10) sem estourar o prompt (~2500 tokens de contexto)

**500 seria pequeno demais porque:**
- Conceitos academicos precisam de mais espaco para serem auto-contidos
- Definicao + exemplo ficam em chunks separados — a busca retorna a definicao sem o exemplo
- Mais chunks = mais chamadas de embedding = custo desnecessario

**2000 seria grande demais porque:**
- Dois assuntos diferentes caem no mesmo chunk
- A busca por "microsservicos" retorna um chunk que fala 50% de microsservicos e 50% de monolitos
- O LLM recebe contexto poluido e pode misturar conceitos na resposta

### Calculo para o nosso PDF

```
PDF: 34 paginas
Caracteres estimados por pagina: ~2000-3000
Total estimado: ~85.000 caracteres

Com chunk_size=1000 e overlap=150:
  Chunks efetivos: ~85.000 / (1000 - 150) = ~100 chunks

Com chunk_size=500:
  Chunks efetivos: ~85.000 / (500 - 150) = ~243 chunks (2.4x mais)

Com chunk_size=2000:
  Chunks efetivos: ~85.000 / (2000 - 150) = ~46 chunks (metade)
```

---

## 2. chunk_overlap = 150 — Por que 150?

### O Problema que Overlap Resolve

Sem overlap, frases que caem na fronteira entre dois chunks sao cortadas. O significado se perde nos dois lados.

```
SEM OVERLAP (overlap=0):
  Chunk 1: "...A arquitetura de micro"
  Chunk 2: "servicos distribui a logica em componentes independentes..."
                                    ^
                       Frase cortada — nenhum chunk tem a frase completa

COM OVERLAP (overlap=150):
  Chunk 1: "...A arquitetura de microsservicos distribui a logica em com"
  Chunk 2: "microsservicos distribui a logica em componentes independentes..."
            |_________ 150 chars repetidos _________|
                       ^
                       Ambos os chunks tem a frase completa
```

### Por que 150 e nao outro valor

O overlap e definido como **porcentagem do chunk_size**. O nosso e 15% (150/1000).

| Overlap | % do chunk | Efeito | Problema |
|---|---|---|---|
| **0** | 0% | Nenhuma redundancia | Frases cortadas perdem significado |
| **50** | 5% | Minimo — ~1 frase curta | Insuficiente para frases longas |
| **150** | **15%** | **~1-2 frases completas** | **Nenhum — equilibrio ideal** |
| **300** | 30% | ~3-4 frases | Redundancia excessiva, chunks quase iguais |
| **500** | 50% | Metade do chunk repetida | Desperdicio de storage e embedding |

### A Regra dos 10-20%

A literatura de RAG recomenda overlap entre **10% e 20%** do chunk_size:

```
chunk_size=1000 --> overlap ideal: 100 a 200
                    nosso valor: 150 (15%) -- dentro da faixa
```

**Por que nao menos que 100:**
Uma frase em portugues academico tem em media 80-150 caracteres. Com overlap de 50, metade das frases de fronteira ainda seriam cortadas.

**Por que nao mais que 200:**
Overlap de 200 significa que 20% de cada chunk e duplicado. Com 100 chunks, sao ~20 chunks-equivalentes de dados repetidos sendo embedados e armazenados sem necessidade.

### Impacto no armazenamento

```
100 chunks x 1000 chars = 100.000 chars de texto armazenado
Desses, ~15.000 chars sao overlap repetido (15%)

Se overlap fosse 500 (50%):
100.000 chars armazenados, ~50.000 sao repeticao
(e precisaria de ~170 chunks em vez de 100)
```

---

## 3. Por que RecursiveCharacterTextSplitter e nao CharacterTextSplitter?

### A Diferenca Fundamental

Ambos dividem texto em chunks de tamanho fixo. A diferenca e **onde** cortam.

**CharacterTextSplitter** — corta em um unico separador:

```python
# Usa apenas "\n\n" como separador
# Se nao encontrar "\n\n" dentro de 1000 chars, corta no limite exato
CharacterTextSplitter(separator="\n\n", chunk_size=1000)
```

**RecursiveCharacterTextSplitter** — tenta multiplos separadores em cascata:

```python
# Tenta cortar nesta ordem de prioridade:
# 1. "\n\n" (paragrafo)  -- melhor corte possivel
# 2. "\n"   (linha)      -- segundo melhor
# 3. " "    (palavra)    -- aceitavel
# 4. ""     (caractere)  -- ultimo recurso
RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
```

### Exemplo Pratico com Texto Real

Suponha este texto de 1200 chars que precisa ser dividido (chunk_size=1000):

```
Arquitetura de Microsservicos

Microsservicos sao componentes de software independentes
que se comunicam via APIs. Cada servico encapsula uma
funcionalidade de negocio especifica.

Vantagens dos Microsservicos

Escalabilidade independente permite que cada servico
escale conforme sua demanda. Deploy independente reduz
risco de falhas em cascata. Equipes autonomas podem
trabalhar em servicos diferentes simultaneamente.

Desvantagens dos Microsservicos

Complexidade operacional aumenta significativamente.
Comunicacao entre servicos introduz latencia de rede.
Monitoramento e debugging tornam-se mais desafiadores
em sistemas distribuidos.
```

**CharacterTextSplitter (separator="\n\n") cortaria assim:**

```
Chunk 1 (ate 1000 chars):
  "Arquitetura de Microsservicos\n\n
   Microsservicos sao componentes...\n\n
   Vantagens dos Microsservicos\n\n
   Escalabilidade independente permite..."
   ^-- corta aqui no "\n\n" mais proximo de 1000

Chunk 2:
  "Desvantagens dos Microsservicos\n\n
   Complexidade operacional..."
```

Funciona neste caso, mas **se nao houver "\n\n" dentro de 1000 chars** (paragrafo gigante), ele corta no char 1000 exato — no meio de uma palavra.

**RecursiveCharacterTextSplitter cortaria assim:**

```
Chunk 1 (ate 1000 chars):
  Tenta "\n\n" --> encontra! Corta no final de "Vantagens..."

Chunk 2:
  Tenta "\n\n" --> encontra! Corta no final de "Desvantagens..."

SE nao encontrasse "\n\n":
  Tenta "\n" --> corta no fim de uma linha
SE nao encontrasse "\n":
  Tenta " " --> corta entre duas palavras (nunca no meio de uma)
```

### Tabela Comparativa

| Criterio | CharacterTextSplitter | RecursiveCharacterTextSplitter |
|---|---|---|
| Separadores | Um unico | Multiplos em cascata |
| Respeita paragrafos | Sim (se configurado) | Sim (por padrao) |
| Fallback inteligente | Nao — corta no limite exato | Sim — desce para separador menor |
| Corta palavras no meio | Pode acontecer | Praticamente nunca |
| Configuracao | Precisa definir separador | Funciona bem com defaults |
| Recomendado para | Textos muito estruturados | **Uso geral (nosso caso)** |

### Veredicto

`RecursiveCharacterTextSplitter` e o **padrao recomendado pelo LangChain** para a maioria dos casos. Ele e mais robusto porque nao depende de um unico separador. Se o PDF tiver paragrafos longos sem "\n\n", o Recursive ainda corta de forma inteligente. O Character cortaria no meio de uma palavra.

---

## 4. Quando Mudar Esses Parametros?

### Guia de Ajuste por Tipo de Documento

```
+-----------------------------------------------------------------------+
|  TIPO DE DOCUMENTO         | chunk_size | chunk_overlap | Por que     |
+----------------------------+------------+---------------+-------------+
|  PDF tecnico denso         |  500-800   |   100-150     | Conceitos   |
|  (specs, APIs, formulas)   |            |               | curtos e    |
|                            |            |               | precisos    |
+----------------------------+------------+---------------+-------------+
|  PDF academico (nosso)     |  1000      |   150         | Equilibrio  |
|  (artigos, dissertacoes)   |            |               | entre       |
|                            |            |               | contexto e  |
|                            |            |               | precisao    |
+----------------------------+------------+---------------+-------------+
|  PDF narrativo             |  1200-1500 |   200-250     | Ideias se   |
|  (livros, relatorios)      |            |               | desenvolvem |
|                            |            |               | em blocos   |
|                            |            |               | maiores     |
+----------------------------+------------+---------------+-------------+
|  FAQ / Q&A                 |  300-500   |   50-100      | Cada par    |
|  (perguntas e respostas)   |            |               | pergunta/   |
|                            |            |               | resposta e  |
|                            |            |               | atomico     |
+----------------------------+------------+---------------+-------------+
|  Codigo fonte              |  1500-2000 |   200         | Funcoes e   |
|  (scripts, configs)        |            |               | classes     |
|                            |            |               | precisam    |
|                            |            |               | de contexto |
+----------------------------+------------+---------------+-------------+
```

### Sinais de que os Parametros Precisam de Ajuste

**Sintoma: Respostas cortam no meio da frase**
```
Diagnostico: overlap insuficiente
Acao: aumentar chunk_overlap de 150 para 200-250
```

**Sintoma: Busca retorna chunks irrelevantes junto com relevantes**
```
Diagnostico: chunk_size grande demais — mistura assuntos
Acao: diminuir chunk_size de 1000 para 700-800
```

**Sintoma: LLM responde "nao tenho informacao" mas a resposta esta no PDF**
```
Diagnostico: informacao dividida entre chunks que nao foram recuperados
Acao: aumentar chunk_overlap OU aumentar k (numero de chunks retornados)
```

**Sintoma: Respostas sao genericas e rasas**
```
Diagnostico: chunks pequenos demais — so pegam definicao, nao o detalhe
Acao: aumentar chunk_size de 1000 para 1200-1500
```

**Sintoma: Custo de embedding esta alto demais**
```
Diagnostico: chunks muito pequenos geram muitos vetores
Acao: aumentar chunk_size (reduz numero total de chunks)
```

---

## 5. Como o chunk_size Afeta o Custo?

### Formula do Custo de Ingestao

```
Custo = (numero_de_chunks x tokens_por_chunk x preco_por_token)
```

Para text-embedding-3-small ($0.02 por 1M tokens):

| chunk_size | Chunks estimados | Tokens totais | Custo de embedding |
|---|---|---|---|
| 500 | ~243 | ~30.375 | $0.0006 |
| **1000** | **~100** | **~25.000** | **$0.0005** |
| 2000 | ~46 | ~23.000 | $0.0005 |

### Observacao Importante sobre Custo

Para o nosso PDF de 34 paginas, o custo e **irrelevante** — menos de $0.001 em qualquer configuracao. A diferenca entre 500 e 2000 chars e fracao de centavo.

**O custo so importa quando:**
- Milhares de PDFs sendo ingeridos regularmente
- Documentos muito grandes (livros, manuais de 500+ paginas)
- Modelo de embedding caro (text-embedding-3-large custa 6.5x mais)

### Onde o chunk_size realmente impacta o custo: na BUSCA

Cada pergunta do usuario gera:
1. **1 chamada de embedding** para a query (custo fixo, independe de chunk_size)
2. **Tokens de contexto no prompt do LLM** (aqui chunk_size importa)

```
k=10 chunks retornados:

chunk_size=500:  10 x 125 tokens = 1.250 tokens de contexto
chunk_size=1000: 10 x 250 tokens = 2.500 tokens de contexto  <-- nosso caso
chunk_size=2000: 10 x 500 tokens = 5.000 tokens de contexto

Com gpt-5-nano, a diferenca de custo por pergunta e minima.
Mas em 10.000 perguntas/dia, chunk_size=2000 custa 2x mais que 1000.
```

### Resumo de Custo

```
Para nosso projeto (34 paginas, uso academico):
  Custo de embedding total: < $0.001
  Custo por pergunta: negligivel
  Conclusao: chunk_size=1000 e ideal pelo QUALIDADE, nao pelo custo

Para producao (milhares de docs, muitos usuarios):
  chunk_size menor = mais chunks = mais embedding = mais custo de ingestao
  chunk_size maior = mais tokens por prompt = mais custo por pergunta
  Equilibrio: 800-1200 chars e a faixa mais custo-eficiente
```

---

## Decisao Final

```
+---------------------------------------------------------------------+
|  PARAMETRO                  |  VALOR  |  STATUS                     |
+-----------------------------+---------+-----------------------------+
|  chunk_size                 |  1000   |  APROVADO — uso geral       |
|  chunk_overlap              |  150    |  APROVADO — 15% do chunk    |
|  splitter                   |  RCTS   |  APROVADO — padrao LangChain|
|  separators (default)       |  padrao |  APROVADO — \n\n,\n, ,""   |
+-----------------------------+---------+-----------------------------+
|                                                                     |
|  Proxima revisao: apos testes com o PDF real (Fase 2)               |
|  Criterio de mudanca: respostas cortadas ou busca imprecisa         |
+---------------------------------------------------------------------+
```
