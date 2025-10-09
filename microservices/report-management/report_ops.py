from config import ROUTE, SERVICE_URL
from validation import Report
import httpx


class AuthClient:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def request(self, param: int):
        resp = await self.client.get(f"{SERVICE_URL}{ROUTE}/{param}")
        resp.raise_for_status()
        return resp.json()


class AuthAdapter:
    def __init__(self):
        self.client = AuthClient()

    async def send(self, input) -> dict:

        param = input['patient_id']
        response = await self.client.request(param)
        return response



async def get_anagrafica(report: Report): 
    adapter = AuthAdapter()
    response = await adapter.send(report)
    print(response)
    return {
        "social_sec_number": response['social_sec_number'],
        "firstname": response['firstname'],
        "lastname": response['lastname'],
        "birth_date": response['birth_date'],  # converto la data in stringa ISO
        "sex": response['sex'],
        "birth_place": response['birth_place']
    }
