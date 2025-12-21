"""
ForkDog Visualizer - Dog Edition
"""

import math
from typing import Dict, List
from src.genetics import DogDNA, TraitCategory, Rarity

class DogVisualizer:
    """Generates generic SVG dog art from DNA"""

    BODY_COLORS = {
        "brown": {"main": "#8B4513", "shadow": "#5D2E0C", "highlight": "#A0522D"},
        "tan": {"main": "#D2B48C", "shadow": "#B8956E", "highlight": "#E8D4B8"},
        "beige": {"main": "#F5F5DC", "shadow": "#D4D4B8", "highlight": "#FFFFF0"},
        "gray": {"main": "#808080", "shadow": "#5A5A5A", "highlight": "#A0A0A0"},
        "golden": {"main": "#FFD700", "shadow": "#B8860B", "highlight": "#FFEC8B"},
        "white": {"main": "#FFFFFF", "shadow": "#E0E0E0", "highlight": "#FFFFFF"},
        "black": {"main": "#333333", "shadow": "#000000", "highlight": "#555555"},
        "spotted": {"main": "#FFFFFF", "shadow": "#E0E0E0", "highlight": "#FFFFFF"},
    }

    BACKGROUNDS = {
        "white": {"type": "solid", "color": "#F8F9FA"},
        "blue_sky": {"type": "gradient", "id": "sky-gradient"},
        "green_grass": {"type": "gradient", "id": "grass-gradient"},
    }

    @classmethod
    def generate_svg(cls, dna: DogDNA, width: int = 400, height: int = 400) -> str:
        traits = {
            "body_color": dna.traits[TraitCategory.BODY_COLOR].value,
            "expression": dna.traits[TraitCategory.FACE_EXPRESSION].value,
            "accessory": dna.traits[TraitCategory.ACCESSORY].value,
            "pattern": dna.traits[TraitCategory.PATTERN].value,
            "background": dna.traits[TraitCategory.BACKGROUND].value,
            "special": dna.traits[TraitCategory.SPECIAL].value,
        }
        seed = int(dna.dna_hash[:8], 16) if dna.dna_hash else 12345

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            cls._generate_defs(),
            cls._generate_background(traits["background"], width, height, seed),
            cls._generate_body(traits["body_color"], traits["pattern"], width, height, seed),
            cls._generate_face(traits["expression"], width, height),
            "</svg>",
        ]
        return "\n".join(svg_parts)

    @classmethod
    def _generate_defs(cls) -> str:
        return '''<defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="2" dy="4" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
    <linearGradient id="sky-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#87CEEB"/><stop offset="100%" stop-color="#E0F4FF"/>
    </linearGradient>
</defs>'''

    @classmethod
    def _generate_background(cls, bg: str, w: int, h: int, seed: int) -> str:
        return f'<rect width="{w}" height="{h}" fill="#F0F8FF"/>'

    @classmethod
    def _generate_body(cls, color: str, pattern: str, w: int, h: int, seed: int) -> str:
        cx, cy = w // 2, h // 2
        c = cls.BODY_COLORS.get(color, cls.BODY_COLORS["brown"])
        parts = []

        # Floppy Ears
        parts.append(f'<ellipse cx="{cx-70}" cy="{cy-40}" rx="30" ry="60" fill="{c["main"]}" transform="rotate(20 {cx-70} {cy-40})" filter="url(#shadow)"/>')
        parts.append(f'<ellipse cx="{cx+70}" cy="{cy-40}" rx="30" ry="60" fill="{c["main"]}" transform="rotate(-20 {cx+70} {cy-40})" filter="url(#shadow)"/>')
        
        # Head
        parts.append(f'<rect x="{cx-80}" y="{cy-80}" width="160" height="150" rx="40" fill="{c["main"]}" filter="url(#shadow)"/>')
        
        # Snout area
        parts.append(f'<ellipse cx="{cx}" cy="{cy+20}" rx="50" ry="35" fill="{c["highlight"]}" opacity="0.6"/>')

        return "\n".join(parts)

    @classmethod
    def _generate_face(cls, expr: str, w: int, h: int) -> str:
        cx, cy = w // 2, h // 2
        parts = []
        
        # Eyes (Round for dog)
        parts.append(f'<circle cx="{cx-35}" cy="{cy-20}" r="15" fill="#FFF"/>')
        parts.append(f'<circle cx="{cx+35}" cy="{cy-20}" r="15" fill="#FFF"/>')
        parts.append(f'<circle cx="{cx-35}" cy="{cy-20}" r="8" fill="#000"/>')
        parts.append(f'<circle cx="{cx+35}" cy="{cy-20}" r="8" fill="#000"/>')
        
        # Big nose
        parts.append(f'<ellipse cx="{cx}" cy="{cy+10}" rx="20" ry="15" fill="#000"/>')
        parts.append(f'<ellipse cx="{cx-5}" cy="{cy+5}" rx="5" ry="3" fill="#FFF" opacity="0.5"/>')
        
        # Tongue out?
        if expr in ["happy", "excited"]:
             parts.append(f'<path d="M{cx-10} {cy+30} Q{cx} {cy+60} {cx+10} {cy+30}" fill="#FF69B4" stroke="#D14785" stroke-width="2"/>')
        else:
            parts.append(f'<path d="M{cx-15} {cy+30} Q{cx} {cy+45} {cx+15} {cy+30}" stroke="#000" stroke-width="3" fill="none"/>')
            
        return "\n".join(parts)

    @classmethod
    def generate_thumbnail(cls, dna: DogDNA, size: int = 100) -> str:
        return cls.generate_svg(dna, width=size, height=size)

def main():
    pass

if __name__ == "__main__":
    main()
