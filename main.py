# Imports
import os
import logging
import argparse
from pathlib import Path
from extract_components import ExtractComponents
from convert_and_quantize import ConvertAndQuantize
from setup_llama_cpp import SetupLLamaCpp
from download_civitai import CivitaiDownloader

# UI Imports
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box
from rich.markdown import Markdown
from rich.filesize import decimal as filesize_decimal

# Setup console
console = Console()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_header():
    """Display attractive header for the application"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]SDXL Model GGUF Quantization Tool[/bold blue]\n"
        "[cyan]Convert and quantize your Stable Diffusion XL models to GGUF format[/cyan]",
        border_style="green",
        box=box.DOUBLE,
        padding=(1, 6)
    ))
    console.print("\n")

def show_steps():
    """Display the steps of the process"""
    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
    table.add_column("#", style="dim", width=3)
    table.add_column("Step", style="cyan")
    table.add_column("Description", style="green")
    
    table.add_row("1", "Extract Components", "Extract UNet, CLIP_L, CLIP_G and VAE from model")
    table.add_row("2", "Convert to GGUF", "Convert UNet to GGUF format")
    table.add_row("3", "Quantize", "Create quantized versions with reduced precision")
    
    console.print(Panel(table, title="[bold yellow]Process Steps[/bold yellow]", border_style="yellow"))
    console.print("\n")

def get_model_info(model_path):
    """Display model information in a panel"""
    if not os.path.exists(model_path):
        return
    
    file_size = os.path.getsize(model_path) / (1024 * 1024 * 1024)  # Size in GB
    file_name = os.path.basename(model_path)
    
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("File Name", file_name)
    table.add_row("File Size", f"{file_size:.2f} GB")
    table.add_row("Location", str(model_path))
    
    console.print(Panel(table, title="[bold yellow]Model Information[/bold yellow]", border_style="yellow"))

def display_quantization_results(original_path, quantized_paths):
    """Display a summary of the quantization results with size comparisons"""
    if not os.path.exists(original_path):
        original_size = 0
    else:
        original_size = os.path.getsize(original_path) / (1024 * 1024)  # Size in MB
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Model Type", style="cyan")
    table.add_column("File Size", style="green")
    table.add_column("% of Original", style="yellow")
    
    table.add_row("Original Model", f"{original_size:.2f} MB", "100%")
    
    for path in quantized_paths:
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024 * 1024)
            percentage = (size / original_size) * 100 if original_size > 0 else 0
            quant_type = os.path.basename(path).split('_')[-1].replace('.gguf', '')
            table.add_row(f"{quant_type}", f"{size:.2f} MB", f"{percentage:.1f}%")
    
    console.print(Panel(table, title="[bold yellow]Quantization Results[/bold yellow]", border_style="yellow"))
    console.print("\n")

def run_with_progress(task_description, function, *args, **kwargs):
    """Run a function with a progress spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}"),
        BarColumn(),
        TextColumn("[bold yellow]{task.fields[status]}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        # Create a task
        task = progress.add_task(f"[cyan]{task_description}[/cyan]", total=None, status="Processing...")
        
        # Run the function
        try:
            result = function(*args, **kwargs)
            progress.update(task, status="Complete!")
            return result
        except Exception as e:
            progress.update(task, status=f"Failed: {str(e)}")
            raise

def main():
    """
    Main entry point for the modular SDXL model processing pipeline.
    Handles extraction of model components, conversion to GGUF, and quantization.
    """
    parser = argparse.ArgumentParser(description="Modular SDXL Model Processing Pipeline")
    
    # Model input options
    model_input_group = parser.add_argument_group("Model Input Options")
    model_input_group.add_argument("--model_path", type=str, help="Path to the SDXL model file")
    model_input_group.add_argument("--output_dir", type=str, default="./output", help="Directory to save all outputs")
    
    # Civitai options
    civitai_group = parser.add_argument_group("Civitai Download Options")
    civitai_group.add_argument("--civitai", action="store_true", help="Download model from CivitAI")
    civitai_group.add_argument("--model_name", type=str, help="Name for the downloaded model file")
    civitai_group.add_argument("--model_version_id", type=str, help="CivitAI model version ID")
    civitai_group.add_argument("--civitai_token", type=str, help="CivitAI API token")
    civitai_group.add_argument("--download_dir", type=str, default="./downloads", help="Directory to save downloaded models")
    
    # Processing options
    processing_group = parser.add_argument_group("Processing Options")
    processing_group.add_argument("--skip_extract", action="store_true", help="Skip extraction and use existing UNet file")
    processing_group.add_argument("--unet_path", type=str, help="Path to existing UNet file (if skipping extraction)")
    processing_group.add_argument("--skip_setup", action="store_true", help="Skip llama.cpp setup (use if already set up)")
    processing_group.add_argument("--skip_convert", action="store_true", help="Skip conversion and use existing GGUF file")
    processing_group.add_argument("--gguf_path", type=str, help="Path to existing GGUF file (if skipping conversion)")
    
    # Quantization options
    quant_group = parser.add_argument_group("Quantization Options")
    quant_group.add_argument("--skip_quant", action="store_true", help="Skip quantization and only generate F16 GGUF")
    quant_group.add_argument("--quant_types", type=str, nargs="+", default=["Q5_K_S"],
                      choices=["Q4_K_S", "Q5_K_S", "Q8_0", "all"],
                      help="Quantization types to generate (use 'all' for all types)")
    
    args = parser.parse_args()
    
    # Display rich UI header
    show_header()
    
    # Try to display banner if available
    try:
        from ascii_art import display_banner
        display_banner()
    except ImportError:
        console.print("[yellow]ASCII art module not found. Continuing without banner...[/yellow]")
    
    # Display process steps
    show_steps()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Handle quantization types
    if "all" in args.quant_types:
        quant_types = ["Q4_K_S", "Q5_K_S", "Q8_0"]
    else:
        quant_types = args.quant_types
    
    # Download from CivitAI if requested
    model_path = args.model_path
    if args.civitai:
        if not all([args.model_name, args.model_version_id, args.civitai_token]):
            parser.error("When using --civitai, you must provide --model_name, --model_version_id, and --civitai_token")
        
        console.print(Panel(f"[bold cyan]Downloading model from CivitAI: {args.model_name} (Version: {args.model_version_id})[/bold cyan]", border_style="cyan"))
        
        downloader = CivitaiDownloader(args.download_dir)
        model_path = run_with_progress(
            f"Downloading {args.model_name}",
            downloader.download_model,
            args.model_name, args.model_version_id, args.civitai_token
        )
        
        if not model_path:
            console.print("[bold red]Failed to download model from CivitAI. Aborting.[/bold red]")
            return
        
        console.print(f"[green]✓ Successfully downloaded model to: [bold]{model_path}[/bold][/green]")
    
    # Validate inputs
    if not args.skip_extract and not model_path:
        parser.error("Either --model_path or --civitai options are required when not skipping extraction")
    
    if args.skip_extract and not args.unet_path and not args.skip_convert:
        parser.error("--unet_path is required when skipping extraction and not skipping conversion")
    
    if args.skip_convert and not args.gguf_path and not args.skip_quant:
        parser.error("--gguf_path is required when skipping conversion and not skipping quantization")
    
    # Display model info if available
    if model_path:
        get_model_info(model_path)
    
    # Step 1: Extract components
    unet_path = args.unet_path
    if not args.skip_extract:
        console.print(Panel("[bold cyan]STEP 1: Extracting Model Components[/bold cyan]", border_style="cyan"))
        
        extractor = ExtractComponents(model_path)
        components = run_with_progress(
            "Extracting model components",
            extractor.extract_components, 
            model_path
        )
        
        unet_path = components['unet']
        console.print(f"[green]✓ Components extracted. UNet saved to: [bold]{unet_path}[/bold][/green]")
    else:
        console.print(f"[yellow]Skipping extraction, using existing UNet: {unet_path}[/yellow]")
    
    # Step 2: Convert to GGUF
    gguf_path = args.gguf_path
    if not args.skip_convert and unet_path:
        console.print(Panel("[bold cyan]STEP 2: Converting UNet to GGUF Format[/bold cyan]", border_style="cyan"))
        
        converter = ConvertAndQuantize(Path(unet_path).parent)
        gguf_path = run_with_progress(
            "Converting to GGUF format",
            converter.convert_to_gguf,
            unet_path, not args.skip_setup
        )
        
        if gguf_path:
            console.print(f"[green]✓ Conversion complete. GGUF saved to: [bold]{gguf_path}[/bold][/green]")
        else:
            console.print("[bold red]Conversion failed![/bold red]")
            return
    elif gguf_path:
        console.print(f"[yellow]Skipping conversion, using existing GGUF: {gguf_path}[/yellow]")
    else:
        console.print("[bold red]No UNet path available for conversion. Skipping GGUF conversion.[/bold red]")
        return
    
    # Step 3: Quantize GGUF
    if not args.skip_quant and gguf_path:
        console.print(Panel("[bold cyan]STEP 3: Quantizing GGUF Model[/bold cyan]", border_style="cyan"))
        
        converter = ConvertAndQuantize(Path(gguf_path).parent)
        quantized_paths = []
        
        for quant_type in quant_types:
            quantized_path = run_with_progress(
                f"Quantizing to {quant_type}",
                converter.quantize_gguf,
                gguf_path, quant_type
            )
            
            if quantized_path:
                quantized_paths.append(quantized_path)
                console.print(f"[green]✓ Quantization to {quant_type} complete: [bold]{quantized_path}[/bold][/green]")
            else:
                console.print(f"[bold red]Quantization to {quant_type} failed![/bold red]")
        
        if quantized_paths:
            display_quantization_results(gguf_path, quantized_paths)
    elif args.skip_quant:
        console.print("[yellow]Skipping quantization as requested.[/yellow]")
    
    console.print(Panel("[bold green]Processing pipeline complete![/bold green]", border_style="green"))

if __name__ == "__main__":
    main()