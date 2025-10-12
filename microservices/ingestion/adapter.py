from typing import Any, Dict
import httpx
from config import URL_SERVICE, ROUTE_SERVICE
import logging

logger = logging.getLogger(__name__)
## optiamo per il pattern adapter per ridurre il coupling tra ingestion e decision 
## in questo modo ingestion non ha modo di conoscere l'url del decision engine e la route
## in più non deve nemmeno conoscere il modo in cui deve essere formata la richiesta 
## qualora in futuro dovesse cambiare il modo in cui decision chiede i dati 
## basta cambiare questo file

class DecisionClientError(Exception):
    """Errore generico nel client Decision."""
    pass


class DecisionClient:
    def __init__(self, timeout: float = 10.0):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def request(self, headers, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.debug(f"[DecisionClient] Invio richiesta a {URL_SERVICE}{ROUTE_SERVICE} con payload: {payload}")

            resp = await self.client.post(f"{URL_SERVICE}{ROUTE_SERVICE}", headers=headers, json=payload)
            resp.raise_for_status()

            logger.debug(f"[DecisionClient] Risposta ricevuta: {resp.text}")
            return resp.json()

        except httpx.RequestError as e:
            # errore di connessione, DNS, timeout, ecc.
            logger.error(f"[DecisionClient] Errore di rete: {str(e)}")
            raise DecisionClientError(f"Errore di rete nel contattare Decision Engine: {str(e)}") from e

        except httpx.HTTPStatusError as e:
            # il server ha risposto ma con status 4xx o 5xx
            logger.error(f"[DecisionClient] Errore HTTP {e.response.status_code}: {e.response.text}")
            raise DecisionClientError(
                f"Decision Engine ha risposto con errore {e.response.status_code}: {e.response.text}"
            ) from e

        except Exception as e:
            # qualsiasi altro errore imprevisto
            logger.exception("[DecisionClient] Errore imprevisto")
            raise DecisionClientError(f"Errore imprevisto nel client Decision: {str(e)}") from e

    async def close(self):
        await self.client.aclose()



class DecisionAdapter:
    def __init__(self):
        self.client = DecisionClient()

    async def send(self, headers, ingestion_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        L'ingestion_output contiene quello che il servizio di ingestion produce.
        Qui facciamo la 'traduzione' nel formato che il Decision Engine si aspetta.
        """

   
        corrected_text = ingestion_output.get("corrected_text")
        

        new_headers = {"X-User-Id": headers["X-User-Id"], "Authorization": headers["Authorization"]}
        payload = {"sintomi": corrected_text}

        try:
            response = await self.client.request(headers=new_headers, payload=payload)
            return response

        except DecisionClientError as e:
            # Log di alto livello — utile per capire dove è fallita la catena
            logger.error(f"[DecisionAdapter] Errore nel DecisionClient: {str(e)}")
            raise

        except Exception as e:
            logger.exception("[DecisionAdapter] Errore inatteso durante l'invio")
            raise DecisionClientError(f"Errore inatteso nel DecisionAdapter: {str(e)}") from e



