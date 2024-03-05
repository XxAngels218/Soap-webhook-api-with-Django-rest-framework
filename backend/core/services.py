# services.py
import hmac
import hashlib

def verify_signature(body, signature, secret):
    """Verifica la firma HMAC de la solicitud."""
    hmac_digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_digest, signature)
