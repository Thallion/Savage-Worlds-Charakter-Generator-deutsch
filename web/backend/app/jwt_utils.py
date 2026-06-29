import base64
import hashlib
import hmac
import json
import time


class JWTError(Exception):
    pass


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    header = {"alg": algorithm, "typ": "JWT"}
    header_b64 = _b64_encode(json.dumps(header).encode())
    payload_b64 = _b64_encode(json.dumps(payload, default=str).encode())
    message = f"{header_b64}.{payload_b64}"
    sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    sig_b64 = _b64_encode(sig)
    return f"{message}.{sig_b64}"


def decode(token: str, secret: str, algorithms: list[str] | None = None) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTError("Ungültiges Token-Format")

        message = f"{parts[0]}.{parts[1]}"
        sig = _b64_decode(parts[2])
        expected_sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()

        if not hmac.compare_digest(sig, expected_sig):
            raise JWTError("Ungültige Signatur")

        payload = json.loads(_b64_decode(parts[1]))

        if "exp" in payload:
            exp = payload["exp"]
            if isinstance(exp, str):
                exp = float(exp)
            if exp < time.time():
                raise JWTError("Token abgelaufen")

        return payload
    except JWTError:
        raise
    except Exception as e:
        raise JWTError(f"Token-Fehler: {e}")
