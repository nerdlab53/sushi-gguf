from rich.console import Console
from rich.panel import Panel

def display_banner():
    """Display the SUSHI-GGUF ASCII art banner."""
    console = Console()
    
    # ASCII art representation of the SUSHI-GGUF logo
    banner = r"""
  ███████╗██╗   ██╗███████╗██╗  ██╗██╗      ██████╗  ██████╗ ██╗   ██╗███████╗
  ██╔════╝██║   ██║██╔════╝██║  ██║██║     ██╔════╝ ██╔════╝ ██║   ██║██╔════╝
  ███████╗██║   ██║███████╗███████║██║     ██║  ███╗██║  ███╗██║   ██║█████╗  
  ╚════██║██║   ██║╚════██║██╔══██║██║     ██║   ██║██║   ██║██║   ██║██╔══╝  
  ███████║╚██████╔╝███████║██║  ██║██║     ╚██████╔╝╚██████╔╝╚██████╔╝██║     
  ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝     
    """
    
    # Display the banner with mint green color that matches the image
    console.print(Panel.fit(banner, border_style="green", style="bold spring_green1"))
    console.print("\n") 