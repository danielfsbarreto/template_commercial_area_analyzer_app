import asyncio
import json
from base64 import b64decode, b64encode
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from clients import CrewAiClient, S3Client
from models import Execution


class ExecutionsService:
    INPUT_FILE = "input.csv"
    OUTPUT_FILE = "output.csv"

    def __init__(self):
        self.s3 = S3Client()
        self.crewai = CrewAiClient()

    def list_execution_ids(self) -> list[str]:
        return self.s3.find_unique_uuids()

    def find(self, uuid: str) -> Execution:
        files = self.s3.find_files_with(uuid)
        input_file = next(
            (f for f in files if f.key and f.key.endswith(self.INPUT_FILE)), None
        )
        output_file = next(
            (f for f in files if f.key and f.key.endswith(self.OUTPUT_FILE)), None
        )
        return Execution(
            uuid=uuid,
            input_file=input_file,
            output_file=output_file,
            started_at=input_file.last_modified if input_file else None,
            completed_at=output_file.last_modified if output_file else None,
            status="pending" if input_file and not output_file else "completed",
        )

    def start_execution(self, file: bytes):
        def _run_async_status():
            try:
                response = asyncio.run(_check_status_async(kickoff_id))
                _after_execution_callback(uuid, response)
            except Exception as e:
                print(f"Error checking status for {uuid}: {e}")
                raise e

        async def _check_status_async(uuid: str):
            try:
                response = await self.crewai.status(uuid)
                print(f"Status check completed for {uuid}")
                return response
            except Exception as e:
                print(f"Error checking status for {uuid}: {e}")
                return None

        def _after_execution_callback(uuid: str, response):
            result_dict = json.loads(response["result"])
            file = b64decode(result_dict["result_csv_base64"])
            self.s3.upload_file(file, uuid, "output.csv")

        uuid = str(uuid4())
        self.s3.upload_file(file, uuid, "input.csv")
        kickoff_response = self.crewai.kickoff(uuid, b64encode(file).decode("utf-8"))
        kickoff_id = kickoff_response["kickoff_id"]
        return ThreadPoolExecutor(max_workers=3).submit(_run_async_status)
