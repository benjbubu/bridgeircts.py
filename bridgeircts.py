import sopel.module
import ts3
#import ts3.definitions
import time
import random

from sopel.module import commands

@commands('tslist')
def tslist(bot,trigger):
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
				client_login_password="wakuun42!"
			)
		except ts3.query.TS3QueryError as err:
			bot.say("Login failed: "+ err.resp.error["msg"])
			exit(1)

		ts3conn.use(sid=1)
		
		# on récupère le message
		if not trigger.group(2):
			bot.reply("Et ton message boulet ?")
		else:
			message = "<IRC " + trigger.nick + "> " + trigger.group(2)
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
	
			# tri des events avec ajout de condition szupplémentaire dans le IF pour éviter que les serverquery apparaissent soit en join.quit soit en message (ex : message tstalk arrivant dans le chat Teamspeak est considéré comme un event et donc le bot tente de le dire aussi sur IRC
			if 'targetmode' in event[0] and event[0]["invokerid"] != '0':
				# invokerid= 0 --> Server
				# Du texte a été prononcé sur TS
				bot.say("<TS " + event[0]["invokername"] + "> " + event[0]["msg"])
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
						if event[0]['clid'] in clidpseudo:
							# le pseudo est enregistré
							bot.say(clidpseudo[event[0]["clid"]] + " a quitté Teamspeak")
							del clidpseudo[event[0]["clid"]]
						else:
							# le pseudo n'est pas enregistré
							bot.say("Ta grandmère a quitté Teamspeak")


@commands('tsstop')
def tsstop(bot, trigger):
	global tsListening

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

		ts3conn.servernotifyunregister()

		tsListening = False
		bot.say("Connexion TS<->IRC arrêtée")


@commands('tswhirl')
def tswhirl(bot, trigger, duration=5, relax_time=0.2):
	"""
	Moves all clients randomly in other channels for *duration* seconds.
	After the whirpool event, all clients will be in the same channel as
	before. Between the whirlpool cycles, the programm will sleep for
	*relax_time* seconds.
	"""
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

		# Countdown till whirlpool
		for i in range(3, 0, -1):
			ts3conn.gm(msg="Il arrive dans {}s".format(i))
			time.sleep(1)
		# AVERTISSEMENT FINAL
		ts3conn.gm(msg="AND HIS NAME IS")
		time.sleep(2)
		ts3conn.gm(msg="JOHN CENAAAAAA")
		time.sleep(2)

		# Fetch the clientlist and the channellist.
		clientlist = ts3conn.clientlist()
		channellist = ts3conn.channellist()

		# Ignore query clients
		clientlist = [client for client in clientlist \
			  if client["client_type"] != "1"]

		# Whirpool with one channel or no users is boring.
		if len(channellist) == 1 or not clientlist:
			return None

		# We need this try-final construct to make sure, that all
		# clients will be in the same channel at the end of the
		# whirlpool as to the beginning.
		try:
			end_time = time.time() + duration
			while end_time > time.time():
				for client in clientlist:
					clid = client["clid"]
					cid = random.choice(channellist)["cid"]
					try:
						ts3conn.clientmove(clid=clid, cid=cid)
					except ts3.query.TS3QueryError as err:
						# Only ignore 'already member of channel error'
						if err.resp.error["id"] != "770":
							raise
				time.sleep(relax_time)
		finally:
		# Move all clients back
			for client in clientlist:
				try:
					ts3conn.clientmove(clid=client["clid"], cid=client["cid"])
				except ts3.query.TS3QueryError as err:
					if err.resp.error["id"] != "770":
						raise



@commands('THUNDER')
def THUNDER(bot, trigger):
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


		# Fetch the clientlist and the channellist.
		clientlist = ts3conn.clientlist()

		# Ignore query clients
		clientlist = [client for client in clientlist \
			  if client["client_type"] != "1"]

		# On choisit un client au hasard :)
		clid = random.choice(clientlist)["clid"]
			
		#Greyskull Power
		ts3conn.clientpoke(msg="PAR LE POUVOIR DU CRANE ANCESTRAL BITCH", clid=clid)		
		ts3conn.clientkick(reasonid=5, reasonmsg="PAR LE POUVOIR DU CRANE ANCESTRAL BITCH", clid=clid)
