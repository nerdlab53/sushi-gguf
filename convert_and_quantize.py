import logging
from pathlib import Path
import os
import subprocess

# Import setup_llama_cpp
from setup_llama_cpp import SetupLLamaCpp

class ConvertAndQuantize:
    def __init__(self, model_path):
        self.model_path = model_path
        self.gguf_dir = Path(model_path).parent / "gguf"
        self.gguf_dir.mkdir(exist_ok=True)
        self.llama_cpp = SetupLLamaCpp()

    def convert_to_gguf(self, unet_path, setup_llama_cpp=True):
        """Convert UNet to GGUF format"""
        if setup_llama_cpp:
            self.llama_cpp.setup_llama_cpp()
        
        unet_path = Path(unet_path)
        if not unet_path.exists():
            logging.error(f"UNet file not found: {unet_path}")
            return None
            
        filename_prefix = unet_path.stem.replace("_unet", "")
        logging.info(f"Converting UNet to GGUF: {unet_path}")
        
        # Make output directory if it doesn't exist
        self.gguf_dir.mkdir(exist_ok=True)
        
        # Output path for the GGUF file
        output_path = self.gguf_dir / f"{filename_prefix}-F16.gguf"
        
        # Navigate to llama.cpp directory
        original_dir = os.getcwd()
        try:
            # Get absolute paths
            unet_abs_path = os.path.abspath(str(unet_path))
            output_abs_path = os.path.abspath(str(output_path))
            
            # Approach 1: Use a shell command directly with explicit architecture
            cmd_str = f'python llama.cpp/convert.py --src "{unet_abs_path}" --dst "{output_abs_path}"'
            logging.info(f"Running command: {cmd_str}")
            
            try:
                # Try using os.system first
                exit_code = os.system(cmd_str)
                if exit_code != 0:
                    raise RuntimeError(f"Command exited with code {exit_code}")
            except Exception as e1:
                logging.warning(f"First conversion attempt failed: {e1}")
        except Exception as e:
            logging.error(f"Conversion attempts have failed: {e}")
            return None
        finally:
            os.chdir(original_dir)
        
        # Check if output file was created
        if not output_path.exists():
            logging.error("Conversion failed: Output file not created")
            return None
            
        logging.info(f"GGUF conversion complete. Output saved to: {output_path}")
        return str(output_path)
    
    def quantize_gguf(self, gguf_path, quant_type):
        """Quantize a GGUF model to the specified quantization type"""
        gguf_path = Path(gguf_path)
        gguf_abs_path = os.path.abspath(str(gguf_path))
        
        if not os.path.exists(gguf_abs_path):
            logging.error(f"Source GGUF file not found: {gguf_abs_path}")
            return None
            
        base_name = gguf_path.stem.replace("-F16", "")
        self.quantized_dir.mkdir(exist_ok=True)
        dst = self.quantized_dir / f"{base_name}_{quant_type}.gguf"
        dst_abs_path = os.path.abspath(str(dst))
        
        # Navigate to llama.cpp directory
        original_dir = os.getcwd()
        try:
            os.chdir("llama.cpp")
            
            # Find the quantize binary
            quantize_bin = "./build/bin/llama-quantize"
            if not os.path.exists(quantize_bin):
                quantize_bin = "./build/llama-quantize"  # Alternative path
                
            if not os.path.exists(quantize_bin):
                raise FileNotFoundError(f"llama-quantize binary not found at {quantize_bin}")
            
            # Run quantization with absolute paths
            cmd = [quantize_bin, gguf_abs_path, dst_abs_path, quant_type]
            
            logging.info(f"Running quantization: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if result.stdout:
                logging.info(f"Quantization output: {result.stdout}")
            if result.stderr:
                logging.warning(f"Quantization stderr: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            logging.error(f"Quantization failed: {e}")
            logging.error(f"Command error: {e.stderr if hasattr(e, 'stderr') else 'No error info'}")
            return None
        finally:
            os.chdir(original_dir)
        
        if not dst.exists():
            logging.error("Quantization failed: Output file not created")
            return None
            
        logging.info(f"Quantization complete. Output saved to: {dst}")
        return str(dst)
