import hmac
import hashlib
from fastapi import Request, HTTPException, Header
from app.config import settings
from app.utils import logger

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature using GITHUB_WEBHOOK_SECRET."""
    if not settings.GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET is not set. Skipping signature verification.")
        return True
        
    if not signature_header:
        logger.error("Missing X-Hub-Signature-256 header.")
        return False
        
    try:
        sha_name, signature = signature_header.split('=')
    except ValueError:
        logger.error("Malformed X-Hub-Signature-256 header.")
        return False
        
    if sha_name != 'sha256':
        logger.error(f"Unsupported signature hash algorithm: {sha_name}")
        return False
        
    mac = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    return hmac.compare_digest(mac.hexdigest(), signature)

async def handle_github_webhook(request: Request, x_hub_signature_256: str = Header(None)) -> dict:
    """Validates and processes an incoming GitHub Webhook request."""
    payload_body = await request.body()
    
    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    repo_name = payload.get("repository", {}).get("full_name", "unknown")
    sender = payload.get("sender", {}).get("login", "unknown")
    
    logger.info(f"Verified GitHub Webhook: event={event_type}, repo={repo_name}, sender={sender}")
    
    # Process event logic (e.g., store pull request / commit info)
    return {
        "status": "verified",
        "event_type": event_type,
        "repository": repo_name,
        "sender": sender
    }
