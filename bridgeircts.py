import sopel.module
import ts3

from sopel.module import commands

@commands('tslist')
def tslist(bot,trigger):
	with ts3.query.TS3Connection("localhost") as ts3conn:
		try:
			ts3conn.login(
				client_login_name="serveradmin",
				client_login_password="XXXXXX"
			)
		except ts3.query.TS3QueryError as err:
			bot.say("Login failed: "+ err.resp.error["msg"])
			exit(1)

		ts3conn.use(sid=1)

		# récupérer la liste des channels
		clistresp = ts3conn.channellist()
		clist = {}
		for channel in clistresp.parsed:
			clist[channel["cid"]] = channel["channel_name"]


		# récuperer la liste des clients
		resp=ts3conn.clientlist()
		listeClient = {}
		for client in resp.parsed:
			#Ignore ServerQuery (ex: 127.0.0.1:5402) Client in the result
			if client["client_type"] != "1":
				cid = client["cid"]
				if not(cid in listeClient):
					listeClient[cid] = []
				listeClient[cid].append(client["client_nickname"])


                # exploiter les listes
		if not listeClient:
			bot.say("Il n'y a personne")
		else:
			for cid, channelName in clist.items():
				if cid in listeClient:
					bot.say(channelName)
					for clientName in listeClient[cid]:
						bot.say("   " + clientName)
					
#Trigger .tsstalk
@commands('tstalk')
def tstalk(bot,trigger):
	with ts3.query.TS3Connection("localhost") as ts3conn:
		try:
			ts3conn.login(
				client_login_name="serveradmin",
				client_login_password="XXXX"
			)
		except ts3.query.TS3QueryError as err:
			bot.say("Login failed: "+ err.resp.error["msg"])
			exit(1)

		ts3conn.use(sid=1)
		
		# on récupère le message
		if not trigger.group(2):
			bot.reply("Et ton message boulet ?")
		else:
			message = "<IRC - " + trigger.nick + "> " + trigger.group(2)
			print(message)
			ts3conn.gm(msg=message)

#EVENT HANDLING BITCH

tsListening = False

@commands('tsstart')
def tsstart(bot, trigger):

	global tsListening

	if tsListening == True:
		return
	else:
		tsListening = True

	with ts3.query.TS3Connection("localhost") as ts3conn:
		try:
			ts3conn.login(
				client_login_name="serveradmin",
				client_login_password="wakuun42!"
			)
		except ts3.query.TS3QueryError as err:
			bot.say("Login failed: "+ err.resp.error["msg"])
			exit(1)

		ts3conn.use(sid=1)
		
		ts3conn.servernotifyregister(event="server")
		ts3conn.servernotifyregister(event="textserver")
		bot.say("Connexion TS<->IRC lancée")

		# Dict des clid <-> pseudos
		clidpseudo = {}
		# clidServer
		clidServer = -1

		while tsListening:
			event = ts3conn.wait_for_event()
	
			# DEBUG
			for value in event:
				print(value)
			# tri des events avec ajout de condition szupplémentaire dans le IF pour éviter que les serverquery apparaissent soit en join.quit soit en message (ex : message tstalk arrivant dans le chat Teamspeak est considéré comme un event et donc le bot tente de le dire aussi sur IRC
			if 'targetmode' in event[0] and event[0]["invokerid"] != 0:
				# invokerid= 0 --> Server
				# Du texte a été prononcé sur TS
				bot.say("<TS> " + event[0]["invokername"] + ": " + event[0]["msg"])
			elif 'reasonid' in event[0]:
				# Quelqu'un rentre ou sort du serveur

				if event[0]["reasonid"] == "0":
					# Entrée sur le serveur
					if "serveradmin from 127.0.0.1" in event[0]["client_nickname"]:
						# C'est le serveur qui se connecte
						clidServer = event[0]["clid"]
					else:
						# C'est un humain qui se connecte
						# On associe son pseudo à son clid
						bot.say(event[0]["client_nickname"] + " est entré sur Teamspeak")
						clidpseudo[event[0]["clid"]] = event[0]["client_nickname"]
					
				else:
					# le client QUITTE le serveur
					if event[0]["clid"] != clidServer:
						# Ce n'est pas le Server, c'est un humain
						bot.say(clidpseudo[event[0]["clid"]] + " a quitté Teamspeak")
						del clidpseudo[event[0]["clid"]


@commands('tsstop')
def tsstop(bot, trigger):
	ts3conn.servernotifyunregister()
	tsListening = False
	bot.say("Connexion TS<->IRC arrêtée")

