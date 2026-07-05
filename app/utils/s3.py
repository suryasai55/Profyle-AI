import os
import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logger = logging.getLogger(__name__)

def upload_file_to_s3(file_obj, filename, config):
    """
    Uploads a file to an AWS S3 bucket.
    If USE_S3 is False, or upload fails due to credentials/network,
    it falls back to local storage and returns the local relative path.
    
    Returns:
        s3_key: The S3 object key if uploaded, or None if saved locally.
        saved_filename: The final filename saved on the storage medium.
    """
    use_s3 = config.get('USE_S3', False)
    bucket_name = config.get('S3_BUCKET_NAME')
    
    # 1. Local Storage Fallback Check
    if not use_s3:
        logger.info(f"USE_S3 is disabled. Saving file '{filename}' locally.")
        local_path = os.path.join(config['UPLOAD_FOLDER'], filename)
        file_obj.save(local_path)
        return None, filename

    # 2. Attempt S3 Upload
    logger.info(f"USE_S3 is enabled. Attempting S3 upload for '{filename}' to bucket '{bucket_name}'.")
    try:
        # Boto3 client will automatically use IAM Instance Profiles if key/secret are None
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config.get('AWS_SECRET_ACCESS_KEY'),
            region_name=config.get('AWS_REGION', 'us-east-1')
        )
        
        # Upload file object directly to S3
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            filename,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        logger.info(f"Successfully uploaded '{filename}' to S3 bucket '{bucket_name}'.")
        return filename, filename

    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.warning(f"AWS Credentials missing or partial: {str(e)}. Falling back to local storage.")
    except Exception as e:
        logger.error(f"Failed to upload to S3 due to unexpected error: {str(e)}. Falling back to local storage.")
        
    # 3. Fallback to Local Storage on Error
    try:
        # Reset file pointer to start before saving locally
        file_obj.seek(0)
        local_path = os.path.join(config['UPLOAD_FOLDER'], filename)
        file_obj.save(local_path)
        logger.info(f"Locally saved fallback copy of '{filename}' to uploads/.")
        return None, filename
    except Exception as save_err:
        logger.critical(f"Local storage fallback failed critical error: {str(save_err)}")
        raise save_err
