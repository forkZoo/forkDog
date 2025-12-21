"""
ForkDog CLI

Command-line interface for managing your dog.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.genetics import GeneticsEngine, DogDNA
from src.storage import DogStorage
from src.visualizer import DogVisualizer
from src.evolution import EvolutionAgent

console = Console()


@click.group()
def cli():
    """🐵 ForkDog - Your AI-powered digital pet on GitHub"""
    pass


@cli.command()
@click.option('--from-fork', is_flag=True, help='Initialize from parent repo (for forks)')
@click.option('--force', '-f', is_flag=True, help='Force overwrite without confirmation (for CI)')
def init(from_fork, force):
    """Initialize a new dog"""
    console.print("\n🐵 [bold cyan]Initializing ForkDog...[/bold cyan]\n")
    
    storage = DogStorage()
    
    # Check if dog already exists
    existing_dna = storage.load_dna()
    if existing_dna:
        console.print("[yellow]⚠️  Dog already exists![/yellow]")
        console.print(f"   DNA Hash: {existing_dna.dna_hash}")
        console.print(f"   Generation: {existing_dna.generation}")
        
        # In fork mode or with --force, auto-confirm to allow CI to proceed
        if not force and not from_fork:
            if not click.confirm("\nOverwrite existing dog?"):
                console.print("[red]Cancelled.[/red]")
                return
        else:
            console.print("[cyan]   Auto-confirming for fork/CI mode...[/cyan]")
    
    # Initialize DNA
    if from_fork:
        console.print("[cyan]🍴 Checking for parent repository...[/cyan]")
        dna = storage.initialize_from_parent()
        
        if not dna:
            console.print("[yellow]⚠️  Not a fork or parent DNA not found[/yellow]")
            console.print("[cyan]   Generating new dog instead...[/cyan]")
            dna = GeneticsEngine.generate_random_dna()
    else:
        console.print("[cyan]🎲 Generating random dog...[/cyan]")
        dna = GeneticsEngine.generate_random_dna()
    
    # Save DNA
    storage.save_dna_locally(dna)
    storage.save_stats(dna, age_days=0)
    storage.save_history_entry(dna, "🎉 Your dog was born!")
    
    # Generate initial visualization
    svg = DogVisualizer.generate_svg(dna)
    svg_file = Path("dog_data/dog.svg")
    svg_file.write_text(svg)
    
    # Archive with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_file = Path(f"dog_evolution/{timestamp}_dog.svg")
    archive_file.parent.mkdir(exist_ok=True)
    archive_file.write_text(svg)
    
    # Display info
    console.print("\n[bold green]✅ Dog initialized![/bold green]\n")
    
    table = Table(title="Your Dog")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("DNA Hash", dna.dna_hash)
    table.add_row("Generation", str(dna.generation))
    table.add_row("Rarity Score", f"{dna.get_rarity_score():.1f}/100")
    
    console.print(table)
    
    console.print("\n[bold]Traits:[/bold]")
    for cat, trait in dna.traits.items():
        console.print(f"  • {cat.value}: [green]{trait.value}[/green] ([yellow]{trait.rarity.value}[/yellow])")
    
    console.print(f"\n[dim]SVG saved to: {svg_file}[/dim]")


@cli.command()
@click.option('--ai', is_flag=True, help='Use AI-powered evolution')
@click.option('--strength', default=0.1, help='Evolution strength (0-1)')
def evolve(ai, strength):
    """Evolve your dog"""
    console.print("\n🧬 [bold cyan]Evolving dog...[/bold cyan]\n")
    
    storage = DogStorage()
    
    # Load current DNA
    dna = storage.load_dna()
    if not dna:
        console.print("[red]❌ No dog found! Run 'init' first.[/red]")
        return
    
    console.print(f"Current DNA: {dna.dna_hash}")
    console.print(f"Mutations so far: {dna.mutation_count}")
    
    # Evolve
    # Evolve
    if ai:
        provider = os.getenv("AI_PROVIDER", "github")
        console.print(f"\n[cyan]🤖 Using AI-powered evolution ({provider})...[/cyan]")
        
        try:
            agent = EvolutionAgent(provider_type=provider)
            evolved_dna = agent.evolve_with_ai(dna, days_passed=1)
            story = agent.generate_evolution_story(dna, evolved_dna)
        except Exception as e:
            console.print(f"[yellow]⚠️  AI evolution failed: {e}[/yellow]")
            console.print("[cyan]🎲 Falling back to random evolution...[/cyan]")
            evolved_dna = GeneticsEngine.evolve(dna, evolution_strength=strength)
            story = "Your dog evolved randomly!"
    else:
        console.print(f"\n[cyan]🎲 Using random evolution (strength: {strength})...[/cyan]")
        evolved_dna = GeneticsEngine.evolve(dna, evolution_strength=strength)
        story = "Your dog evolved randomly!"
    
    # Show changes
    console.print("\n[bold]Changes:[/bold]")
    changes = []
    for cat in dna.traits.keys():
        old_trait = dna.traits[cat]
        new_trait = evolved_dna.traits[cat]
        
        if old_trait.value != new_trait.value:
            console.print(f"  • {cat.value}: [red]{old_trait.value}[/red] → [green]{new_trait.value}[/green]")
            changes.append(cat.value)
        else:
            console.print(f"  • {cat.value}: {old_trait.value} (unchanged)")
    
    if not changes:
        console.print("  [dim]No changes today[/dim]")
    
    # Save
    storage.save_dna_locally(evolved_dna)
    storage.save_stats(evolved_dna, age_days=0)  # TODO: calculate actual age
    storage.save_history_entry(evolved_dna, story)
    
    # Generate new visualization
    svg = DogVisualizer.generate_svg(evolved_dna)
    svg_file = Path("dog_data/dog.svg")
    svg_file.write_text(svg)
    
    # Archive with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_file = Path(f"dog_evolution/{timestamp}_dog.svg")
    archive_file.parent.mkdir(exist_ok=True)
    archive_file.write_text(svg)
    
    console.print(f"\n[bold green]✅ Evolution complete![/bold green]")
    console.print(f"New DNA: {evolved_dna.dna_hash}")
    console.print(f"Total mutations: {evolved_dna.mutation_count}")
    console.print(f"\n[italic]{story}[/italic]")


@cli.command()
def show():
    """Show current dog stats"""
    console.print("\n🐵 [bold cyan]Your Dog[/bold cyan]\n")
    
    storage = DogStorage()
    dna = storage.load_dna()
    
    if not dna:
        console.print("[red]❌ No dog found! Run 'init' first.[/red]")
        return
    
    # Stats table
    table = Table(title="Dog Stats")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("DNA Hash", dna.dna_hash)
    table.add_row("Generation", str(dna.generation))
    table.add_row("Parent", dna.parent_id or "None (Genesis)")
    table.add_row("Mutations", str(dna.mutation_count))
    table.add_row("Rarity Score", f"{dna.get_rarity_score():.1f}/100")
    
    console.print(table)
    
    # Traits table
    traits_table = Table(title="Traits")
    traits_table.add_column("Category", style="cyan")
    traits_table.add_column("Value", style="green")
    traits_table.add_column("Rarity", style="yellow")
    
    for cat, trait in dna.traits.items():
        traits_table.add_row(cat.value, trait.value, trait.rarity.value)
    
    console.print("\n")
    console.print(traits_table)


@cli.command()
@click.option('--limit', default=10, help='Number of entries to show')
def history(limit):
    """Show evolution history"""
    console.print("\n📜 [bold cyan]Evolution History[/bold cyan]\n")
    
    storage = DogStorage()
    entries = storage.get_history()
    
    if not entries:
        console.print("[yellow]No history yet.[/yellow]")
        return
    
    # Show recent entries
    for entry in entries[-limit:]:
        timestamp = entry.get("timestamp", "Unknown")
        story = entry.get("story", "")
        mutations = entry.get("mutation_count", 0)
        rarity = entry.get("rarity_score", 0)
        
        panel = Panel(
            f"[dim]{timestamp}[/dim]\n\n{story}\n\n"
            f"Mutations: {mutations} | Rarity: {rarity:.1f}/100",
            title=f"Generation {entry.get('generation', '?')}",
            border_style="cyan"
        )
        console.print(panel)
        console.print()


@cli.command()
def visualize():
    """Generate and save dog visualization"""
    console.print("\n🎨 [bold cyan]Generating visualization...[/bold cyan]\n")
    
    storage = DogStorage()
    dna = storage.load_dna()
    
    if not dna:
        console.print("[red]❌ No dog found! Run 'init' first.[/red]")
        return
    
    # Generate SVG
    svg = DogVisualizer.generate_svg(dna)
    svg_file = Path("dog_data/dog.svg")
    svg_file.write_text(svg)
    
    # Archive with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_file = Path(f"dog_evolution/{timestamp}_dog.svg")
    archive_file.parent.mkdir(exist_ok=True)
    archive_file.write_text(svg)
    
    console.print(f"[green]✅ SVG saved to: {svg_file}[/green]")
    console.print(f"[dim]   Archived to: {archive_file}[/dim]")
    
    # Try to open in browser
    try:
        import webbrowser
        webbrowser.open(str(svg_file.absolute()))
        console.print("[dim]Opening in browser...[/dim]")
    except:
        pass


@cli.command()
def update_readme():
    """Update README with current dog"""
    console.print("\n📝 [bold cyan]Updating README...[/bold cyan]\n")
    
    storage = DogStorage()
    dna = storage.load_dna()
    
    if not dna:
        console.print("[red]❌ No dog found! Run 'init' first.[/red]")
        return
    
    # Read current README
    readme_file = Path("README.md")
    if not readme_file.exists():
        console.print("[red]❌ README.md not found![/red]")
        return
    
    readme = readme_file.read_text()
    
    # Generate SVG and save it
    svg = DogVisualizer.generate_svg(dna, width=400, height=400)
    svg_file = Path("dog_data/dog.svg")
    svg_file.write_text(svg)
    
    # Archive with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_file = Path(f"dog_evolution/{timestamp}_dog.svg")
    archive_file.parent.mkdir(exist_ok=True)
    archive_file.write_text(svg)
    
    # Update dog display section with image reference
    dog_section = '''<!-- DOG_DISPLAY_START -->
<div align="center">

![Your Dog](dog_data/dog.svg)

</div>
<!-- DOG_DISPLAY_END -->'''
    
    # Replace section
    import re
    pattern = r'<!-- DOG_DISPLAY_START -->.*?<!-- DOG_DISPLAY_END -->'
    readme = re.sub(pattern, dog_section, readme, flags=re.DOTALL)
    
    # Update stats section
    history = storage.get_history()
    age_days = len(history)
    
    stats_section = f'''<!-- DOG_STATS_START -->
- **Generation**: {dna.generation}
- **Age**: {age_days} days
- **Mutations**: {dna.mutation_count}
- **Rarity Score**: {dna.get_rarity_score():.1f}/100
<!-- DOG_STATS_END -->'''
    
    pattern = r'<!-- DOG_STATS_START -->.*?<!-- DOG_STATS_END -->'
    readme = re.sub(pattern, stats_section, readme, flags=re.DOTALL)
    
    # Save
    readme_file.write_text(readme)
    
    console.print("[green]✅ README updated![/green]")


if __name__ == "__main__":
    cli()
