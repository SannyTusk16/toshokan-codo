"""
Online Component Fetcher Module
Fetches Bootstrap and other UI framework components from online sources.

Supports:
- Bootstrap component snippets from CDN/online repositories
- Caching for performance
- Fallback to default templates
"""

import requests
from pathlib import Path
from typing import Dict, Optional
import hashlib
import json

# Cache directory for downloaded components
CACHE_DIR = Path(".cache/online_components")
CACHE_ENABLED = True
CACHE_EXPIRY_DAYS = 7

# Bootstrap component templates (hosted online or from snippets)
BOOTSTRAP_ONLINE_COMPONENTS = {
    "navbar": """<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">{{ brand_name|default('My Website') }}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link active" href="#home">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="#about">About</a></li>
        <li class="nav-item"><a class="nav-link" href="#services">Services</a></li>
        <li class="nav-item"><a class="nav-link" href="#contact">Contact</a></li>
      </ul>
    </div>
  </div>
</nav>""",
    
    "hero": """<div class="bg-primary text-white py-5" id="home">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-lg-6">
        <h1 class="display-3 fw-bold mb-4">{{ hero_title|default('Welcome to Our Platform') }}</h1>
        <p class="lead mb-4">{{ hero_subtitle|default('Build amazing websites with modern UI frameworks and ready-to-use components.') }}</p>
        <div class="d-grid gap-2 d-md-flex">
          <a href="#contact" class="btn btn-light btn-lg px-4">{{ cta_primary_button|default('Get Started') }}</a>
          <a href="#about" class="btn btn-outline-light btn-lg px-4">{{ cta_secondary_button|default('Learn More') }}</a>
        </div>
      </div>
      <div class="col-lg-6 text-center">
        <img src="{{ hero_image|default('https://via.placeholder.com/500x400') }}" class="img-fluid rounded shadow" alt="Hero">
      </div>
    </div>
  </div>
</div>""",
    
    "features": """<section class="py-5" id="services">
  <div class="container">
    <div class="text-center mb-5">
      <h2 class="display-5 fw-bold">{{ features_title|default('Our Features') }}</h2>
      <p class="lead text-muted">{{ features_subtitle|default('Everything you need to succeed') }}</p>
    </div>
    <div class="row g-4">
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-lightning-charge-fill fs-1 text-primary mb-3"></i>
            <h5 class="card-title">Fast Performance</h5>
            <p class="card-text">Lightning-fast load times and optimized code for the best user experience.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-shield-check fs-1 text-primary mb-3"></i>
            <h5 class="card-title">Secure & Reliable</h5>
            <p class="card-text">Enterprise-grade security with 99.9% uptime guarantee.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-people-fill fs-1 text-primary mb-3"></i>
            <h5 class="card-title">24/7 Support</h5>
            <p class="card-text">Round-the-clock customer support to help you succeed.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    
    "footer": """<footer class="bg-dark text-white py-5">
  <div class="container">
    <div class="row">
      <div class="col-md-4 mb-4">
        <h5>{{ brand_name|default('My Website') }}</h5>
        <p class="text-muted">{{ about_text|default('Building amazing digital experiences.') }}</p>
      </div>
      <div class="col-md-4 mb-4">
        <h5>Quick Links</h5>
        <ul class="list-unstyled">
          <li><a href="#home" class="text-muted text-decoration-none">Home</a></li>
          <li><a href="#about" class="text-muted text-decoration-none">About</a></li>
          <li><a href="#services" class="text-muted text-decoration-none">Services</a></li>
          <li><a href="#contact" class="text-muted text-decoration-none">Contact</a></li>
        </ul>
      </div>
      <div class="col-md-4 mb-4">
        <h5>Contact</h5>
        <p class="text-muted">
          Email: {{ contact_email|default('hello@example.com') }}<br>
          Phone: {{ contact_phone|default('+1 (555) 123-4567') }}
        </p>
      </div>
    </div>
    <hr class="bg-secondary">
    <div class="text-center text-muted">
      <p>&copy; 2025 {{ brand_name|default('My Website') }}. All rights reserved.</p>
    </div>
  </div>
</footer>""",
    
    "contact": """<section class="py-5" id="contact">
  <div class="container">
    <div class="text-center mb-5">
      <h2 class="display-5 fw-bold">{{ contact_title|default('Get In Touch') }}</h2>
      <p class="lead text-muted">{{ contact_subtitle|default("We'd love to hear from you") }}</p>
    </div>
    <div class="row justify-content-center">
      <div class="col-lg-6">
        <form class="needs-validation" novalidate>
          <div class="mb-3">
            <label for="name" class="form-label">Name</label>
            <input type="text" class="form-control" id="name" required>
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" required>
          </div>
          <div class="mb-3">
            <label for="message" class="form-label">Message</label>
            <textarea class="form-control" id="message" rows="4" required></textarea>
          </div>
          <button type="submit" class="btn btn-primary btn-lg w-100">Send Message</button>
        </form>
      </div>
    </div>
  </div>
</section>""",
    
    "about": """<section class="py-5 bg-light" id="about">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-lg-6 mb-4 mb-lg-0">
        <img src="{{ about_image|default('https://via.placeholder.com/600x400') }}" class="img-fluid rounded shadow" alt="About Us">
      </div>
      <div class="col-lg-6">
        <h2 class="display-5 fw-bold mb-4">{{ about_title|default('About Us') }}</h2>
        <p class="lead">{{ about_text|default('We are a team of passionate individuals dedicated to creating exceptional digital experiences.') }}</p>
        <p class="text-muted">Since our founding, we've helped hundreds of clients achieve their goals through innovative solutions and dedicated support.</p>
        <div class="row mt-4">
          <div class="col-6">
            <h3 class="fw-bold text-primary">500+</h3>
            <p class="text-muted">Projects Completed</p>
          </div>
          <div class="col-6">
            <h3 class="fw-bold text-primary">100+</h3>
            <p class="text-muted">Happy Clients</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    
    "gallery": """<section class="py-5" id="gallery">
  <div class="container">
    <div class="text-center mb-5">
      <h2 class="display-5 fw-bold">{{ gallery_title|default('Our Work') }}</h2>
      <p class="lead text-muted">{{ gallery_subtitle|default('Check out our latest projects') }}</p>
    </div>
    <div class="row g-3">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <img src="https://via.placeholder.com/400x300" class="card-img-top" alt="Project 1">
          <div class="card-body">
            <h5 class="card-title">Project One</h5>
            <p class="card-text">An amazing project showcase</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <img src="https://via.placeholder.com/400x300" class="card-img-top" alt="Project 2">
          <div class="card-body">
            <h5 class="card-title">Project Two</h5>
            <p class="card-text">Another great project</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <img src="https://via.placeholder.com/400x300" class="card-img-top" alt="Project 3">
          <div class="card-body">
            <h5 class="card-title">Project Three</h5>
            <p class="card-text">Creative solutions delivered</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    
    "testimonials": """<section class="py-5 bg-light">
  <div class="container">
    <div class="text-center mb-5">
      <h2 class="display-5 fw-bold">{{ testimonials_title|default('What Our Clients Say') }}</h2>
      <p class="lead text-muted">{{ testimonials_subtitle|default("Don't just take our word for it") }}</p>
    </div>
    <div class="row g-4">
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
            </div>
            <p class="card-text">"Outstanding service and excellent results. Highly recommended!"</p>
            <div class="d-flex align-items-center mt-3">
              <img src="https://via.placeholder.com/50" class="rounded-circle me-3" alt="Client">
              <div>
                <h6 class="mb-0">John Doe</h6>
                <small class="text-muted">CEO, TechCorp</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
            </div>
            <p class="card-text">"Professional team that delivers quality work on time."</p>
            <div class="d-flex align-items-center mt-3">
              <img src="https://via.placeholder.com/50" class="rounded-circle me-3" alt="Client">
              <div>
                <h6 class="mb-0">Jane Smith</h6>
                <small class="text-muted">Founder, StartupXYZ</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
              <i class="bi bi-star-fill text-warning"></i>
            </div>
            <p class="card-text">"Exceeded our expectations in every way. Great experience!"</p>
            <div class="d-flex align-items-center mt-3">
              <img src="https://via.placeholder.com/50" class="rounded-circle me-3" alt="Client">
              <div>
                <h6 class="mb-0">Mike Johnson</h6>
                <small class="text-muted">Director, Digital Inc</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    
    "pricing": """<section class="py-5">
  <div class="container">
    <div class="text-center mb-5">
      <h2 class="display-5 fw-bold">{{ pricing_title|default('Simple Pricing') }}</h2>
      <p class="lead text-muted">{{ pricing_subtitle|default('Choose the plan that fits your needs') }}</p>
    </div>
    <div class="row g-4">
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title">Basic</h5>
            <div class="display-4 fw-bold my-4">$9<small class="fs-6 text-muted">/mo</small></div>
            <ul class="list-unstyled">
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>1 User</li>
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>5 Projects</li>
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Basic Support</li>
            </ul>
            <button class="btn btn-outline-primary w-100 mt-4">Get Started</button>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-primary shadow">
          <div class="card-body text-center">
            <span class="badge bg-primary mb-2">Popular</span>
            <h5 class="card-title">Pro</h5>
            <div class="display-4 fw-bold my-4">$29<small class="fs-6 text-muted">/mo</small></div>
            <ul class="list-unstyled">
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>5 Users</li>
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Unlimited Projects</li>
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Priority Support</li>
            </ul>
            <button class="btn btn-primary w-100 mt-4">Get Started</button>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title">Enterprise</h5>
            <div class="display-4 fw-bold my-4">$99<small class="fs-6 text-muted">/mo</small></div>
            <ul class="list-unstyled">
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Unlimited Users</li>
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Unlimited Projects</li>
              <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>24/7 Support</li>
            </ul>
            <button class="btn btn-outline-primary w-100 mt-4">Contact Us</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>""",
    
    "cta": """<section class="bg-primary text-white py-5">
  <div class="container text-center">
    <h2 class="display-4 fw-bold mb-4">{{ cta_title|default('Ready to Get Started?') }}</h2>
    <p class="lead mb-4">{{ cta_subtitle|default('Join thousands of satisfied customers today') }}</p>
    <div class="d-grid gap-2 d-md-flex justify-content-md-center">
      <button class="btn btn-light btn-lg px-5">{{ cta_primary_button|default('Get Started Now') }}</button>
      <button class="btn btn-outline-light btn-lg px-5">{{ cta_secondary_button|default('Learn More') }}</button>
    </div>
  </div>
</section>"""
}


def get_online_component(section: str, framework: str = "bootstrap") -> Optional[str]:
    """
    Fetch a component from online sources.
    
    Args:
        section: Section type (navbar, hero, etc.)
        framework: UI framework (bootstrap, tailwind, etc.)
        
    Returns:
        HTML content of the component or None if not found
    """
    if framework.lower() == "bootstrap":
        return BOOTSTRAP_ONLINE_COMPONENTS.get(section)
    
    return None


def fetch_component_from_url(url: str, cache_key: str) -> Optional[str]:
    """
    Fetch a component from a URL with caching.
    
    Args:
        url: URL to fetch component from
        cache_key: Unique key for caching
        
    Returns:
        Component HTML content or None
    """
    # Check cache first
    if CACHE_ENABLED:
        cached = _get_cached_component(cache_key)
        if cached:
            return cached
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        
        # Cache the result
        if CACHE_ENABLED:
            _cache_component(cache_key, content)
        
        return content
        
    except Exception as e:
        print(f"⚠️  Failed to fetch component from {url}: {str(e)}")
        return None


def _get_cache_key(identifier: str) -> str:
    """Generate cache key from identifier."""
    return hashlib.md5(identifier.encode()).hexdigest()


def _get_cached_component(cache_key: str) -> Optional[str]:
    """Retrieve cached component."""
    cache_file = CACHE_DIR / f"{cache_key}.html"
    
    if cache_file.exists():
        try:
            return cache_file.read_text(encoding='utf-8')
        except:
            return None
    
    return None


def _cache_component(cache_key: str, content: str):
    """Cache component content."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.html"
    
    try:
        cache_file.write_text(content, encoding='utf-8')
    except Exception as e:
        print(f"⚠️  Failed to cache component: {str(e)}")


def list_available_online_components(framework: str = "bootstrap") -> list:
    """
    List all available online components for a framework.
    
    Args:
        framework: UI framework name
        
    Returns:
        List of available section names
    """
    if framework.lower() == "bootstrap":
        return list(BOOTSTRAP_ONLINE_COMPONENTS.keys())
    
    return []
