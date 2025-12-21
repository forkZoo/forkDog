"""
ForkDog Genetics System

Handles DNA generation, inheritance, mutations, and trait management.
Inspired by CryptoKitties breeding mechanics.
"""

import random
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field


class Rarity(str, Enum):
    """Trait rarity levels"""
    COMMON = "common"          # 60%
    UNCOMMON = "uncommon"      # 25%
    RARE = "rare"              # 10%
    LEGENDARY = "legendary"    # 5%


class TraitCategory(str, Enum):
    """Categories of dog traits"""
    BODY_COLOR = "body_color"
    FACE_EXPRESSION = "face_expression"
    ACCESSORY = "accessory"
    PATTERN = "pattern"
    BACKGROUND = "background"
    SPECIAL = "special"


class Trait(BaseModel):
    """A single genetic trait"""
    category: TraitCategory
    value: str
    rarity: Rarity
    gene_sequence: str = Field(default="")  # Hex representation
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.gene_sequence:
            # Generate gene sequence from value
            self.gene_sequence = hashlib.md5(
                f"{self.category}:{self.value}".encode()
            ).hexdigest()[:8]


class DogDNA(BaseModel):
    """Complete DNA sequence for a dog"""
    generation: int = 1
    parent_id: Optional[str] = None
    traits: Dict[TraitCategory, Trait] = Field(default_factory=dict)
    mutation_count: int = 0
    birth_timestamp: int = 0
    dna_hash: str = ""
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.dna_hash:
            self.dna_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate unique hash for this DNA"""
        trait_string = "".join([
            f"{cat.value}:{trait.gene_sequence}"
            for cat, trait in sorted(self.traits.items())
        ])
        return hashlib.sha256(trait_string.encode()).hexdigest()[:16]
    
    def get_rarity_score(self) -> float:
        """Calculate overall rarity score (0-100)"""
        rarity_values = {
            Rarity.COMMON: 1,
            Rarity.UNCOMMON: 2,
            Rarity.RARE: 5,
            Rarity.LEGENDARY: 10
        }
        total = sum(rarity_values[trait.rarity] for trait in self.traits.values())
        max_possible = len(self.traits) * rarity_values[Rarity.LEGENDARY]
        return (total / max_possible) * 100 if max_possible > 0 else 0


class GeneticsEngine:
    """Handles all genetic operations"""
    
    # Trait definitions with rarity
    TRAIT_POOL = {
        TraitCategory.BODY_COLOR: {
            Rarity.COMMON: ["brown", "tan", "beige", "gray"],
            Rarity.UNCOMMON: ["golden", "silver", "copper", "bronze"],
            Rarity.RARE: ["blue", "purple", "green", "pink"],
            Rarity.LEGENDARY: ["rainbow", "galaxy", "holographic", "crystal"]
        },
        TraitCategory.FACE_EXPRESSION: {
            Rarity.COMMON: ["happy", "neutral", "curious", "sleepy"],
            Rarity.UNCOMMON: ["excited", "mischievous", "wise", "cool"],
            Rarity.RARE: ["surprised", "laughing", "winking", "zen"],
            Rarity.LEGENDARY: ["enlightened", "cosmic", "legendary", "divine"]
        },
        TraitCategory.ACCESSORY: {
            Rarity.COMMON: ["none", "simple_hat", "bandana", "bow"],
            Rarity.UNCOMMON: ["sunglasses", "crown", "headphones", "monocle"],
            Rarity.RARE: ["laser_eyes", "halo", "horns", "wizard_hat"],
            Rarity.LEGENDARY: ["golden_crown", "diamond_chain", "jetpack", "wings"]
        },
        TraitCategory.PATTERN: {
            Rarity.COMMON: ["solid", "spots", "stripes", "gradient"],
            Rarity.UNCOMMON: ["swirls", "stars", "hearts", "diamonds"],
            Rarity.RARE: ["fractals", "nebula", "lightning", "flames"],
            Rarity.LEGENDARY: ["aurora", "quantum", "cosmic_dust", "void"]
        },
        TraitCategory.BACKGROUND: {
            Rarity.COMMON: ["white", "blue_sky", "green_grass", "sunset"],
            Rarity.UNCOMMON: ["forest", "beach", "mountains", "city"],
            Rarity.RARE: ["space", "underwater", "volcano", "aurora"],
            Rarity.LEGENDARY: ["multiverse", "black_hole", "dimension_rift", "heaven"]
        },
        TraitCategory.SPECIAL: {
            Rarity.COMMON: ["none"],
            Rarity.UNCOMMON: ["sparkles", "glow", "shadow"],
            Rarity.RARE: ["aura", "particles", "energy"],
            Rarity.LEGENDARY: ["transcendent", "godlike", "mythical"]
        }
    }
    
    @classmethod
    def generate_random_dna(cls, generation: int = 1, parent_id: Optional[str] = None) -> DogDNA:
        """Generate completely random DNA"""
        traits = {}
        
        for category in TraitCategory:
            rarity = cls._roll_rarity()
            available_traits = cls.TRAIT_POOL[category][rarity]
            value = random.choice(available_traits)
            
            traits[category] = Trait(
                category=category,
                value=value,
                rarity=rarity
            )
        
        return DogDNA(
            generation=generation,
            parent_id=parent_id,
            traits=traits,
            birth_timestamp=int(random.random() * 1000000)  # Mock timestamp
        )
    
    @classmethod
    def _roll_rarity(cls) -> Rarity:
        """Roll for trait rarity based on probabilities"""
        roll = random.random() * 100
        
        if roll < 60:
            return Rarity.COMMON
        elif roll < 85:
            return Rarity.UNCOMMON
        elif roll < 95:
            return Rarity.RARE
        else:
            return Rarity.LEGENDARY
    
    @classmethod
    def breed(cls, parent_dna: DogDNA, mutation_rate: float = 0.3) -> DogDNA:
        """
        Create child DNA from parent with inheritance and mutations
        
        Args:
            parent_dna: Parent's DNA
            mutation_rate: Probability of mutation per trait (0-1)
        """
        child_traits = {}
        
        for category in TraitCategory:
            if random.random() < 0.5:
                # Inherit from parent
                child_traits[category] = parent_dna.traits[category].model_copy()
            else:
                # Generate new trait
                rarity = cls._roll_rarity()
                available_traits = cls.TRAIT_POOL[category][rarity]
                value = random.choice(available_traits)
                
                child_traits[category] = Trait(
                    category=category,
                    value=value,
                    rarity=rarity
                )
            
            # Apply mutation
            if random.random() < mutation_rate:
                child_traits[category] = cls._mutate_trait(child_traits[category])
        
        return DogDNA(
            generation=parent_dna.generation + 1,
            parent_id=parent_dna.dna_hash,
            traits=child_traits,
            birth_timestamp=int(random.random() * 1000000)
        )
    
    @classmethod
    def _mutate_trait(cls, trait: Trait) -> Trait:
        """Mutate a single trait"""
        # 70% chance to stay in same rarity, 30% chance to shift
        if random.random() < 0.7:
            new_rarity = trait.rarity
        else:
            # Shift rarity up or down
            rarities = list(Rarity)
            current_idx = rarities.index(trait.rarity)
            shift = random.choice([-1, 1])
            new_idx = max(0, min(len(rarities) - 1, current_idx + shift))
            new_rarity = rarities[new_idx]
        
        # Pick new value from rarity pool
        available_traits = cls.TRAIT_POOL[trait.category][new_rarity]
        new_value = random.choice(available_traits)
        
        return Trait(
            category=trait.category,
            value=new_value,
            rarity=new_rarity
        )
    
    @classmethod
    def evolve(cls, dna: DogDNA, evolution_strength: float = 0.1) -> DogDNA:
        """
        Evolve DNA over time (daily mutations)
        
        Args:
            dna: Current DNA
            evolution_strength: Probability of change per trait (0-1)
        """
        evolved_traits = {}
        mutations = 0
        
        for category, trait in dna.traits.items():
            if random.random() < evolution_strength:
                # Evolve this trait
                evolved_traits[category] = cls._mutate_trait(trait)
                mutations += 1
            else:
                # Keep unchanged
                evolved_traits[category] = trait.model_copy()
        
        return DogDNA(
            generation=dna.generation,
            parent_id=dna.parent_id,
            traits=evolved_traits,
            mutation_count=dna.mutation_count + mutations,
            birth_timestamp=dna.birth_timestamp
        )
    
    @classmethod
    def dna_to_dict(cls, dna: DogDNA) -> dict:
        """Convert DNA to dictionary for storage"""
        return {
            "generation": dna.generation,
            "parent_id": dna.parent_id,
            "dna_hash": dna.dna_hash,
            "mutation_count": dna.mutation_count,
            "birth_timestamp": dna.birth_timestamp,
            "traits": {
                cat.value: {
                    "value": trait.value,
                    "rarity": trait.rarity.value,
                    "gene_sequence": trait.gene_sequence
                }
                for cat, trait in dna.traits.items()
            },
            "rarity_score": dna.get_rarity_score()
        }
    
    @classmethod
    def dict_to_dna(cls, data: dict) -> DogDNA:
        """Convert dictionary to DNA object"""
        traits = {}
        for cat_str, trait_data in data["traits"].items():
            category = TraitCategory(cat_str)
            traits[category] = Trait(
                category=category,
                value=trait_data["value"],
                rarity=Rarity(trait_data["rarity"]),
                gene_sequence=trait_data["gene_sequence"]
            )
        
        return DogDNA(
            generation=data["generation"],
            parent_id=data.get("parent_id"),
            traits=traits,
            mutation_count=data.get("mutation_count", 0),
            birth_timestamp=data.get("birth_timestamp", 0),
            dna_hash=data.get("dna_hash", "")
        )


def main():
    """Test genetics system"""
    print("🧬 ForkDog Genetics System Test\n")
    
    # Generate random dog
    print("1. Generating random dog...")
    dog1 = GeneticsEngine.generate_random_dna()
    print(f"   DNA Hash: {dog1.dna_hash}")
    print(f"   Rarity Score: {dog1.get_rarity_score():.1f}/100")
    print(f"   Traits:")
    for category, trait in dog1.traits.items():
        print(f"     - {category.value}: {trait.value} ({trait.rarity.value})")
    
    # Breed child
    print("\n2. Breeding child dog...")
    child = GeneticsEngine.breed(dog1)
    print(f"   Generation: {child.generation}")
    print(f"   Parent: {child.parent_id}")
    print(f"   DNA Hash: {child.dna_hash}")
    print(f"   Rarity Score: {child.get_rarity_score():.1f}/100")
    
    # Evolve
    print("\n3. Evolving dog over time...")
    evolved = GeneticsEngine.evolve(dog1, evolution_strength=0.3)
    print(f"   Mutations: {evolved.mutation_count}")
    print(f"   New DNA Hash: {evolved.dna_hash}")
    
    # Serialization
    print("\n4. Testing serialization...")
    data = GeneticsEngine.dna_to_dict(dog1)
    restored = GeneticsEngine.dict_to_dna(data)
    print(f"   Original hash: {dog1.dna_hash}")
    print(f"   Restored hash: {restored.dna_hash}")
    print(f"   Match: {dog1.dna_hash == restored.dna_hash}")
    
    print("\n✅ Genetics system working!")


if __name__ == "__main__":
    main()
