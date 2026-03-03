#!/usr/bin/env bash
set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
die()      { echo -e "${RED}[ERRO]${NC} $*" >&2; exit 1; }

# Mapas
declare -A PHASE_NAMES
PHASE_NAMES[0]="bootstrap"
PHASE_NAMES[1]="descoberta"
PHASE_NAMES[2]="ingestao"
PHASE_NAMES[3]="busca-chat"
PHASE_NAMES[4]="polish"

declare -A PHASE_TITLES
PHASE_TITLES[0]="Fase 0 — Bootstrap: ambiente, Docker e dependencias"
PHASE_TITLES[1]="Fase 1 — Descoberta: pipeline RAG e decisoes de chunking"
PHASE_TITLES[2]="Fase 2 — Ingestao: PDF → chunks → embeddings → pgVector"
PHASE_TITLES[3]="Fase 3 — Busca + Chat: similarity search e CLI interativo"
PHASE_TITLES[4]="Fase 4 — Polish: README, validacao e entrega"

declare -A DELIVERABLES
DELIVERABLES[0]="venv ativo, Docker rodando, deps instaladas, .env configurado"
DELIVERABLES[1]="Pipeline RAG entendido, chunking documentado, prompt template projetado"
DELIVERABLES[2]="ingest.py funcional, chunks no pgVector, validacao no banco"
DELIVERABLES[3]="search.py + chat.py, CLI responde + rejeita, grounding OK"
DELIVERABLES[4]="README final, validacao E2E, commit pushed, repo publico"

declare -A GATES
GATES[0]="docker compose ps + python -c 'import langchain'"
GATES[1]="Explicar RAG em 3 frases"
GATES[2]="python src/ingest.py + SELECT count(*) FROM langchain_pg_embedding"
GATES[3]="python -m src.chat — responde no contexto e rejeita fora"
GATES[4]="Validacao E2E completa + git push origin main"

# --- Validar argumento ---
PHASE="${1:-}"
[[ -z "$PHASE" ]] && die "Uso: $0 {0|1|2|3|4}"
[[ ! "$PHASE" =~ ^[0-4]$ ]] && die "Fase deve ser 0, 1, 2, 3 ou 4"
PHASE=$((10#$PHASE))

NAME="${PHASE_NAMES[$PHASE]}"
TITLE="${PHASE_TITLES[$PHASE]}"
DELIV="${DELIVERABLES[$PHASE]}"
GATE="${GATES[$PHASE]}"

BRANCH_ATUAL="fase-${PHASE}-${NAME}"
BASE_BRANCH="main"

log_info "Fase $PHASE: $NAME"
log_info "Branch: $BRANCH_ATUAL"

# --- Verificar gh ---
command -v gh >/dev/null 2>&1 || die "gh nao encontrado. Instale: sudo apt install gh && gh auth login"

# --- Garantir que estamos na branch da fase ---
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
if [[ "$CURRENT_BRANCH" != "$BRANCH_ATUAL" ]]; then
  if git show-ref --verify --quiet "refs/heads/$BRANCH_ATUAL" 2>/dev/null; then
    log_info "Checkout para $BRANCH_ATUAL"
    git checkout "$BRANCH_ATUAL"
  else
    log_info "Criando branch $BRANCH_ATUAL a partir de $BASE_BRANCH"
    git fetch origin "$BASE_BRANCH" 2>/dev/null || true
    git checkout -b "$BRANCH_ATUAL" "$BASE_BRANCH" 2>/dev/null || git checkout -b "$BRANCH_ATUAL"
  fi
fi

# --- Commit se houver mudancas ---
if [[ -n $(git status -s) ]]; then
  log_info "Mudancas nao commitadas encontradas. Commitando..."
  git add -A
  git commit -m "feat(fase-${PHASE}): ${NAME} concluida"
  log_ok "Commit criado"
else
  log_info "Nenhuma mudanca pendente"
fi

# --- Push ---
log_info "Push para origin $BRANCH_ATUAL"
git push -u origin "$BRANCH_ATUAL" || git push origin "$BRANCH_ATUAL"
log_ok "Push concluido"

# --- Montar corpo do PR ---
PR_BODY="## Entregaveis
- [ ] ${DELIV}

## Gate de verificacao
\`\`\`
${GATE}
\`\`\`"

# --- Criar PR ---
log_info "Criando PR..."
PR_URL=$(gh pr create \
  --title "$TITLE" \
  --body "$PR_BODY" \
  --base "$BASE_BRANCH" \
  --head "$BRANCH_ATUAL" \
  2>&1) || die "Falha ao criar PR. Verifique: gh auth status"

log_ok "PR criado: $PR_URL"

# --- Proxima fase (se fase < 4) ---
if [[ $PHASE -lt 4 ]]; then
  NEXT_PHASE=$((PHASE + 1))
  NEXT_NAME="${PHASE_NAMES[$NEXT_PHASE]}"
  NEXT_BRANCH="fase-${NEXT_PHASE}-${NEXT_NAME}"
  log_info "Criando branch da proxima fase: $NEXT_BRANCH"
  git checkout "$BASE_BRANCH" 2>/dev/null || git checkout main
  git pull origin "$BASE_BRANCH" 2>/dev/null || true
  git checkout -b "$NEXT_BRANCH"
  log_ok "Branch $NEXT_BRANCH criada. Proxima fase: $NEXT_PHASE — $NEXT_NAME"
fi

# --- Resumo ---
echo ""
echo -e "${GREEN}=== Resumo ===${NC}"
echo "PR: $PR_URL"
echo "Branch: $BRANCH_ATUAL → mergear em $BASE_BRANCH"
[[ $PHASE -lt 4 ]] && echo "Proxima branch: fase-$((PHASE + 1))-${PHASE_NAMES[$((PHASE + 1))]}"
log_ok "Concluido"
