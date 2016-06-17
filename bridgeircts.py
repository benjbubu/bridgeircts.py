import sopel.module
import ts3

from sopel.module import commands

@commands('tslist')
def tslist(bot,trigger):
	with ts3.query.TS3Connection("localhost") as ts3conn:
		try:
			ts3conn.login(
				client_login_name="serveradmin",
				client_login_password="XXXXX"
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

		while tsListening:
			event = ts3conn.wait_for_event()
	
			# DEBUG
			for value in event:
				print(value)
			# tri des events
			if 'targetmode' in event[0]:
				bot.say("message provenant de TS")
			elif 'reasonid' in event[0]:
				print("test")
			elif event[0]["reasonid"] == "0":
				bot.say("Machin a rejoint TS")
			else:
			#event[0]["reasonid"] == "8":
				bot.say("Machin a quitté TS")
			#else:
			#	bot.say("Je ne connais pas cet event")
@commands('tsstop')
def tsstop(bot, trigger):
	ts3conn.servernotifyunregister()
	tsListening = False
	bot.say("Connexion TS<->IRC arrêtée")

