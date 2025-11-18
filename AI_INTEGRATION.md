# AI Integration - Gemini Component Generation

## Overview

Toshokan-Codo now includes AI-powered component generation using Google's Gemini 2.0 Flash model. The system can dynamically generate Bootstrap 5 components based on user prompts, extract actual content (names, descriptions, etc.), and intelligently cache results.

## Features

### 🤖 AI-Powered Generation
- **Dynamic Components**: Generate custom Bootstrap components on-the-fly
- **Content Extraction**: Automatically extracts names, descriptions, and context from user prompts
- **Multi-Modal Support**: Ready for image/video inputs to enhance component generation
- **Style Guidelines**: Bootstrap 5 best practices built-in

### 💾 Intelligent Caching
- **MD5-based**: Caches components by prompt hash for instant reuse
- **Persistent**: Cache stored in `.cache/ai_components/`
- **Efficient**: Avoids redundant API calls for identical prompts

### 📦 Fallback System
- **Graceful Degradation**: Falls back to pre-defined Bootstrap components if AI fails
- **Configurable**: Can disable AI with `--no-ai` flag or `.env` setting
- **Robust**: Never fails due to API issues

## Setup

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Environment

Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your API key:
```ini
# Gemini API Configuration
GEMINI_API_KEY=your_actual_api_key_here

# Enable AI Generation
USE_AI_GENERATION=true

# Gemini Model (default: gemini-2.0-flash-exp)
GEMINI_MODEL=gemini-2.0-flash-exp

# Cache Settings
AI_CACHE_DIR=.cache/ai_components
AI_CACHE_ENABLED=true
```

### 3. Verify Installation

Run the AI integration test:
```powershell
python test_ai_integration.py
```

Expected output:
```
🤖 AI INTEGRATION TEST - GEMINI COMPONENT GENERATION
======================================================================

📋 Configuration Check:
  GEMINI_API_KEY: ✅ Set
  USE_AI_GENERATION: True

📝 Test Prompt:
  "Build a portfolio website for John Doe, a software engineer..."

🧠 Stage 1: Parsing Intent...
  ✅ Framework: bootstrap
  ✅ Sections: hero, about, portfolio, contact

🗺️  Stage 2: Component Mapping...
  ✅ Mapped 4 components

  📊 AI Generation Stats:
     🤖 AI Generated: 4
     💾 From Cache: 0
     📦 Fallback: 0

  ✅ AI generation working!
```

## Usage

### Basic Usage (AI Enabled)

```powershell
python src/main.py "Build a portfolio for Sarah Miller, a graphic designer"
```

Output:
```
Stage 2: 🗺️  Mapping Components...
  ✅ Mapped 4 components
  🤖 AI Generated: 4 | Cached: 0 | Fallback: 0
     hero → 🤖 AI Generated
     about → 🤖 AI Generated
     portfolio → 🤖 AI Generated
     contact → 🤖 AI Generated
```

### Disable AI (Use Pre-defined Components)

```powershell
python src/main.py "Build a portfolio" --no-ai
```

### Content-Rich Prompts

The AI extracts actual content from your prompts:

```powershell
python src/main.py "Create a restaurant website for 'The Golden Spoon', an Italian fine dining restaurant in downtown Chicago specializing in homemade pasta"
```

The AI will:
- Use "The Golden Spoon" as the restaurant name
- Extract "Italian fine dining" as the description
- Include "homemade pasta" in the specialties
- Reference "downtown Chicago" as the location

### Multi-Modal Input (Future)

```powershell
# Not yet implemented, but architecture supports:
python src/main.py "Build a portfolio" --image logo.png --style-ref reference.jpg
```

## How It Works

### Architecture

```
User Prompt
    ↓
Intent Parser (sections, framework, style)
    ↓
Component Mapper
    ├─→ Check .env: USE_AI_GENERATION?
    │   ├─ Yes → Gemini Generator
    │   │   ├─→ Check Cache (MD5 hash)
    │   │   │   ├─ Hit → Return cached HTML
    │   │   │   └─ Miss → Call Gemini API
    │   │   │       ├─→ Extract content hints
    │   │   │       ├─→ Build prompt with guidelines
    │   │   │       ├─→ Parse HTML from response
    │   │   │       └─→ Cache result
    │   │   └─→ Return AI components
    │   └─ No → Pre-defined Components
    └─→ Component Map + AI Metadata
        ↓
Assembler
    ├─→ Check for "AI_GENERATED:" markers
    │   ├─ Yes → Retrieve from cache
    │   └─ No → Read from file
    └─→ Combine into complete HTML
        ↓
Output (dist/website.html)
```

### Content Extraction

The `_extract_content_hints()` function uses regex patterns to find:

- **Names**: "John Doe", "Sarah Miller", "The Golden Spoon"
- **Titles**: "Software Engineer", "Graphic Designer"
- **Company Names**: TechStart, Acme Corp
- **Descriptions**: "specializing in web development"
- **Locations**: "downtown Chicago", "San Francisco"

### Prompt Engineering

For each component, the AI generator:

1. **Applies Bootstrap Guidelines**:
   - Use utility classes (mt-3, p-4, text-center)
   - Responsive grid system (container, row, col-md-6)
   - Component classes (navbar, card, btn-primary)

2. **Section-Specific Requirements**:
   - **Hero**: Large headings, CTAs, background images
   - **About**: Text-heavy, team photos, mission statements
   - **Portfolio**: Grid layout, project cards, filtering
   - **Contact**: Forms, maps, social links

3. **Injects Extracted Content**:
   - Replaces "Your Name" with "John Doe"
   - Uses actual descriptions instead of placeholders

### Caching System

Cache location: `.cache/ai_components/`

Cache key: `MD5(prompt + section + style + framework)`

Example cache file:
```
.cache/ai_components/a3f4b2c1d5e6f7g8h9i0j1k2l3m4n5o6.html
```

Cache invalidation:
- Different prompt → New cache file
- Different section → New cache file
- Manual: Delete `.cache/ai_components/`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *required* | Your Google AI API key |
| `USE_AI_GENERATION` | `true` | Enable/disable AI globally |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model to use |
| `AI_CACHE_DIR` | `.cache/ai_components` | Cache directory |
| `AI_CACHE_ENABLED` | `true` | Enable/disable caching |

### Component Registry

`components/component_registry.json`:
```json
{
  "default_framework": "bootstrap",
  "frameworks": {
    "bootstrap": {
      "name": "Bootstrap 5",
      "version": "5.3.0",
      "cdn": {
        "css": [
          "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
          "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
        ],
        "js": [
          "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
        ]
      },
      "components": {
        "navbar": "components/online_kits/bootstrap/navbar.html",
        "hero": "components/online_kits/bootstrap/hero.html",
        ...
      }
    }
  }
}
```

## Troubleshooting

### API Key Issues

**Error**: `Invalid API key`
```
Solution: 
1. Check .env file has correct key
2. Verify no extra spaces/quotes
3. Regenerate key in Google AI Studio
```

**Error**: `API key not found`
```
Solution:
1. Ensure .env exists (not just .env.example)
2. Check .env is in project root
3. Restart Python process to reload env
```

### Rate Limits

**Error**: `429 Resource Exhausted`
```
Solution:
1. Wait 60 seconds and retry
2. Use --no-ai flag temporarily
3. Enable caching to reduce calls
```

### Content Not Extracted

**Issue**: Generic placeholders instead of actual content

```
Solution:
1. Make prompts more specific:
   ❌ "Build a portfolio"
   ✅ "Build a portfolio for John Doe, a software engineer"

2. Use descriptive language:
   ❌ "Make a website"
   ✅ "Create a restaurant website for 'Pasta Palace'"
```

### Cache Issues

**Issue**: Stale components being served

```
Solution:
1. Clear cache: Remove-Item -Recurse .cache/ai_components
2. Disable cache temporarily: Set AI_CACHE_ENABLED=false in .env
3. Use different wording in prompt to generate new cache key
```

### Fallback to Pre-defined Components

If you see `📦 Fallback: 4`, AI generation failed. Check:

1. **API Key**: Set correctly in `.env`?
2. **USE_AI_GENERATION**: Set to `true`?
3. **Network**: Can reach Google AI API?
4. **Quota**: Haven't exceeded free tier limits?

## Best Practices

### Writing Effective Prompts

✅ **Good Prompts**:
- "Build a portfolio for Sarah Chen, a UX designer specializing in mobile apps"
- "Create a restaurant website for 'The Golden Spoon', an Italian fine dining establishment"
- "Make a landing page for TechStart, a B2B SaaS company offering project management tools"

❌ **Poor Prompts**:
- "Build a website" (too vague)
- "Make something cool" (no content)
- "Portfolio" (one word, no context)

### Optimizing for Speed

1. **Use Caching**: Identical prompts = instant results
2. **Batch Similar Requests**: Cache warming for common patterns
3. **Fallback Mode**: Use `--no-ai` for testing/development

### Cost Management

Gemini 2.0 Flash is extremely affordable:
- **Free Tier**: 1,500 requests/day
- **Paid**: ~$0.001 per request

Tips:
- Enable caching (default: ON)
- Use fallback for non-production
- Monitor usage in Google AI Studio

## API Reference

### `gemini_generator.py`

#### `generate_component_with_ai(section, user_prompt, style, framework)`

Generate a single component.

**Parameters**:
- `section` (str): Section type (hero, about, contact, etc.)
- `user_prompt` (str): Original user prompt
- `style` (str): Style preference (modern, minimalist, etc.)
- `framework` (str): UI framework (bootstrap, tailwind, etc.)

**Returns**:
- `dict`: `{"success": bool, "html": str, "from_cache": bool, "error": str}`

**Example**:
```python
from src.gemini_generator import generate_component_with_ai

result = generate_component_with_ai(
    section="hero",
    user_prompt="Build portfolio for John Doe",
    style="modern",
    framework="bootstrap"
)

if result["success"]:
    print(result["html"])
```

#### `generate_full_website_with_ai(sections, user_prompt, style, framework)`

Generate multiple components in one call.

**Parameters**:
- `sections` (list): List of section types
- `user_prompt` (str): Original user prompt
- `style` (str): Style preference
- `framework` (str): UI framework

**Returns**:
- `dict`: `{section: {"success": bool, "html": str, ...}, ...}`

### `component_mapper.py`

#### `map_sections_to_components(intent, registry, user_prompt, use_ai)`

Map sections to components (AI or pre-defined).

**Parameters**:
- `intent` (dict): Parsed intent from intent_parser
- `registry` (dict): Component registry
- `user_prompt` (str, optional): User prompt for AI generation
- `use_ai` (bool): Whether to use AI generation

**Returns**:
- `tuple`: `(component_map, ai_metadata)`

**Example**:
```python
from src.component_mapper import map_sections_to_components

component_map, metadata = map_sections_to_components(
    intent={"sections": ["hero", "about"], "framework": "bootstrap"},
    registry=load_component_registry(),
    user_prompt="Build portfolio for Sarah",
    use_ai=True
)

print(f"AI generated: {metadata['ai_generated']}")
print(f"From cache: {metadata['from_cache']}")
```

## Examples

### Example 1: Portfolio with AI

```powershell
python src/main.py "Build a portfolio for Alex Rivera, a full-stack developer with 5 years of experience in React and Node.js"
```

Generated content will include:
- Name: "Alex Rivera"
- Title: "Full-Stack Developer"
- Experience: "5 years"
- Skills: "React, Node.js"

### Example 2: Restaurant Website

```powershell
python src/main.py "Create a website for Bella Napoli, a family-owned Italian restaurant in Brooklyn serving authentic Neapolitan pizza since 1985"
```

Generated content will include:
- Restaurant: "Bella Napoli"
- Type: "Italian restaurant"
- Location: "Brooklyn"
- Specialty: "Neapolitan pizza"
- Heritage: "Since 1985", "Family-owned"

### Example 3: Startup Landing Page

```powershell
python src/main.py "Make a landing page for CloudSync, a B2B SaaS platform that helps teams collaborate on documents in real-time with AI-powered suggestions"
```

Generated content will include:
- Product: "CloudSync"
- Category: "B2B SaaS"
- Features: "Real-time collaboration", "AI-powered suggestions"
- Target: "Teams"

## Roadmap

### Planned Features

- [ ] **Multi-modal input**: Image references for style/layout
- [ ] **Component variants**: Generate multiple options, let user choose
- [ ] **Style consistency**: Maintain design tokens across components
- [ ] **A/B testing**: Generate variant versions automatically
- [ ] **Localization**: Multi-language content generation
- [ ] **SEO optimization**: AI-generated meta tags, structured data
- [ ] **Accessibility**: WCAG compliance checks and fixes

### Model Upgrades

Currently using: `gemini-2.0-flash-exp`

Future options:
- `gemini-2.0-pro`: Better quality (slower, more expensive)
- `gemini-1.5-flash`: Faster (lower quality)
- Custom fine-tuned models for specific industries

## Support

For issues or questions:

1. Check `.env` configuration
2. Run `python test_ai_integration.py`
3. Review error messages in console
4. Check Google AI Studio for quota/limits
5. Open an issue with full error trace

## License

Same as main project.
