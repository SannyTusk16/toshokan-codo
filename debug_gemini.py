"""
Debug Gemini API Connection
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Test 1: Check API key
print("Test 1: Check API Key")
api_key = os.getenv("GEMINI_API_KEY")
print(f"  API Key: {api_key[:20]}...{api_key[-5:]}" if api_key else "  ❌ Not found")

# Test 2: Import Gemini
print("\nTest 2: Import Google Generative AI")
try:
    import google.generativeai as genai
    print("  ✅ Import successful")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 3: Configure Gemini
print("\nTest 3: Configure Gemini")
try:
    genai.configure(api_key=api_key)
    print("  ✅ Configuration successful")
except Exception as e:
    print(f"  ❌ Configuration failed: {e}")
    sys.exit(1)

# Test 4: Initialize Model
print("\nTest 4: Initialize Model")
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    print("  ✅ Model initialized")
except Exception as e:
    print(f"  ❌ Model initialization failed: {e}")
    sys.exit(1)

# Test 5: Simple Generation
print("\nTest 5: Test Simple Generation")
try:
    response = model.generate_content("Say hello in one sentence")
    print(f"  ✅ Response: {response.text[:100]}")
except Exception as e:
    print(f"  ❌ Generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Component Generation
print("\nTest 6: Test Component Generation")
try:
    prompt = """Generate a simple Bootstrap 5 navbar with:
- Brand name: "John Doe Portfolio"
- Links: Home, About, Contact
Return ONLY the HTML, no explanations."""
    
    response = model.generate_content(prompt)
    html = response.text
    print(f"  ✅ Generated {len(html)} characters")
    print(f"  Preview: {html[:200]}...")
except Exception as e:
    print(f"  ❌ Component generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
