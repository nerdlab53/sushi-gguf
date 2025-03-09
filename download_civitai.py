import os
import logging
import subprocess
from pathlib import Path

class CivitaiDownloader:
    def __init__(self, output_dir="./downloads"):
        """Initialize the downloader with an output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def download_model(self, model_name, model_version_id, civitai_token):
        """
        Download a model from CivitAI using the provided version ID and API token.
        
        Args:
            model_name: Name to save the model as
            model_version_id: CivitAI model version ID
            civitai_token: CivitAI API token
            
        Returns:
            Path to the downloaded model file
        """
        if not model_name.endswith(".safetensors"):
            model_name += ".safetensors"
            
        output_file_path = self.output_dir / model_name
        
        # Construct the download URL with version ID and token
        file_url = f"https://civitai.com/api/download/models/{model_version_id}?token={civitai_token}"
        
        logging.info(f"Downloading model from CivitAI: {model_name}")
        logging.info(f"Output path: {output_file_path}")
        
        # Download the file using wget
        try:
            cmd = ["wget", "-c", file_url, "-O", str(output_file_path)]
            subprocess.run(cmd, check=True)
            logging.info(f"Model downloaded successfully to: {output_file_path}")
            return str(output_file_path)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to download model: {e}")
            return None 