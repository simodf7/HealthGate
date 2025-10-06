import httpx
from config import URL_SERVICE, ROUTE_SERVICE


## optiamo per il pattern adapter per ridurre il coupling tra ingestion e decision 
## in questo modo ingestion non ha modo di conoscere l'url del decision engine e la route
## in più non deve nemmeno conoscere il modo in cui deve essere formata la richiesta 
## qualora in futuro dovesse cambiare il modo in cui decision chiede i dati 
## basta cambiare questo file

class DecisionClient:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def request(self, payload: dict):
        resp = await self.client.post(f"{URL_SERVICE}{ROUTE_SERVICE}", json=payload)
        resp.raise_for_status()
        return resp.json()


class DecisionAdapter:
    def __init__(self):
        self.client = DecisionClient()

    async def send(self, ingestion_output: str) -> dict:
        """
        L' ingestion_output contiene quello che il servizio di ingestion produce.
        Qui facciamo la 'traduzione' nel formato che il Decision Engine si aspetta.
        """

        payload = {
            "storia" : "", ## storia di rimuovere solo testing
            "sintomi": ingestion_output.get("corrected_text"),   # mapping logico
        }

        # Chiamata effettiva al Decision Engine
        response = await self.client.request(payload)
        return response



