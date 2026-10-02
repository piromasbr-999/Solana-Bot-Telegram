import httpx
import os

WEBACY_API_KEY = os.getenv("WEBACY_API_KEY")
BASE_URL = "https://api.dd.xyz/v1"

async def check_address_risk(address: str):
    # Se ainda não houver chave real no .env, retorna dados simulados para teste
    if not WEBACY_API_KEY or WEBACY_API_KEY == "tua_chave_aqui_quando_chegar":
        return {
            "risk_score": 85,
            "flags": [
                "Modo de Teste: API Key ainda não configurada",
                "Alta concentração de tokens identificada",
                "Contrato com histórico de atividade suspeita"
            ]
        }

    # Chamada real para a API da Webacy quando a chave chegar
    headers = {
        "Accept": "application/json",
        "X-API-KEY": WEBACY_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/threat-risks/{address}", headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erro na requisição da API: {e}")
            return None

async def check_url_risk(url: str):
    if not WEBACY_API_KEY or WEBACY_API_KEY == "tua_chave_aqui_quando_chegar":
        return {
            "is_malicious": True
        }

    headers = {
        "Accept": "application/json",
        "X-API-KEY": WEBACY_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/url-risk", headers=headers, json={"url": url})
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erro na requisição da API: {e}")
            return None