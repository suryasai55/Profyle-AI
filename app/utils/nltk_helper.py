import os
import nltk
import logging

logger = logging.getLogger(__name__)

def init_nltk_resources(nltk_data_dir):
    """
    Ensures required NLTK resources are downloaded and available.
    Stores downloaded packages in the configured nltk_data directory to avoid system-wide installs.
    """
    # Create the directory if it doesn't exist
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Prepend our custom directory to NLTK's data path
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)
        
    resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords': 'stopwords'
    }
    
    for resource_path, download_name in resources.items():
        try:
            # Check if resource is already downloaded
            nltk.data.find(resource_path)
            logger.info(f"NLTK resource '{resource_path}' is available.")
        except LookupError:
            logger.info(f"NLTK resource '{resource_path}' not found. Downloading '{download_name}'...")
            try:
                nltk.download(download_name, download_dir=nltk_data_dir, quiet=True)
                logger.info(f"Successfully downloaded NLTK resource '{download_name}' to {nltk_data_dir}")
            except Exception as e:
                logger.error(f"Failed to download NLTK resource '{download_name}': {str(e)}")
                # Dynamic fallback check in standard path if custom download fails
                pass
