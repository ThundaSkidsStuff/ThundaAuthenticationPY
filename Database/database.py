from tinydb import TinyDB, Query
from Settings.settings import Settings
import time

db = TinyDB(Settings.dbpath)

# dont touch this
class Database:
    attestation = db.table("attestation")
    bans = db.table("bans")
    attest = Query()
    def SavePreauth(attestid, attestdata, exp, iat, id):
        Database.attestation.insert({"id": id, "vars": {"attestid": attestid, "attestdata": attestdata}, "iat": iat, "exp": exp})

    def CheckPreauth(attestid, attestdata):
        at = Database.attest
        preauth2 = Database.attestation.get((at.vars.attestid == attestid) & (at.vars.attestdata == attestdata))
        if preauth2 is None:
            return "Invalid"
        if preauth2["exp"] < int(time.time()):
            return "Invalid"
        return "valid"
    def SaveBan(uniqueid, nonce, userid, username):
        Database.bans.insert({"id": userid, "vars": {"nonce": nonce, "attestuniqueid": uniqueid, "username": username}})
