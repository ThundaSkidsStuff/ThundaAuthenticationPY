from Settings.settings import Settings
import requests

class PlayfabSDK:
    def Login(orgscope):
        headers = {"X-SecretKey": Settings.secretkey}
        body = {"ServerCustomId": "OCULUS" + str(orgscope), "CreateAccount": True}
        pfab = requests.post(f"https://{Settings.titleid}.playfabapi.com/Server/LoginWithServerCustomId", json=body, headers=headers)
        pf = pfab.json()
        if pfab.status_code != 200:
            if pf.get("error") == "AccountBanned":
                details = pf.get("errorDetails") or {}
                reason = next(iter(details), "unknown")
                expiry = details.get(reason, ["Indefinite"])[0]
                return {"status": "banned", "message": "you have been banned, reason: " + reason + ", expires: " + expiry, "code": 6}
            return {"status": "error", "message": "error logging in with playfab", "code": 2}
        data = pf["data"]
        return {"status": "ok", "code": 0, "vars": {"EntityToken": data["EntityToken"]["EntityToken"], "NewlyCreated": data["NewlyCreated"], "PlayFabId": data["PlayFabId"], "SessionTicket": data["SessionTicket"]}}
