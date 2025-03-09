"""
This module is responsible for setting up llama.cpp for GGUF conversion.
"""

import subprocess
import os
import logging


class SetupLLamaCpp:
    def setup_llama_cpp(self):
        """Set up llama.cpp for GGUF conversion"""
        logging.info("Setting up llama.cpp...")
        
        # Clone llama.cpp repository if it doesn't exist
        if os.path.exists("llama.cpp"):
            # Remove the current version of llama.cpp in this directory
            subprocess.run(["rm", "-rf", "llama.cpp"])
            logging.info("Removed existing llama.cpp directory")

        if not os.path.exists("llama.cpp"):
            # Clone the latest version of llama.cpp
            subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"], check=True)
            logging.info("Cloned llama.cpp repository")
        
        # Navigate to llama.cpp directory and build
        original_dir = os.getcwd()
        os.chdir("llama.cpp")

        # Install gguf-py if needed
        try:
            import gguf
            logging.info("gguf already installed")
        except ImportError:
            logging.info("Installing gguf-py...")
            subprocess.run(["pip", "install", "./gguf-py"], check=True)
        
        # Change directory to llama.cpp
        try:
            subprocess.run(["cd", "llama.cpp"], check=True)
        except Exception as e:
            logging.warning("Can't change directory to llama.cpp")
        
        # Download conversion script and patch
        logging.info("Downloading conversion script and patch...")
        subprocess.run(["wget", "-O", "convert.py", 
                      "https://raw.githubusercontent.com/city96/ComfyUI-GGUF/main/tools/convert.py"], check=True)
        subprocess.run(["wget", "-O", "convert_g.py", 
                      "https://huggingface.co/Old-Fisherman/SDXL_Finetune_GGUF_Files/resolve/main/convert_g.py"], check=True)
        subprocess.run(["wget", "-O", "lcpp.patch", 
                      "https://raw.githubusercontent.com/city96/ComfyUI-GGUF/main/tools/lcpp.patch"], check=True)
        
        # Apply the patch (make non-fatal)
        logging.info("Applying patch to llama.cpp...")
        try:
            subprocess.run(["git", "checkout", "tags/b3600"], check=True)
            # Try to apply the patch, but don't error if it fails
            subprocess.run(["git", "apply", "lcpp.patch"],  check=True)
        except Exception as e:
            logging.warning(f"Error during patching: {e}")
            logging.warning("Continuing without patch. This may affect compatibility.")
        
        # Build the project
        logging.info("Building llama.cpp...")
            
        # Try CMake build 
        try:
            logging.info("Trying CMake build .. ")
            os.makedirs("build", exist_ok=True)
            os.chdir("build")
            subprocess.run(["cmake", ".."], check=True)
            subprocess.run(["cmake", "--build", ".", "--config", "Debug", "-j10", "--target", "llama-quantize"], check=True)
            os.chdir("..")
        except subprocess.CalledProcessError as e2:
            logging.error(f"CMake build also failed: {e2}")
            raise RuntimeError("Failed to build llama.cpp using both make and CMake")
        
        # Return to original directory
        os.chdir(original_dir)
        logging.info("llama.cpp setup complete")