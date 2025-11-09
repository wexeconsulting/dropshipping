"""
CLI interface for the dropshipping application.
Provides clean, table-formatted output for all commands.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parser_manager import main_df_parser, run_batch_task
from utils.etl import run_etl_task
from utils.db import get_margins, get_config_settings, update_margin, get_product_ids
from utils.logger import get_technical_logger, get_user_logger

console = Console()
tech_logger = get_technical_logger(__name__)
user_logger = get_user_logger(__name__)


@click.group()
@click.version_option(version='1.5.4')
def cli():
    """Dropshipping Management CLI - Clean, table-based interface"""
    pass


@cli.command()
@click.argument('config_id', type=int)
def batch(config_id):
    """Run batch task for a configuration."""
    tech_logger.info(f"Starting batch task for config_id: {config_id}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Processing batch for config {config_id}...", total=None)
            run_batch_task(config_id)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓[/green] Batch task completed for config {config_id}")
        tech_logger.info(f"Batch task completed successfully for config_id: {config_id}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Batch task failed: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option('--url', required=True, help='URL to fetch product IDs from')
def import_products(url):
    """Import product IDs from external source."""
    tech_logger.info(f"Starting product import from URL: {url}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Importing product IDs...", total=None)
            run_etl_task("ETL_import_product_ids", {"url": url})
            progress.update(task, completed=True)
        
        console.print("[green]✓[/green] Product IDs imported successfully")
        tech_logger.info("Product import completed successfully")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Product import failed: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('config_id', type=int)
@click.option('--limit', default=10, help='Number of products to display')
def list_products(config_id, limit):
    """List products for a configuration."""
    tech_logger.info(f"Listing products for config_id: {config_id}, limit: {limit}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading product data...", total=None)
            df = main_df_parser(config_id)
            progress.update(task, completed=True)
        
        if df.empty:
            console.print("[yellow]No products found[/yellow]")
            return
        
        # Create table
        table = Table(
            title=f"Products (showing {min(limit, len(df))} of {len(df)})",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        # Add columns
        table.add_column("Name", style="white", no_wrap=False, max_width=40)
        table.add_column("EAN", style="yellow")
        table.add_column("Category", style="blue", max_width=25)
        table.add_column("Qty", justify="right", style="magenta")
        table.add_column("Price", justify="right", style="green")
        table.add_column("Margin", justify="right", style="cyan")
        table.add_column("Gross", justify="right", style="bold green")
        
        # Add rows
        for _, row in df.head(limit).iterrows():
            table.add_row(
                str(row['name'])[:40],
                str(row['ean']),
                str(row.get('category_name', 'N/A'))[:25],
                str(row['quantity']),
                f"{row['price']:.2f}",
                f"{row['margin']:.2%}",
                f"{row['gross_price']:.2f}"
            )
        
        console.print(table)
        console.print(f"\n[dim]Total products: {len(df)}[/dim]")
        tech_logger.info(f"Listed {min(limit, len(df))} products out of {len(df)} total")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Failed to list products: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('config_id', type=int)
def list_margins(config_id):
    """List custom margins for a configuration."""
    tech_logger.info(f"Listing margins for config_id: {config_id}")
    
    try:
        margins_dict = get_margins(config_id)
        
        if not margins_dict:
            console.print("[yellow]No custom margins configured[/yellow]")
            return
        
        # Create table
        table = Table(
            title=f"Custom Margins (Total: {len(margins_dict)})",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("EAN", style="yellow")
        table.add_column("Margin", justify="right", style="green")
        
        # Add rows
        for ean, margin in margins_dict.items():
            table.add_row(str(ean), f"{margin:.2%}")
        
        console.print(table)
        tech_logger.info(f"Listed {len(margins_dict)} custom margins")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Failed to list margins: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('config_id', type=int)
@click.argument('ean', type=str)
@click.argument('margin', type=float)
def set_margin(config_id, ean, margin):
    """Set margin for a specific product."""
    tech_logger.info(f"Setting margin for config_id: {config_id}, ean: {ean}, margin: {margin}")
    
    try:
        update_margin(config_id, ean, margin)
        console.print(f"[green]✓[/green] Margin set: EAN {ean} → {margin:.2%}")
        tech_logger.info(f"Margin updated successfully")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Failed to set margin: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument('config_id', type=int)
def config_info(config_id):
    """Show configuration details."""
    tech_logger.info(f"Fetching config info for config_id: {config_id}")
    
    try:
        name, settings, url = get_config_settings(config_id)
        
        # Create table
        table = Table(
            title=f"Configuration: {name}",
            box=box.ROUNDED,
            show_header=False,
            show_edge=True
        )
        
        table.add_column("Property", style="bold cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Config ID", str(config_id))
        table.add_row("Name", name)
        table.add_row("URL", url)
        table.add_row("Default Margin", f"{settings.get('defaultMargin', 0.2):.2%}")
        
        console.print(table)
        tech_logger.info(f"Config info displayed for config_id: {config_id}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Failed to get config info: {str(e)}", exc_info=True)
        sys.exit(1)


@cli.command()
def list_mappings():
    """List EAN to Product ID mappings."""
    tech_logger.info("Listing product mappings")
    
    try:
        mappings = get_product_ids()
        
        if not mappings:
            console.print("[yellow]No product mappings found[/yellow]")
            return
        
        # Create table
        table = Table(
            title=f"Product Mappings (Total: {len(mappings)})",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("EAN", style="yellow")
        table.add_column("Product ID", style="green")
        
        # Add rows (limit to first 50 for readability)
        limit = 50
        for i, (ean, product_id) in enumerate(mappings.items()):
            if i >= limit:
                break
            table.add_row(str(ean), str(product_id))
        
        console.print(table)
        
        if len(mappings) > limit:
            console.print(f"\n[dim]Showing {limit} of {len(mappings)} mappings[/dim]")
        
        tech_logger.info(f"Listed product mappings: {len(mappings)} total")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)}")
        tech_logger.error(f"Failed to list mappings: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
