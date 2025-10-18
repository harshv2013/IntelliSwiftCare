#utils/blob_utils.py
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta
import os

def generate_file_sas(container_name: str, blob_name: str, hours_valid: int = 1):
    """
    Generate a SAS URL for a specific blob file.
    """
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT")   # e.g. "intellidococrai"
    account_key = os.getenv("AZURE_STORAGE_KEY")        # storage account key

    if not account_name or not account_key:
        raise ValueError("Storage account credentials not found in .env")

    expiry_time = datetime.utcnow() + timedelta(hours=hours_valid)

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time
    )

    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
