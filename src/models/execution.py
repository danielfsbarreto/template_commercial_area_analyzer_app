from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.s3_file import S3File


class Execution(BaseModel):
    uuid: str
    input_file: Optional[S3File]
    output_file: Optional[S3File]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: Optional[str]
