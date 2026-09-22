from flask import Blueprint, request, jsonify
from Settings.settings import Settings
from Database.database import Database
from Attestation.attestation import Attestation
from Tokens.tokens import Jwt
from Playfab.playfab import PlayfabSDK
import requests
import secrets
import hashlib
import hmac
import uuid
import time

route = Blueprint("api", __name__)

# codes
# 0 = everything good
# 1 = update required
# 2 = playfab nonexistant (incorrect setup, your fault)
# 3 = authentication fail (usually invalid credentials, user is modding)
# 4 = invalid attestation (root or invalid signature)
# 5 = something expiredd
# 6 = banned
# 7 = invalid jwt

class Api:
    @route.route("/v1/account/authenticate/preauth", methods=["POST"])
    def PreAuth():
        body = request.get_json(silent=True) or {}
        nonce = body.get("nonce")
        userid = body.get("userid")
        if not nonce or not userid:
            return jsonify({"message": "missing fields", "code": 7}), 400
        # nonce check
        noncecheck = requests.post("https://graph.oculus.com/user_nonce_validate", params={"access_token": Settings.secrettoken, "user_id": userid, "nonce": nonce})
        if noncecheck.json().get("is_valid") != True:
            return jsonify({"message": "nonce check failed", "code": 3})
        attestdata = hmac.new(Settings.secretstring, secrets.token_hex(16).encode(), hashlib.sha256).hexdigest()
        attestid = str(uuid.uuid4())
        iat = int(time.time())
        exp = iat + 30
        Database.SavePreauth(attestid, attestdata, exp, iat, userid)
        return jsonify({"appsafety": {"AttestData": attestdata, "AttestID": attestid}, "iat": iat, "exp": exp})

    @route.route("/v1/account/authenticate/custom", methods=["POST"])
    def login():
        username = request.args.get("username")
        body = request.get_json(silent=True) or {}
        id = body.get("id")
        vars = body.get("vars", {})
        attestid = vars.get("attestId")
        attestdata = vars.get("attestData")
        update = vars.get("ClientUserAgent")
        nonce = vars.get("nonce")
        if not id or not nonce or not attestid or not attestdata:
            return jsonify({"message": "missing fields", "code": 7}), 400
        if update != Settings.Update:
            return jsonify({"message": "Update Required", "code": 1})
        noncecheck = requests.post("https://graph.oculus.com/user_nonce_validate", params={"access_token": Settings.secrettoken, "user_id": id, "nonce": nonce})
        if noncecheck.json().get("is_valid") != True:
            return jsonify({"message": "nonce check failed", "code": 3})
        attestresponse = requests.post("https://graph.oculus.com/platform_integrity/verify", params={"token": attestdata, "access_token": Settings.secrettoken})
        jsn = attestresponse.json()
        if jsn.get("data", {}).get("message") != "Success":
            return jsonify({"message": "App or Device Not Supported", "code": 4})
        postattestcheck = Attestation.CheckAttest(jsn, nonce)
        if postattestcheck["status"] == "banned":
            Database.SaveBan(postattestcheck["uniqueid"], nonce, id, username)
            return jsonify({"message": "you have been banned, remaining time: " + postattestcheck["remaining"], "code": 6})
        if postattestcheck["status"] != "ok":
            return jsonify({"message": postattestcheck["status"], "code": postattestcheck["code"]})
        if Database.CheckPreauth(attestid, postattestcheck["attestdata"]) == "Invalid":
            return jsonify({"message": "attestation mismatch", "code": 4})
        pflogin = PlayfabSDK.Login(id)
        if pflogin["status"] != "ok":
            return jsonify({"message": pflogin["message"], "code": pflogin["code"]})
        token = Jwt.CreateJWT(username, id, pflogin["vars"]["PlayFabId"])
        return jsonify({"message": "logged in", "code": 0, "token": token, "PlayFabId": pflogin["vars"]["PlayFabId"], "SessionTicket": pflogin["vars"]["SessionTicket"]})
