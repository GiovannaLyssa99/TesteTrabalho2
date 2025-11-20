import requests
from app.infra.config import Config

class CrawlerService:

    def listar_chamadas_publicas(self, list_request):
        """
        Faz uma requisição POST para listar chamadas públicas.
        """
        url = f"{Config.BASE_URL_API}/chamada-publica/listar"
        
        # payload = {
        #     "filters": filtros or {},
        #     "pagination": {
        #         "page": pagina,
        #         "size": tamanho
        #     }
        # }

        try:
            response = requests.post(url, json=list_request.dict(), verify=False)
            response.raise_for_status()  # lança exceção se o status for >= 400
            data = response.json()
            # Aqui assumimos que o JSON tem um campo 'content' com a lista
            return data.get("content", [])
        except requests.RequestException as e:
            print(f"Erro ao chamar a API: {e}")
            return None