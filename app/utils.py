from datetime import datetime, timedelta


def obter_hora_brasil():
    return datetime.utcnow() - timedelta(hours=3)
