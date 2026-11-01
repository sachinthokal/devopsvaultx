import json
import os
import time
from flask import Flask, redirect, render_template, Response, request, g
from logger_config import setup_logger, log_request_lifecycle

# Initialize the Flask application
app = Flask(__name__)

# Initialize Enterprise-Grade Production Logger
logger = setup_logger(app)

# Base directory for loading asset resources
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load tools data from static/data.json
with open(os.path.join(BASE_DIR, 'static', 'data.json'), 'r', encoding='utf-8') as f:
    TOOLS_DATA = json.load(f)

# Sort tools data: active first, then disabled
TOOLS_DATA = sorted(TOOLS_DATA, key=lambda x: (x.get('status') != 'active'))

# ------------------------------------------------------------------
# REQUEST LIFECYCLE HOOKS (Latency Tracking & Security Headers)
# ------------------------------------------------------------------
@app.before_request
def before_request_hook():
    # Record request start time for high-precision latency logging
    g.request_start_time = time.time()

@app.after_request
def apply_headers_and_log(response):
    # 1. Mitigate Clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # 2. Prevent MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # 3. Secure Origin Isolation
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    # 4. Strict Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # 5. Strong HSTS Policy (High Severity Lighthouse Best Practice)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    # 6. Permissions Policy
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    # 7. Content Security Policy in Enforcement Mode (High Severity Lighthouse Best Practice)
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:",
        "img-src 'self' data: blob: https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com https://*.google.com",
        "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://*.google.com data: blob:",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    response.headers['Content-Security-Policy'] = '; '.join(csp_directives)

    # 8. Production Request Lifecycle Logging
    return log_request_lifecycle(response)

# Homepage (Root URL) - Pre-renders all tools for instant crawler discovery & 100/100 LCP
@app.route('/')
def index():
    return render_template('index.html', tools=TOOLS_DATA)

# Contact Page
@app.route('/contact/')
def contact():
    return render_template('contact.html')

# About Page
@app.route('/about/')
def about():
    return render_template('about.html')

# HTML Sitemap Page
@app.route('/sitemap/')
def sitemap():
    return render_template('sitemap.html', tools=TOOLS_DATA)

# Search Engine Robots.txt
@app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://www.devopsvaultx.com/sitemap.xml\n"
    return Response(content, mimetype="text/plain")

# Search Engine XML Sitemap
@app.route('/sitemap.xml')
def sitemap_xml():
    base_url = "https://www.devopsvaultx.com"
    pages = [
        {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0"},
        {"loc": f"{base_url}/sitemap/", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/about/", "changefreq": "monthly", "priority": "0.6"},
        {"loc": f"{base_url}/contact/", "changefreq": "monthly", "priority": "0.6"},
    ]
    for tool in TOOLS_DATA:
        action_url = tool.get('actionUrl', '')
        if action_url and action_url.startswith('/'):
            pages.append({
                "loc": f"{base_url}{action_url}",
                "changefreq": "weekly",
                "priority": "0.9"
            })
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for page in pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{page["loc"]}</loc>')
        xml.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        xml.append(f'    <priority>{page["priority"]}</priority>')
        xml.append('  </url>')
    xml.append('</urlset>')
    return Response('\n'.join(xml), mimetype="application/xml")

# ------------------------------------------------------------------
# UNIVERSAL DAILY TOOLS & PDF UTILITIES (High Global Traffic)
# ------------------------------------------------------------------

# Merge PDF Files
@app.route('/merge-pdf/')
def merge_pdf():
    return render_template('merge-pdf.html')

# Image to PDF Converter
@app.route('/image-to-pdf/')
def image_to_pdf():
    return render_template('image-to-pdf.html')

# Word & Character Counter
@app.route('/word-counter/')
def word_counter():
    return render_template('word-counter.html')

# Free QR Code Generator
@app.route('/qr-code-generator/')
def qr_code_generator():
    return render_template('qr-code-generator.html')

# Strong Password Generator
@app.route('/password-generator/')
def password_generator():
    return render_template('password-generator.html')

# Percentage Calculator
@app.route('/percentage-calculator/')
def percentage_calculator():
    return render_template('percentage-calculator.html')

# Text Case Converter
@app.route('/text-case-converter/')
def text_case_converter():
    return render_template('text-case-converter.html')

# Digital Unit Converter
@app.route('/digital-unit-converter/')
def digital_unit_converter():
    return render_template('digital-unit-converter.html')

# Image Format Converter
@app.route('/image-converter/')
def image_converter():
    return render_template('image-converter.html')

# ------------------------------------------------------------------
# TECH & DEVELOPER UTILITIES
# ------------------------------------------------------------------

# CRON Schedule Guru
@app.route('/cron-expression-guru/')
def cron_expression_guru():
    return render_template('cron-expression-guru.html')

# Base64 Encoder/Decoder
@app.route('/base64-encoder-decoder/')   
def base64_encoder_decoder():
    return render_template('base64-encoder-decoder.html')

# IP CIDR Generator
@app.route('/ip-cidr-generator/')
def ip_cidr_generator():
    return render_template('ip-cidr-generator.html')

# Kubernetes YAML Generator
@app.route('/kubernetes-yaml-generator/')
def kubernetes_yaml_generator():
    return render_template('kubernetes-yaml-generator.html')

# ------------------------------------------------------------------
# ERROR HANDLERS (Production 404, 500 & Unhandled Exceptions)
# ------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.exception("Internal Server Error (500) encountered: %s", str(e))
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    # Log complete exception traceback with context in error.log
    logger.exception("Unhandled Exception: %s", str(e))
    return render_template('500.html'), 500

# ------------------------------------------------------------------
# APPLICATION RUNNER (Development & Production Compatible)
# ------------------------------------------------------------------
if __name__ == '__main__':
    # Can be configured via environment variables:
    # PORT=5000 FLASK_DEBUG=1 python3 app.py
    port = int(os.environ.get('PORT', 5000))
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1')
    logger.info("Starting DevOpsVaultX server on port %d (debug=%s)", port, is_debug)
    app.run(host='0.0.0.0', port=port, debug=is_debug)
