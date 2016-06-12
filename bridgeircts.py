import sopel.module
import ts3


from sopel.module import commands
#Debut du tslist
@module.commands('tslist')

def tslist(bot, trigger):
	with ts3.query.TS3Connection("localhost") as ts3conn:
        ts3conn.login(
                client_login_name="",
                client_login_password=""
        )

