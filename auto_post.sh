#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/auto_post.log"

export TZ='America/Sao_Paulo'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

seconds_until_2pm() {
    local current_hour=$(date +%H)
    local current_minute=$(date +%M)
    local current_second=$(date +%S)
    
    local current_seconds=$((current_hour * 3600 + current_minute * 60 + current_second))
    local target_seconds=$((14 * 3600))
    
    if [ $current_seconds -lt $target_seconds ]; then
        echo $((target_seconds - current_seconds))
    else
        echo $((86400 - current_seconds + target_seconds))
    fi
}

run_scripts() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Iniciando execução automática${NC}"
    log "${GREEN}Horário: $(date '+%d/%m/%Y %H:%M:%S') (Brasília)${NC}"
    log "${GREEN}========================================${NC}"
    
    cd "$PROJECT_DIR" || {
        log "${RED}Erro: Não foi possível acessar o diretório $PROJECT_DIR${NC}"
        return 1
    }
    
    log "${YELLOW}Executando: node getsources.js${NC}"
    if node getsources.js >> "$LOG_FILE" 2>&1; then
        log "${GREEN}getsources.js executado com sucesso${NC}"
    else
        log "${RED}Erro ao executar getsources.js${NC}"
        return 1
    fi
    
    sleep 5
    
    log "${YELLOW}Executando: python posting.py${NC}"
    if python3 posting.py >> "$LOG_FILE" 2>&1; then
        log "${GREEN}posting.py executado com sucesso${NC}"
    else
        log "${RED}Erro ao executar posting.py${NC}"
        return 1
    fi
    
    log "${GREEN}========================================${NC}"
    log "${GREEN}Ciclo concluído com sucesso!${NC}"
    log "${GREEN}========================================${NC}"
}

main() {
    log "${BLUE}BOT DE POSTAGEM AUTOMÁTICA${NC}"
    log "${BLUE}Horário: 14h (Brasília)${NC}"
    log ""
    log "${GREEN}Diretório: $PROJECT_DIR${NC}"
    log "${GREEN}Log: $LOG_FILE${NC}"
    log "${GREEN}Timezone: $(date +%Z) (UTC$(date +%z))${NC}"
    log ""
    
    while true; do
        local wait_seconds=$(seconds_until_2pm)
        local next_run=$(date -d "+${wait_seconds} seconds" '+%d/%m/%Y às %H:%M:%S')
        
        log "${BLUE}Aguardando... Próxima execução: $next_run${NC}"
        
        sleep "$wait_seconds"
        run_scripts
        sleep 60
    done
}

trap 'echo -e "\n"; log "${RED}Script interrompido pelo usuário${NC}"; exit 0' INT TERM

if ! command -v node &> /dev/null; then
    log "${RED}Erro: Node.js não está instalado${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    log "${RED}Erro: Python3 não está instalado${NC}"
    exit 1
fi

main
