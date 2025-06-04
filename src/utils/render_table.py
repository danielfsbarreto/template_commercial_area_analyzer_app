from io import StringIO

import pandas as pd

from models import S3File


def render_table(file: S3File):
    return pd.read_csv(StringIO(file.content)) if file and file.content else None
