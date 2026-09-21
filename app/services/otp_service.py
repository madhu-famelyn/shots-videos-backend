import urllib.request
import urllib.parse
import urllib.error
import json
import logging
from typing import Tuple, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class OTPService:
    @staticmethod
    def _format_mobile(phone: str) -> str:
        """Format 10-digit phone to 91XXXXXXXXXX format for MSG91."""
        clean = "".join(filter(str.isdigit, phone))
        if len(clean) == 10:
            return f"91{clean}"
        if len(clean) == 12 and clean.startswith("91"):
            return clean
        return clean

    @classmethod
    def send_otp(cls, phone: str) -> Dict[str, Any]:
        """Send OTP to user's mobile number via MSG91 API."""
        formatted_mobile = cls._format_mobile(phone)
        authkey = settings.MSG91_AUTH_KEY

        if not authkey:
            logger.warning("MSG91_AUTH_KEY not set. Using dev fallback.")
            return {"success": True, "message": f"Dev OTP sent to +{formatted_mobile} (Code: 1234)"}

        # Build query parameters
        params = {
            "mobile": formatted_mobile,
            "authkey": authkey,
            "otp_length": str(settings.MSG91_OTP_LENGTH),
            "otp_expiry": "10"
        }
        if settings.MSG91_TEMPLATE_ID:
            params["template_id"] = settings.MSG91_TEMPLATE_ID

        url = f"https://control.msg91.com/api/v5/otp?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, method="POST")
        req.add_header("authkey", authkey)
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                if data.get("type") == "success" or response.status == 200:
                    return {
                        "success": True,
                        "message": f"OTP sent to +{formatted_mobile}",
                        "request_id": data.get("request_id")
                    }
                else:
                    return {
                        "success": False,
                        "message": data.get("message", "Failed to send OTP")
                    }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"MSG91 Send OTP HTTP error {e.code}: {err_body}")
            try:
                err_data = json.loads(err_body)
                msg = err_data.get("message", f"SMS Gateway Error ({e.code})")
            except Exception:
                msg = f"SMS Gateway Error ({e.code})"
            return {"success": False, "message": msg}
        except Exception as e:
            logger.error(f"MSG91 Send OTP Exception: {e}")
            return {"success": False, "message": "Failed to connect to SMS Gateway"}

    @classmethod
    def verify_otp(cls, phone: str, otp: str) -> Tuple[bool, str]:
        """Verify OTP with MSG91 API."""
        formatted_mobile = cls._format_mobile(phone)
        authkey = settings.MSG91_AUTH_KEY

        # Development / master demo bypass
        if otp in ["1234", "123456", "9999"]:
            logger.info("Universal Dev OTP accepted.")
            return True, "OTP verified successfully (Dev bypass)"

        if not authkey:
            return False, "SMS Gateway not configured"

        params = {
            "mobile": formatted_mobile,
            "otp": otp.strip()
        }
        url = f"https://control.msg91.com/api/v5/otp/verify?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url, method="GET")
        req.add_header("authkey", authkey)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                if data.get("type") == "success" or data.get("message") == "OTP verified success":
                    return True, "OTP verified successfully"
                else:
                    return False, data.get("message", "Invalid OTP")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"MSG91 Verify OTP HTTP error {e.code}: {err_body}")
            try:
                err_data = json.loads(err_body)
                msg = err_data.get("message", "Invalid or expired OTP")
            except Exception:
                msg = "Invalid or expired OTP"
            return False, msg
        except Exception as e:
            logger.error(f"MSG91 Verify OTP Exception: {e}")
            return False, "Failed to connect to OTP verification service"

otp_service = OTPService()
