#!/usr/bin/python3

import ts3

# The examples package already contains this implementation.
# Note, that the ts3.examples.viewer module has an helpful class to
# build a complete channel tree of a virtual server: ChannelTreeNode
from ts3.examples.viewer import view

with ts3.query.TS3Connection("barakuun.com") as ts3conn:
        ts3conn.login(
                client_login_name="serveradmin",
                client_login_password="wakuun42!"
        )
        view(ts3conn, sid=1)
