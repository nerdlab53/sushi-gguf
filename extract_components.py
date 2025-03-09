import logging
from pathlib import Path
from safetensors.torch import load_file, save_file

class ExtractComponents:
    def __init__(self, model_path):
        self.model_path = model_path
        self.components_dir = Path(model_path).parent / "components"
        self.components_dir.mkdir(exist_ok=True)

    def extract_components(self, model_path):
        """Extract UNet, CLIP_L, CLIP_G, and VAE from a SDXL model"""
        logging.info(f"Loading checkpoint from: {model_path}")
        state_dict = load_file(model_path)
        
        filename_prefix = Path(model_path).stem
        
        # Extract UNet
        clip_l_keys = [key for key in state_dict.keys() if key.startswith("conditioner.embedders.0.")]
        clip_g_keys = [key for key in state_dict.keys() if key.startswith("conditioner.embedders.1.")]
        vae_keys = [key for key in state_dict.keys() if key.startswith("first_stage_model.")]
        excluded_keys = set(clip_l_keys + clip_g_keys + vae_keys)
        unet_keys = [key for key in state_dict.keys() if key not in excluded_keys]
        
        unet_state_dict = {key: state_dict[key] for key in unet_keys}
        unet_path = self.components_dir / f"{filename_prefix}_unet.safetensors"
        logging.info(f"Saving UNet weights to: {unet_path}")
        save_file(unet_state_dict, str(unet_path))
        
        # Extract CLIP_L
        clip_l_state_dict = {key: state_dict[key] for key in clip_l_keys}
        clip_l_path = self.components_dir / f"{filename_prefix}_clip_l.safetensors"
        logging.info(f"Saving CLIP_L weights to: {clip_l_path}")
        save_file(clip_l_state_dict, str(clip_l_path))
        
        # Extract CLIP_G
        clip_g_state_dict = {key: state_dict[key] for key in clip_g_keys}
        clip_g_path = self.components_dir / f"{filename_prefix}_clip_g.safetensors"
        logging.info(f"Saving CLIP_G weights to: {clip_g_path}")
        save_file(clip_g_state_dict, str(clip_g_path))
        
        # Extract VAE
        vae_state_dict = {
            key.replace("first_stage_model.", ""): state_dict[key]
            for key in vae_keys
        }
        vae_path = self.components_dir / f"{filename_prefix}_vae.safetensors"
        logging.info(f"Saving VAE weights to: {vae_path}")
        save_file(vae_state_dict, str(vae_path))
        
        # Return paths to all extracted components
        return {
            'unet': str(unet_path),
            'clip_l': str(clip_l_path),
            'clip_g': str(clip_g_path),
            'vae': str(vae_path)
        }