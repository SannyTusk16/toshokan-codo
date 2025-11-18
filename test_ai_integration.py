"""
Test AI Integration - Gemini Component Generation
Tests the complete AI-powered workflow.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.intent_parser import parse_intent
from src.component_mapper import map_sections_to_components
from src.assembler import assemble_website


def test_ai_generation():
    """Test AI component generation with Gemini."""
    
    print("\n" + "="*70)
    print("🤖 AI INTEGRATION TEST - GEMINI COMPONENT GENERATION")
    print("="*70)
    
    # Check if API key is configured
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    use_ai = os.getenv("USE_AI_GENERATION", "false").lower() == "true"
    
    print("\n📋 Configuration Check:")
    print(f"  GEMINI_API_KEY: {'✅ Set' if api_key else '❌ Not Set'}")
    print(f"  USE_AI_GENERATION: {use_ai}")
    
    if not api_key:
        print("\n⚠️  WARNING: No Gemini API key found!")
        print("  To enable AI generation:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your Gemini API key")
        print("  3. Set USE_AI_GENERATION=true")
        print("\n  Continuing with pre-defined components fallback...\n")
    
    # Test prompt with specific content
    test_prompt = "Build a portfolio website for John Doe, a software engineer specializing in web development"
    
    print("\n📝 Test Prompt:")
    print(f'  "{test_prompt}"')
    
    # Stage 1: Parse Intent
    print("\n🧠 Stage 1: Parsing Intent...")
    intent = parse_intent(test_prompt)
    print(f"  ✅ Framework: {intent.get('framework')}")
    print(f"  ✅ Sections: {', '.join(intent.get('sections', []))}")
    
    # Stage 2: Component Mapping (with AI if configured)
    print("\n🗺️  Stage 2: Component Mapping...")
    
    # Test with AI enabled
    component_mapping, ai_metadata = map_sections_to_components(
        intent,
        user_prompt=test_prompt,
        use_ai=True
    )
    
    print(f"  ✅ Mapped {len(component_mapping)} components")
    
    # Display AI stats
    if ai_metadata:
        ai_gen = ai_metadata.get("ai_generated", 0)
        cached = ai_metadata.get("from_cache", 0)
        fallback = ai_metadata.get("fallback_used", 0)
        
        print(f"\n  📊 AI Generation Stats:")
        print(f"     🤖 AI Generated: {ai_gen}")
        print(f"     💾 From Cache: {cached}")
        print(f"     📦 Fallback: {fallback}")
        
        if ai_gen > 0 or cached > 0:
            print(f"\n  ✅ AI generation working!")
        else:
            print(f"\n  ℹ️  Using pre-defined components (AI disabled or failed)")
    
    # Show component sources
    print(f"\n  📂 Component Sources:")
    for section, path in component_mapping.items():
        if isinstance(path, str) and path.startswith("AI_GENERATED:"):
            print(f"     {section}: 🤖 AI Generated")
        else:
            print(f"     {section}: 📦 {Path(path).name}")
    
    # Stage 3: Assembly
    print("\n🔨 Stage 3: Assembly...")
    try:
        html_content = assemble_website(component_mapping, intent)
        size_kb = len(html_content) / 1024
        print(f"  ✅ Generated {size_kb:.2f} KB of HTML")
        
        # Check for content extraction
        if "John Doe" in html_content and "software engineer" in html_content.lower():
            print(f"  ✅ Content extraction working! Found 'John Doe' and 'software engineer'")
        elif ai_gen > 0 or cached > 0:
            print(f"  ⚠️  Content may not be extracted properly")
        
    except Exception as e:
        print(f"  ❌ Assembly failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test cache persistence
    print("\n💾 Stage 4: Testing Cache Persistence...")
    component_mapping_2, ai_metadata_2 = map_sections_to_components(
        intent,
        user_prompt=test_prompt,
        use_ai=True
    )
    
    cached_2 = ai_metadata_2.get("from_cache", 0)
    print(f"  Cached components on 2nd run: {cached_2}")
    
    if cached_2 > 0:
        print(f"  ✅ Caching system working!")
    
    # Test without AI
    print("\n📦 Stage 5: Testing Fallback Mode (--no-ai)...")
    component_mapping_3, ai_metadata_3 = map_sections_to_components(
        intent,
        user_prompt=test_prompt,
        use_ai=False
    )
    
    fallback_3 = ai_metadata_3.get("fallback_used", 0)
    print(f"  ✅ Fallback components: {fallback_3}")
    
    for section, path in list(component_mapping_3.items())[:3]:
        print(f"     {section}: {Path(path).name}")
    
    print("\n" + "="*70)
    print("✅ AI INTEGRATION TEST COMPLETE")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_ai_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
