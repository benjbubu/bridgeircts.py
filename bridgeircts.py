import sopel.module
import ts3


from sopel.module import commands
#Debut du tslist
@commands('tslist')
#Definition des login/mdp du serverquery
def tslist(bot, trigger):
	with ts3.query.TS3Connection("localhost") as ts3conn:
        ts3conn.login(
                client_login_name="",
                client_login_password=""
        )
#Selection du serveur virtuel
ts3conn.use(sid=1)
