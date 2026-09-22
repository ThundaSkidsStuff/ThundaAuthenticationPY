from Settings.settings import Settings
import base64
import json
import time

# dont touch this
class Attestation:
    def CheckAttest(atr, nonce):
        attest = atr["data"]["claims"]
        decodedclaims = json.loads(base64.urlsafe_b64decode(attest + "=" * (-len(attest) % 4)))
        request_details = decodedclaims.get("request_details", {})
        app_state = decodedclaims.get("app_state", {})
        device_state = decodedclaims.get("device_state", {})
        device_ban = decodedclaims.get("device_ban", {})
        uniqueid = device_state.get("unique_id")

        if request_details.get("exp", 0) < time.time():
            return {"status": "expired", "code": 5}
        if request_details.get("nonce") != nonce:
            return {"status": "nonce mismatch", "code": 3}
        if app_state.get("app_integrity_state") != "StoreRecognized" or app_state.get("package_cert_sha256_digest") != Settings.packagecert:
            return {"status": "unknown apk", "code": 4}
        if app_state.get("package_id") != Settings.packagename:
            return {"status": "not my game", "code": 4}
        if device_state.get("device_integrity_state") != "Advanced":
            return {"status": "rooted device", "code": 4}
        if app_state.get("version") != Settings.updateattest:
            return {"status": "update required", "code": 1}
        if device_ban.get("is_banned") == True:
            return {"status": "banned", "code": 6, "uniqueid": uniqueid, "remaining": str(device_ban.get("remaining_ban_time"))}

        return {"status": "ok", "code": 0, "uniqueid": uniqueid, "attestdata": request_details.get("nonce")}
