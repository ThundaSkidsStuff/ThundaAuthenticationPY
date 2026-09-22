from Settings.settings import Settings
import jwt

class Jwt:
    def CreateJWT(username, userid, playfabid):
        thejwt = jwt.encode({"vars": {"username": username, "userid": userid, "playerid": playfabid}}, Settings.secretstring, algorithm="HS256")
        return thejwt

    def ValidateJWT(token):
        try:
            decoded = jwt.decode(token, Settings.secretstring, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"status": "expired", "code": 5}
        except jwt.InvalidTokenError:
            return {"status": "invalid token", "code": 7}
        return {"status": "ok", "code": 0, "vars": decoded}
