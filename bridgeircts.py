import sopel.module
import ts3


with ts3.query.TS3Connection("localhost") as ts3conn:
	try:
		ts3conn.login(
			client_login_name="gipsy",
			client_login_password="XXXXX"
		)
	except ts3.query.TS3QueryError as err:
		print("Login failes:", err.resp.error["msg"])
		exit(1)

	print("Login OK")
	ts3conn.use(sid=1)
	print("Selection server OK")

from sopel.module import commands
@commands('tslist')
def tslist(ts3conn, bot, trigger):
	resp=ts3conn.clientlist()
	for client in resp.parsed:
		bot.msg(client)
