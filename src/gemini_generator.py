"""
Gemini AI Component Generator Module

Uses Google's Gemini API to dynamically generate website components based on user prompts.
Supports multi-modal input for better context and content generation.

Features:
- AI-powered component generation based on prompts
- Multi-modal support (text + images for context)
- Bootstrap 5 component generation
- Content extraction from user prompts
- Caching of generated components
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "8192"))
CACHE_ENABLED = os.getenv("CACHE_AI_COMPONENTS", "true").lower() == "true"
CACHE_DIR = Path(os.getenv("CACHE_DIRECTORY", ".cache/ai_components"))

# Rate limiting configuration
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "2.0"))  # Seconds between requests
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "5.0"))  # Initial retry delay

# Initialize Gemini
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL = genai.GenerativeModel(GEMINI_MODEL)
else:
    MODEL = None


def generate_component_with_ai(
    section_type: str,
    user_prompt: str,
    framework: str = "bootstrap",
    style: str = "modern",
    additional_context: Optional[Dict] = None
) -> Tuple[str, Dict]:
    """
    Generate a website component using Gemini AI.
    
    Args:
        section_type: Type of section (navbar, hero, features, etc.)
        user_prompt: Original user prompt with content details
        framework: UI framework to use (bootstrap, tailwind, etc.)
        style: Design style (modern, minimal, corporate, etc.)
        additional_context: Additional context like colors, brand name, etc.
        
    Returns:
        Tuple of (HTML component code, metadata)
    """
    if not MODEL:
        raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in .env file")
    
    # Check cache first
    if CACHE_ENABLED:
        cached_component = _get_cached_component(section_type, user_prompt, framework, style)
        if cached_component:
            return cached_component, {"cached": True, "section_type": section_type}
    
    # Build comprehensive prompt for Gemini
    ai_prompt = _build_component_prompt(section_type, user_prompt, framework, style, additional_context)
    
    # Retry logic with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            # Generate component with Gemini
            response = MODEL.generate_content(
                ai_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=AI_TEMPERATURE,
                    max_output_tokens=AI_MAX_TOKENS,
                )
            )
            
            # Extract HTML from response
            html_component = _extract_html_from_response(response.text)
            
            # Cache the generated component
            if CACHE_ENABLED and html_component:
                _cache_component(section_type, user_prompt, framework, style, html_component)
            
            metadata = {
                "section_type": section_type,
                "framework": framework,
                "style": style,
                "ai_generated": True,
                "cached": False
            }
            
            # Add delay before next request to avoid rate limits
            time.sleep(RATE_LIMIT_DELAY)
            
            return html_component, metadata
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limit error (429)
            if "429" in error_msg or "Resource exhausted" in error_msg or "quota" in error_msg.lower():
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff: wait longer each retry
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
            
            # For non-rate-limit errors or final retry, raise
            raise Exception(f"AI component generation failed: {error_msg}")
    
    raise Exception(f"AI component generation failed after {MAX_RETRIES} retries")


def _build_component_prompt(
    section_type: str,
    user_prompt: str,
    framework: str,
    style: str,
    additional_context: Optional[Dict]
) -> str:
    """
    Build a comprehensive prompt for Gemini to generate the component.
    """
    
    # Extract content from user prompt
    content_hints = _extract_content_hints(user_prompt, section_type)
    
    # Build context
    context = additional_context or {}
    brand_name = context.get("brand_name", "My Website")
    colors = context.get("colors", ["blue", "white"])
    
    prompt = f"""You are an expert web developer specializing in {framework.upper()} framework.

TASK: Generate a professional, production-ready {section_type} section for a website with REAL CONTENT extracted from the user's prompt.

USER REQUIREMENTS:
- Original prompt: "{user_prompt}"
- Section type: {section_type}
- Framework: {framework.upper()} 5.3
- Design style: {style}
- Brand name: {brand_name}
- Color scheme: {', '.join(colors)}

CONTENT EXTRACTION RULES:
{content_hints}

CRITICAL: Analyze the user prompt carefully and extract:
- Business/person names, titles, and roles
- Product/service descriptions and features
- Contact information if mentioned
- Any specific content, slogans, or messaging
- Target audience and value propositions

REQUIREMENTS:
1. Use ONLY {framework.upper()} 5.3 classes (no custom CSS)
2. Make it fully responsive (mobile-first)
3. Use semantic HTML5 tags
4. Include Bootstrap Icons where appropriate
5. Add proper ARIA labels for accessibility
6. Fill the section with REAL, RELEVANT content based on the prompt - NO generic placeholders
7. Use actual names, descriptions, features from the user's prompt
8. DO NOT include <!DOCTYPE>, <html>, <head>, or <body> tags - ONLY the component HTML
9. Make it professional and production-ready
10. If the prompt mentions specific details (e.g., "shopping site for amazonian warriors"), incorporate that theme throughout

STYLE GUIDELINES FOR "{style}":
{_get_style_guidelines(style)}

{_get_section_specific_requirements(section_type, framework)}

OUTPUT: Return ONLY the HTML component code with real content extracted from the prompt. No explanations, no markdown code blocks, just pure HTML.
"""
    
    return prompt


def _extract_content_hints(user_prompt: str, section_type: str) -> str:
    """
    Extract content-specific hints from the user prompt for this section.
    """
    prompt_lower = user_prompt.lower()
    hints = []
    
    # Extract business type and theme
    business_types = {
        "shop": "e-commerce/shopping",
        "store": "e-commerce/retail",
        "restaurant": "food service",
        "portfolio": "personal portfolio",
        "landing": "product landing page",
        "corporate": "corporate business",
        "startup": "tech startup",
        "agency": "creative agency"
    }
    
    for keyword, btype in business_types.items():
        if keyword in prompt_lower:
            hints.append(f"- Business type: {btype} - tailor ALL content to this industry")
            break
    
    # Extract names and entities
    if " for " in prompt_lower:
        parts = user_prompt.split(" for ")
        if len(parts) > 1:
            name = parts[1].split(" with ")[0].split(" using ")[0].strip()
            hints.append(f"- Primary entity/target: '{name}' - use this name prominently")
    
    # Section-specific content requirements
    section_guidance = {
        "hero": "Create a compelling headline and value proposition based on the prompt theme. Include 2 CTA buttons.",
        "about": "Write an 'About' section that explains the business/person based on prompt context.",
        "features": "Extract or infer 4-6 key features/services that align with the prompt's business type.",
        "testimonials": "Generate 3 realistic testimonials relevant to the business type mentioned.",
        "pricing": "Create 3 pricing tiers appropriate for the business type (Basic, Pro, Premium).",
        "contact": "Include a contact form with fields relevant to the business type.",
        "gallery": "Describe 6-8 portfolio items/products that fit the prompt's theme.",
        "navbar": "Include navigation links relevant to the business type.",
        "footer": "Add footer content with realistic company info based on the prompt.",
        "cta": "Write a compelling call-to-action that matches the business goal."
    }
    
    if section_type in section_guidance:
        hints.append(f"- Content goal: {section_guidance[section_type]}")
    
    # Extract specific themes/keywords
    hints.append(f"- Analyze this prompt for specific themes: '{user_prompt}'")
    hints.append("- Use the prompt's unique elements (e.g., 'amazonian warriors', 'tech startup') in the content")
    hints.append("- Make content specific and relevant - avoid generic text like 'Lorem ipsum' or 'Your Business'")
    
    return "\n".join(hints)


def _get_style_guidelines(style: str) -> str:
    """
    Get style-specific guidelines for the AI.
    """
    guidelines = {
        "modern": "Use clean lines, ample whitespace, gradient backgrounds, rounded corners, shadows",
        "minimal": "Minimalist design, lots of white space, simple typography, monochrome or limited colors",
        "corporate": "Professional, trustworthy, blue/gray colors, structured layout, formal tone",
        "creative": "Vibrant colors, unique layouts, playful elements, artistic flair",
        "dark": "Dark background, light text, high contrast, modern dark mode aesthetic",
        "retro": "Vintage elements, classic typography, nostalgic color palette"
    }
    return guidelines.get(style, guidelines["modern"])


def _get_section_specific_requirements(section_type: str, framework: str) -> str:
    """
    Get section-specific requirements and examples.
    """
    
    if framework.lower() == "bootstrap":
        requirements = {
            "navbar": """
NAVBAR REQUIREMENTS:
- Use navbar-expand-lg for responsive collapse
- Include brand logo/name
- Navigation links (Home, About, Services, Contact)
- Responsive hamburger menu for mobile
- Use navbar-dark bg-dark or navbar-light bg-light
- Example: <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
""",
            "hero": """
HERO REQUIREMENTS:
- Large, eye-catching heading (display-3 or display-4)
- Compelling subtitle/description
- 1-2 call-to-action buttons
- Optional hero image or background
- Use container and row/col for layout
- Example: <div class="bg-primary text-white py-5">
""",
            "features": """
FEATURES REQUIREMENTS:
- 3-6 feature cards using Bootstrap cards
- Icons for each feature (use Bootstrap Icons)
- Title and description for each
- Use row and col-md-4 for 3-column grid
- Example: <div class="row g-4">
""",
            "footer": """
FOOTER REQUIREMENTS:
- Multi-column layout (3-4 columns)
- Links, contact info, social media icons
- Copyright notice
- Use bg-dark text-white
- Example: <footer class="bg-dark text-white py-5">
""",
            "contact": """
CONTACT REQUIREMENTS:
- Contact form with name, email, subject, message
- Use Bootstrap form classes (form-control, form-label)
- Submit button (btn btn-primary)
- Optional contact information display
- Example: <form class="needs-validation">
""",
            "gallery": """
GALLERY REQUIREMENTS:
- Grid of images (3-4 columns)
- Use Bootstrap cards with img-top
- Hover effects (shadow)
- Responsive grid (col-md-4 or col-md-3)
- Example: <div class="row g-3">
""",
            "testimonials": """
TESTIMONIALS REQUIREMENTS:
- 3 testimonial cards
- Avatar image, name, role, quote
- 5-star rating using Bootstrap Icons
- Use card with card-body
- Example: <div class="card h-100">
""",
            "pricing": """
PRICING REQUIREMENTS:
- 3 pricing tiers (Basic, Pro, Enterprise)
- Price, features list, CTA button
- Highlight recommended plan (border-primary)
- Use cards with centered content
- Example: <div class="card h-100 border-0 shadow-sm">
""",
            "about": """
ABOUT REQUIREMENTS:
- Two-column layout (text + image)
- Company/person description
- Stats or achievements
- Use row with col-lg-6
- Example: <div class="row align-items-center">
""",
            "cta": """
CTA REQUIREMENTS:
- Bold, action-oriented heading
- Persuasive description
- Prominent call-to-action button(s)
- Use bg-primary or bg-gradient
- Example: <div class="bg-primary text-white py-5 text-center">
"""
        }
        return requirements.get(section_type, "")
    
    return ""


def _extract_html_from_response(response_text: str) -> str:
    """
    Extract clean HTML from AI response, removing any markdown or explanations.
    """
    # Remove markdown code blocks if present
    if "```html" in response_text:
        parts = response_text.split("```html")
        if len(parts) > 1:
            html_part = parts[1].split("```")[0]
            return html_part.strip()
    elif "```" in response_text:
        parts = response_text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    
    # If no code blocks, return the whole response (assuming it's HTML)
    return response_text.strip()


def _get_cache_key(section_type: str, user_prompt: str, framework: str, style: str) -> str:
    """
    Generate a cache key for the component.
    """
    content = f"{section_type}_{user_prompt}_{framework}_{style}"
    return hashlib.md5(content.encode()).hexdigest()


def _get_cached_component(section_type: str, user_prompt: str, framework: str, style: str) -> Optional[str]:
    """
    Retrieve cached component if available.
    """
    cache_key = _get_cache_key(section_type, user_prompt, framework, style)
    cache_file = CACHE_DIR / f"{cache_key}.html"
    
    if cache_file.exists():
        return cache_file.read_text(encoding='utf-8')
    
    return None


def _cache_component(section_type: str, user_prompt: str, framework: str, style: str, html: str):
    """
    Cache generated component for future use.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = _get_cache_key(section_type, user_prompt, framework, style)
    cache_file = CACHE_DIR / f"{cache_key}.html"
    
    cache_file.write_text(html, encoding='utf-8')


def generate_full_website_with_ai(
    user_prompt: str,
    intent: Dict,
    verbose: bool = True
) -> Dict[str, str]:
    """
    Generate all components for a website using AI.
    
    Args:
        user_prompt: Original user prompt
        intent: Parsed intent dictionary
        verbose: Whether to print progress
        
    Returns:
        Dictionary mapping section types to HTML components
    """
    if not MODEL:
        raise ValueError("Gemini API key not configured")
    
    sections = intent.get("sections", [])
    framework = intent.get("framework", "bootstrap")
    style = intent.get("style", "modern")
    
    additional_context = {
        "brand_name": intent.get("metadata", {}).get("brand_name", "My Website"),
        "colors": intent.get("colors", ["blue", "white"])
    }
    
    components = {}
    
    for section in sections:
        if verbose:
            print(f"  🤖 Generating {section} with Gemini AI...")
        
        try:
            html, metadata = generate_component_with_ai(
                section_type=section,
                user_prompt=user_prompt,
                framework=framework,
                style=style,
                additional_context=additional_context
            )
            
            components[section] = html
            
            if verbose:
                cached_status = "💾 (cached)" if metadata.get("cached") else "✨ (new)"
                print(f"    ✅ Generated {cached_status}")
                
        except Exception as e:
            if verbose:
                print(f"    ❌ Failed: {str(e)}")
            # Will be handled by fallback mechanism
            components[section] = None
    
    return components


def is_ai_available() -> bool:
    """
    Check if Gemini AI is configured and available.
    
    Returns:
        True if AI is available, False otherwise
    """
    return MODEL is not None


def clear_cache():
    """
    Clear all cached AI-generated components.
    """
    if CACHE_DIR.exists():
        import shutil
        shutil.rmtree(CACHE_DIR)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
