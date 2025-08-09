# chatbot_sindico.py

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import uuid

app = FastAPI(title="Chatbot Síndico Profissional")

# --- Banco de dados em memória ---
solicitacoes = []

# --- Tabela de prioridades (mock) ---
tabela_prioridades = {
    ("Elétrica", "Lâmpada queimada"): {"prioridade": 3, "tempo_max_horas": 5},
    ("Hidráulica", "Cano estourado"): {"prioridade": 0, "tempo_max_horas": 2},
}

# --- Models ---
class NovaSolicitacao(BaseModel): 
    morador: str
    predio: str
    categoria: str
    problema: str

class AtualizacaoStatus(BaseModel):
    id: str
    resolvido: bool
    novo_prazo_horas: Optional[int] = None

# --- Função para simular notificação ---
def notificar_sindico(solicitacao):
    print(f"[NOTIFICAÇÃO] Nova solicitação PRIORIDADE {solicitacao['prioridade']}:")
    print(f"  Prédio: {solicitacao['predio']} | Problema: {solicitacao['problema']}")
    print(f"  Tempo máximo de resposta: {solicitacao['tempo_max']}h")

def verificar_prazo(solicitacao):
    tempo_limite = solicitacao['criado_em'] + timedelta(hours=solicitacao['tempo_max'])
    if datetime.now() > tempo_limite and not solicitacao['resolvido']:
        print(f"[LEMBRETE] A solicitação de {solicitacao['morador']} está atrasada!")

# --- Endpoints ---

@app.post("/solicitacao")
def nova_solicitacao(data: NovaSolicitacao, background_tasks: BackgroundTasks):
    chave = (data.categoria, data.problema)
    prioridade_info = tabela_prioridades.get(chave, {"prioridade": 4, "tempo_max_horas": 12})

    solicitacao = {
        "id": str(uuid.uuid4()),
        "morador": data.morador,
        "predio": data.predio,
        "categoria": data.categoria,
        "problema": data.problema,
        "prioridade": prioridade_info["prioridade"],
        "tempo_max": prioridade_info["tempo_max_horas"],
        "criado_em": datetime.now(),
        "resolvido": False
    }

    solicitacoes.append(solicitacao)
    notificar_sindico(solicitacao)

    # agendamento simples para verificação futura
    background_tasks.add_task(verificar_prazo, solicitacao)

    return {"mensagem": "Solicitação registrada", "id": solicitacao["id"]}

@app.post("/atualizar-status")
def atualizar_status(data: AtualizacaoStatus):
    for s in solicitacoes:
        if s['id'] == data.id:
            if data.resolvido:
                s['resolvido'] = True
                return {"mensagem": "Solicitação marcada como resolvida"}
            elif data.novo_prazo_horas:
                s['tempo_max'] = data.novo_prazo_horas
                return {"mensagem": f"Novo prazo definido: {data.novo_prazo_horas}h"}

    return {"erro": "Solicitação não encontrada"}

@app.get("/pendentes", response_model=List[dict])
def listar_pendentes():
    return [s for s in solicitacoes if not s['resolvido']]

@app.get("/todas")
def listar_todas():
    return solicitacoes
