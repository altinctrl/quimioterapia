from enum import Enum

class Turno(str, Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"

class StatusPaciente(str, Enum):
    agendado = "agendado"
    em_triagem = "em-triagem"
    aguardando_exame = "aguardando-exame"
    aguardando_medicamento = "aguardando-medicamento"
    em_infusao = "em-infusao"
    pos_qt = "pos-qt"
    intercorrencia = "intercorrencia"
    suspenso = "suspenso"
    concluido = "concluido"

class StatusFarmacia(str, Enum):
    pendente = "pendente"
    em_preparacao = "em-preparacao"
    pronta = "pronta"
    enviada = "enviada"

class ViaAdministracao(str, Enum):
    IV = "IV"
    BIC = "BIC"
    Bolus = "Bolus"
    SC = "SC"
    IM = "IM"
    VO = "VO"
    Topico = "Tópico"