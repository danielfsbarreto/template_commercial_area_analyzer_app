from base64 import b64encode

from models import S3File


def download_link(file: S3File):
    if file and file.url:
        return f"""
        <a href="{file.url}" target="_blank">
            <img src="data:image/svg+xml;base64,{b64encode(open("src/public/download.svg", "rb").read()).decode()}" width="18" height="18" alt="Download"/>
        </a>
        """
    else:
        return "N/A"
