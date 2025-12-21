"""
ForkDog Evolution Engine

AI-powered evolution using LLMs to make intelligent mutations.
Supports multiple providers:
- GitHub Models (Default)
- Claude (Anthropic)
"""

import os
import json
import abc
from typing import Optional, Dict, Any, List
from src.genetics import DogDNA, GeneticsEngine, TraitCategory


class AIProvider(abc.ABC):
    """Abstract base class for AI providers"""
    
    @abc.abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text response from the model"""
        pass
    
    @abc.abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def name(self) -> str:
        return "Claude"


class GitHubProvider(AIProvider):
    """GitHub Models provider (via OpenAI-compatible endpoint)"""
    
    def __init__(self, token: str, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=token,
        )
        self.model = model
        
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def name(self) -> str:
        return f"GitHub Models ({self.model})"


class EvolutionAgent:
    """AI agent that evolves dogs intelligently"""
    
    def __init__(self, provider_type: str = "github", api_key: Optional[str] = None):
        self.provider = self._setup_provider(provider_type, api_key)
    
    def _setup_provider(self, provider_type: str, api_key: Optional[str]) -> AIProvider:
        """Initialize the requested AI provider"""
        
        if provider_type == "claude":
            key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            return ClaudeProvider(key)
            
        elif provider_type == "github":
            # Use GITHUB_TOKEN or passed key
            token = api_key or os.getenv("GITHUB_TOKEN")
            if not token:
                raise ValueError("GITHUB_TOKEN not found (required for GitHub Models)")
            
            # Allow model selection via env env
            model = os.getenv("GITHUB_MODEL", "gpt-4o")
            return GitHubProvider(token, model)
            
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    def evolve_with_ai(self, dna: DogDNA, days_passed: int = 1) -> DogDNA:
        """
        Use AI to intelligently evolve the dog
        """
        print(f"🧠 Evolving with {self.provider.name()}...")
        
        # Get current traits as readable format
        current_traits = {
            cat.value: {
                "value": trait.value,
                "rarity": trait.rarity.value
            }
            for cat, trait in dna.traits.items()
        }
        
        # Create prompt
        prompt = self._create_evolution_prompt(current_traits, days_passed, dna.generation)
        
        try:
            # Call AI
            response_text = self.provider.generate_response(prompt)
            
            # Parse response
            evolution_decision = self._parse_ai_response(response_text)
            
            # Apply AI-suggested changes
            evolved_dna = self._apply_evolution(dna, evolution_decision)
            
            return evolved_dna
            
        except Exception as e:
            print(f"⚠️  AI evolution failed: {e}")
            print("   Falling back to random evolution...")
            return GeneticsEngine.evolve(dna, evolution_strength=0.1)
    
    def _create_evolution_prompt(self, traits: dict, days: int, generation: int) -> str:
        """Create prompt for AI"""
        return f"""You are an AI evolution agent for ForkDog - a digital pet that lives on GitHub.

Your task is to evolve this dog's appearance in a subtle, aesthetically pleasing way.

Current Dog Traits:
{json.dumps(traits, indent=2)}

Context:
- Generation: {generation}
- Days since last evolution: {days}
- Evolution should be subtle (1-2 traits max)
- Maintain aesthetic coherence
- Rarer traits should change less frequently

Available trait options:
- body_color: brown, tan, beige, gray, golden, silver, copper, bronze, blue, purple, green, pink, rainbow, galaxy, holographic, crystal
- face_expression: happy, neutral, curious, sleepy, excited, mischievous, wise, cool, surprised, laughing, winking, zen, enlightened, cosmic, legendary, divine
- accessory: none, simple_hat, bandana, bow, sunglasses, crown, headphones, monocle, laser_eyes, halo, horns, wizard_hat, golden_crown, diamond_chain, jetpack, wings
- pattern: solid, spots, stripes, gradient, swirls, stars, hearts, diamonds, fractals, nebula, lightning, flames, aurora, quantum, cosmic_dust, void
- background: white, blue_sky, green_grass, sunset, forest, beach, mountains, city, space, underwater, volcano, aurora, multiverse, black_hole, dimension_rift, heaven
- special: none, sparkles, glow, shadow, aura, particles, energy, transcendent, godlike, mythical

Rarity levels (from common to legendary):
- common (60% chance): Basic traits
- uncommon (25% chance): Special traits
- rare (10% chance): Unique traits
- legendary (5% chance): Ultra-rare traits

Respond with a JSON object ONLY (no markdown formatting) indicating which traits to change:
{{
  "changes": [
    {{
      "category": "body_color",
      "new_value": "golden",
      "new_rarity": "uncommon",
      "reason": "Subtle shift to warmer tone"
    }}
  ],
  "evolution_story": "Your dog is maturing, developing a golden sheen..."
}}

Keep changes minimal (0-2 traits). Consider the dog's current aesthetic."""
    
    def _parse_ai_response(self, response_text: str) -> dict:
        """Parse AI response"""
        try:
            # Clean up markdown code blocks if present
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON
            start = clean_text.find('{')
            end = clean_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = clean_text[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON object found")
        except Exception as e:
            print(f"⚠️  Failed to parse AI response: {e}")
            print(f"Raw response: {response_text[:100]}...")
            return {"changes": [], "evolution_story": "No changes today."}
    
    def _apply_evolution(self, dna: DogDNA, decision: dict) -> DogDNA:
        """Apply AI-decided evolution"""
        from src.genetics import Trait, Rarity
        
        # Copy current traits
        new_traits = {cat: trait.model_copy() for cat, trait in dna.traits.items()}
        mutations = 0
        
        # Apply changes
        for change in decision.get("changes", []):
            try:
                category = TraitCategory(change["category"])
                new_value = change["new_value"]
                new_rarity = Rarity(change["new_rarity"])
                
                # Create new trait
                new_traits[category] = Trait(
                    category=category,
                    value=new_value,
                    rarity=new_rarity
                )
                mutations += 1
                
            except Exception as e:
                print(f"⚠️  Failed to apply change: {e}")
        
        # Create evolved DNA
        evolved = DogDNA(
            generation=dna.generation,
            parent_id=dna.parent_id,
            traits=new_traits,
            mutation_count=dna.mutation_count + mutations,
            birth_timestamp=dna.birth_timestamp
        )
        
        return evolved
    
    def generate_evolution_story(self, old_dna: DogDNA, new_dna: DogDNA) -> str:
        """Generate a story about the evolution"""
        
        changes = []
        for category in TraitCategory:
            old_trait = old_dna.traits[category]
            new_trait = new_dna.traits[category]
            
            if old_trait.value != new_trait.value:
                changes.append(f"{category.value}: {old_trait.value} → {new_trait.value}")
        
        if not changes:
            return "Your dog rested today. No visible changes."
        
        prompt = f"""Generate a short, whimsical story (2-3 sentences) about a dog's evolution.

Changes that occurred:
{chr(10).join(changes)}

Make it fun and engaging, like a Tamagotchi update message."""
        
        try:
            return self.provider.generate_response(prompt, max_tokens=256).strip()
        except:
            return f"Your dog evolved! Changes: {', '.join(changes)}"


def main():
    """Test evolution agent"""
    from src.genetics import GeneticsEngine
    
    print("🧬 ForkDog Evolution Agent Test\n")
    
    # Determine provider
    provider = os.getenv("AI_PROVIDER", "github")
    print(f"Using provider: {provider}")
    
    try:
        agent = EvolutionAgent(provider_type=provider)
    except Exception as e:
        print(f"⚠️  Failed to initialize agent: {e}")
        return
    
    print("1. Generating random dog...")
    dna = GeneticsEngine.generate_random_dna()
    
    print("\n2. Evolving with AI...")
    evolved = agent.evolve_with_ai(dna, days_passed=1)
    
    print("\n3. Generating evolution story...")
    story = agent.generate_evolution_story(dna, evolved)
    print(f"   {story}")
    
    print("\n✅ Evolution agent working!")


if __name__ == "__main__":
    main()
