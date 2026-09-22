import os

class Settings: # use env variables for better protection but you should still be good
    titleid = os.environ.get("TITLEID", "")
    # DO NOT SHARE ANYTHING BELOW THIS
    secretkey = os.environ.get("SECRETKEY", "")
    secretstring = os.urandom(32) # change this, if you are using vercel or sum liek dat
    secrettoken = "OC|" # < find this in ur api section in ur app
    # actual settings
    UseOculusUsername = False
    Update = "YourUpdate"
    # package stuff
    packagename = ""
    updateattest = ""
    packagecert = ""
    # db stuff
    dbpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Database", "tinydb", "tinydb.db")
