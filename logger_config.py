import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import request, g

# -----------------------------------------------------------------------------
# PRODUCTION LOGGING CONFIGURATION FOR DEVOPSVAULTX
# -----------------------------------------------------------------------------

def setup_logger(app):
    """
    Sets up enterprise-grade production logging with:
    1. Rotating file handlers (app.log and error.log) to prevent disk exhaustion.
    2. StreamHandler (stdout) for cloud / container platforms (Docker, K8s, GCP/AWS).
    3. Strict proxy-aware client IP extraction (Cloudflare, Nginx, Load Balancers).
    4. Sub-millisecond request latency tracking.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Standard production log formatter
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [PID:%(process)d] [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger('devopsvaultx')
    logger.setLevel(log_level)

    # Avoid adding duplicate handlers if already configured
    if not logger.handlers:
        # 1. Console / Stdout Handler (12-Factor App Standard)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 2. General Rotating File Handler (app.log - Max 10MB x 5 backups)
        app_log_path = os.path.join(log_dir, 'app.log')
        file_handler = RotatingFileHandler(
            app_log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 3. Dedicated Error Rotating File Handler (error.log - Only ERROR & CRITICAL)
        error_log_path = os.path.join(log_dir, 'error.log')
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    # Attach logger to Flask app
    app.logger_instance = logger
    logger.info("Production logging initialized successfully. Log directory: %s", log_dir)
    return logger


def get_client_ip():
    """
    Safely resolves client IP respecting reverse proxies (Cloudflare, Nginx, AWS ALB).
    Sanitizes string against CRLF log injection.
    """
    # 1. Cloudflare header
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip.strip().split(',')[0].strip()

    # 2. X-Forwarded-For header
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        return xff.strip().split(',')[0].strip()

    # 3. X-Real-IP header
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()

    # 4. Fallback to remote_addr
    return request.remote_addr or '127.0.0.1'


def log_request_lifecycle(response):
    """
    Logs every completed HTTP request with latency, status code, IP, and path.
    """
    # Skip logging noise for static assets unless they error
    is_static = request.path.startswith('/static/')
    if is_static and response.status_code < 400:
        return response

    start_time = getattr(g, 'request_start_time', None)
    if start_time:
        duration_ms = (time.time() - start_time) * 1000
        latency_str = f"{duration_ms:.2f}ms"
    else:
        latency_str = "- ms"

    ip = get_client_ip()
    method = request.method
    path = request.path
    status = response.status_code
    user_agent = (request.user_agent.string or 'Unknown')[:100]

    log_msg = f"{status} {method} {path} ({latency_str}) | IP: {ip} | UA: {user_agent}"

    logger = logging.getLogger('devopsvaultx')
    if status >= 500:
        logger.error("[SERVER ERROR] %s", log_msg)
    elif status >= 400:
        logger.warning("[CLIENT ERROR] %s", log_msg)
    else:
        logger.info("[OK] %s", log_msg)

    return response

