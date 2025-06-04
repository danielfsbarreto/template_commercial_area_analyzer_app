import asyncio
import os

import aiohttp
import requests


class CrewAiClient:
    CREWAI_API_URL = os.getenv("CREWAI_URL")
    CREWAI_API_BEARER_TOKEN = os.getenv("CREWAI_API_BEARER_TOKEN")

    def kickoff(self, id: str, companies_csv_base64: str):
        response = requests.post(
            f"{self.CREWAI_API_URL}/kickoff",
            json={
                "inputs": {
                    "id": id,
                    "companies_csv_base64": companies_csv_base64,
                }
            },
            headers=self._headers,
        )
        response.raise_for_status()
        return response.json()

    async def status(self, id: str):
        max_attempts = 120
        attempts = 0

        async with aiohttp.ClientSession() as session:
            while attempts < max_attempts:
                try:
                    async with session.get(
                        f"{self.CREWAI_API_URL}/status/{id}", headers=self._headers
                    ) as response:
                        response.raise_for_status()
                        response_json = await response.json()

                        if response_json.get("state") == "SUCCESS":
                            return response_json

                        await asyncio.sleep(1)
                        attempts += 1

                except Exception as e:
                    print(f"Error checking status: {e}")
                    await asyncio.sleep(1)
                    attempts += 1

    @property
    def _headers(self):
        return {"Authorization": f"Bearer {self.CREWAI_API_BEARER_TOKEN}"}
