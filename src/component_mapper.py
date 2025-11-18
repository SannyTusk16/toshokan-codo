"""
Component Mapper Module
Maps abstract section names to concrete component file paths OR generates them with AI.

Responsibilities:
- Maintain a registry of available components for each framework
- Map section names to appropriate component files
- Handle component variants (e.g., navbar1, navbar2, hero3)
- Support multiple UI frameworks
- AI-powered component generation using Gemini (when enabled)
- Fallback to pre-defined components when AI unavailable

Example Registry:
{
    "tailwind": {
        "navbar": ["components/tailwind/nav1.html", "components/tailwind/nav2.html"],
        "hero": ["components/tailwind/hero1.html", "components/tailwind/hero2.html"]
    }
}
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import AI generator
try:
    from src.gemini_generator import (
        is_ai_available, 
        generate_full_website_with_ai,
        generate_component_with_ai
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Import online component fetcher
try:
    from src.online_component_fetcher import get_online_component, list_available_online_components
    ONLINE_FETCHER_AVAILABLE = True
except ImportError:
    ONLINE_FETCHER_AVAILABLE = False

# Configuration
USE_AI = os.getenv("USE_AI_GENERATION", "true").lower() == "true"
AI_FALLBACK = os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true"

# Default component registry path
REGISTRY_PATH = "components/component_registry.json"


def load_component_registry(registry_path: str = REGISTRY_PATH) -> dict:
    """
    Load the component registry from JSON file.
    
    Args:
        registry_path: Path to the component registry JSON file
        
    Returns:
        Dictionary mapping frameworks and sections to component paths
    """
    # Get absolute path relative to project root
    project_root = Path(__file__).parent.parent
    full_path = project_root / registry_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"Component registry not found at {full_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    return registry


def map_sections_to_components(
    intent: dict,
    user_prompt: str = "",
    use_ai: bool = None,
    selection_strategy: str = "first",
    registry_path: str = REGISTRY_PATH,
    verbose: bool = True
) -> Tuple[dict, dict]:
    """
    Map each section in the intent to a specific component file OR generate with AI.
    
    Args:
        intent: Parsed intent dictionary from intent_parser
        user_prompt: Original user prompt (required for AI generation)
        use_ai: Override USE_AI setting (None = use env setting)
        selection_strategy: How to select from multiple variants (for fallback)
        registry_path: Path to component registry file
        verbose: Whether to print progress messages
        
    Returns:
        Tuple of (component_map, metadata)
        - component_map: Dictionary mapping sections to component file paths or HTML
        - metadata: Dictionary with generation metadata (ai_used, cached_count, etc.)
    """
    metadata = {
        "ai_used": False,
        "ai_generated_count": 0,
        "cached_count": 0,
        "fallback_count": 0,
        "total_sections": 0
    }
    
    # Determine if we should use AI
    should_use_ai = (use_ai if use_ai is not None else USE_AI) and AI_AVAILABLE
    
    if should_use_ai and is_ai_available():
        # Try AI generation first
        if verbose:
            print("  🤖 Using Gemini AI for component generation...")
        
        try:
            ai_components = generate_full_website_with_ai(user_prompt, intent, verbose=verbose)
            component_map = {}
            
            for section, html in ai_components.items():
                if html:
                    # Store generated HTML directly (will be handled by assembler)
                    component_map[section] = f"AI_GENERATED:{section}"
                    metadata["ai_generated_count"] += 1
                elif AI_FALLBACK:
                    # Fallback to registry
                    if verbose:
                        print(f"  ⚠️  Falling back to pre-defined component for {section}")
                    fallback = _get_component_from_registry(
                        section, intent, selection_strategy, registry_path
                    )
                    if fallback:
                        component_map[section] = fallback
                        metadata["fallback_count"] += 1
            
            metadata["ai_used"] = True
            metadata["total_sections"] = len(component_map)
            
            # Cache AI components for assembler to access
            _cache_ai_components_for_assembler(ai_components)
            
            return component_map, metadata
            
        except Exception as e:
            if verbose:
                print(f"  ⚠️  AI generation failed: {str(e)}")
            
            if not AI_FALLBACK:
                raise
            
            if verbose:
                print("  📁 Falling back to pre-defined components...")
    
    # Use traditional registry mapping
    component_map = _map_from_registry(intent, selection_strategy, registry_path, verbose)
    metadata["total_sections"] = len(component_map)
    metadata["fallback_count"] = len(component_map)
    
    return component_map, metadata


def _get_component_from_registry(
    section: str,
    intent: dict,
    selection_strategy: str,
    registry_path: str
) -> Optional[str]:
    """Get a single component from the registry."""
    registry = load_component_registry(registry_path)
    framework = intent.get("framework", "bootstrap")
    
    if framework not in registry:
        return None
    
    framework_components = registry[framework]
    available_components = framework_components.get(section, [])
    
    if not available_components:
        return None
    
    # Select component based on strategy
    if selection_strategy == "random":
        return random.choice(available_components)
    elif selection_strategy == "round_robin":
        # Simple round-robin (could be improved with state)
        index = hash(section) % len(available_components)
        return available_components[index]
    else:  # "first" or default
        return available_components[0]


def _map_from_registry(
    intent: dict,
    selection_strategy: str,
    registry_path: str,
    verbose: bool
) -> dict:
    """Map sections to components using the traditional registry approach."""
    framework = intent.get("framework", "tailwind")
    sections = intent.get("sections", [])
    component_map = {}
    
    # Use online components for Bootstrap if available
    if framework.lower() == "bootstrap" and ONLINE_FETCHER_AVAILABLE:
        if verbose:
            print("  🌐 Using online Bootstrap components...")
        
        available_online = list_available_online_components("bootstrap")
        
        for section in sections:
            if section in available_online:
                # Mark as online component (will be fetched by assembler)
                component_map[section] = f"ONLINE:bootstrap:{section}"
            elif verbose:
                print(f"  ⚠️  Warning: No online component for section '{section}', skipping...")
        
        return component_map
    
    # Traditional file-based approach for other frameworks
    registry = load_component_registry(registry_path)
    
    # Check if framework exists in registry
    if framework not in registry:
        raise ValueError(f"Framework '{framework}' not found in registry. Available: {list(registry.keys())}")
    
    framework_components = registry[framework]
    
    for section in sections:
        # Get available components for this section
        available_components = framework_components.get(section, [])
        
        if not available_components:
            # Try to find a fallback or skip
            print(f"⚠️  Warning: No {framework} component found for section '{section}', skipping...")
            continue
        
        # Select component based on strategy
        selected_component = _select_component(
            available_components, 
            selection_strategy,
            section
        )
        
        component_map[section] = selected_component
    
    return component_map


def _select_component(
    components: List[str], 
    strategy: str,
    section_name: str = ""
) -> str:
    """
    Select a component from available options based on strategy.
    
    Args:
        components: List of available component paths
        strategy: Selection strategy (first, random, round_robin)
        section_name: Name of the section (for round_robin state)
        
    Returns:
        Selected component path
    """
    if not components:
        raise ValueError("No components available to select from")
    
    if strategy == "first":
        return components[0]
    
    elif strategy == "random":
        return random.choice(components)
    
    elif strategy == "round_robin":
        # Simple round robin using hash of section name
        # In production, you'd track state across calls
        index = hash(section_name) % len(components)
        return components[index]
    
    else:
        # Default to first
        return components[0]


def get_available_components(
    framework: str,
    section: Optional[str] = None,
    registry_path: str = REGISTRY_PATH
) -> Dict[str, List[str]]:
    """
    Get available components for a framework and optionally a specific section.
    
    Args:
        framework: UI framework name (tailwind, bootstrap, etc.)
        section: Optional section name to filter by
        registry_path: Path to component registry file
        
    Returns:
        Dictionary of section -> component paths
    """
    registry = load_component_registry(registry_path)
    
    if framework not in registry:
        return {}
    
    framework_components = registry[framework]
    
    if section:
        return {section: framework_components.get(section, [])}
    
    return framework_components


def validate_component_paths(registry_path: str = REGISTRY_PATH) -> Dict[str, List[str]]:
    """
    Validate that all component files in the registry actually exist.
    
    Args:
        registry_path: Path to component registry file
        
    Returns:
        Dictionary of framework -> list of missing component paths
    """
    registry = load_component_registry(registry_path)
    project_root = Path(__file__).parent.parent
    
    missing_components = {}
    
    for framework, sections in registry.items():
        missing_in_framework = []
        
        for section, components in sections.items():
            for component_path in components:
                full_path = project_root / component_path
                if not full_path.exists():
                    missing_in_framework.append(component_path)
        
        if missing_in_framework:
            missing_components[framework] = missing_in_framework
    
    return missing_components


def add_component_to_registry(
    framework: str,
    section: str,
    component_path: str,
    registry_path: str = REGISTRY_PATH
) -> bool:
    """
    Add a new component to the registry.
    
    Args:
        framework: UI framework name
        section: Section name
        component_path: Path to component file
        registry_path: Path to component registry file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        registry = load_component_registry(registry_path)
        
        # Initialize framework if it doesn't exist
        if framework not in registry:
            registry[framework] = {}
        
        # Initialize section if it doesn't exist
        if section not in registry[framework]:
            registry[framework][section] = []
        
        # Add component if not already present
        if component_path not in registry[framework][section]:
            registry[framework][section].append(component_path)
        
        # Save updated registry
        project_root = Path(__file__).parent.parent
        full_path = project_root / registry_path
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error adding component: {e}")
        return False


def get_component_stats(registry_path: str = REGISTRY_PATH) -> Dict:
    """
    Get statistics about the component registry.
    
    Args:
        registry_path: Path to component registry file
        
    Returns:
        Dictionary with component statistics
    """
    registry = load_component_registry(registry_path)
    
    stats = {
        "frameworks": len(registry),
        "framework_details": {}
    }
    
    for framework, sections in registry.items():
        total_components = sum(len(components) for components in sections.values())
        stats["framework_details"][framework] = {
            "sections": len(sections),
            "total_components": total_components,
            "sections_list": list(sections.keys())
        }
    
    return stats


# Test function for development
def test_component_mapper():
    """
    Test the component mapper with sample intents.
    """
    from intent_parser import parse_intent
    
    test_prompts = [
        "Build a modern portfolio site with navbar, hero, and footer",
        "Create a landing page with features using Bootstrap",
        "Simple site with hero and contact sections"
    ]
    
    print("🗺️  Testing Component Mapper\n" + "="*60 + "\n")
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"Test {i}: {prompt}")
        intent = parse_intent(prompt)
        
        try:
            component_map = map_sections_to_components(intent)
            print(f"  Intent sections: {intent['sections']}")
            print(f"  Framework: {intent['framework']}")
            print(f"  Mapped components:")
            for section, path in component_map.items():
                print(f"    {section}: {path}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print("-" * 60 + "\n")
    
    # Print component stats
    print("\n📊 Component Registry Statistics:")
    stats = get_component_stats()
    print(f"  Total frameworks: {stats['frameworks']}")
    for framework, details in stats['framework_details'].items():
        print(f"\n  {framework.upper()}:")
        print(f"    Sections: {details['sections']}")
        print(f"    Total components: {details['total_components']}")
        print(f"    Available sections: {', '.join(details['sections_list'])}")
    
    # Validate component paths
    print("\n🔍 Validating Component Paths...")
    missing = validate_component_paths()
    if missing:
        print("  ⚠️  Missing components found:")
        for framework, paths in missing.items():
            print(f"    {framework}: {len(paths)} missing")
            for path in paths:
                print(f"      - {path}")
    else:
        print("  ✅ All component paths are valid!")


# AI component cache (temporary storage)
_AI_COMPONENT_CACHE = {}


def _cache_ai_components_for_assembler(components: dict):
    """Cache AI-generated components for assembler to access."""
    global _AI_COMPONENT_CACHE
    _AI_COMPONENT_CACHE = components


def get_ai_component(section: str) -> Optional[str]:
    """
    Retrieve AI-generated component HTML.
    
    Args:
        section: Section type
        
    Returns:
        HTML string or None
    """
    return _AI_COMPONENT_CACHE.get(section)


def clear_ai_cache():
    """Clear the AI component cache."""
    global _AI_COMPONENT_CACHE
    _AI_COMPONENT_CACHE = {}


if __name__ == "__main__":
    test_component_mapper()
