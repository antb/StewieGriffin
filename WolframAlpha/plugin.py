###
# Copyright (c) 2011, Michael Ziegler
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from urllib import quote, urlopen
from xml.dom import minidom

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class WolframAlpha(callbacks.Plugin):
    """Add the help for "@plugin help WolframAlpha" here
    This should describe *how* to use this plugin."""
    threaded = True

    def wolf( self, irc, msg, args, keywords ):
        apikey = self.registryValue('apikey')
#	apikey = "A54874-G7Y9A8X6RJ"
        dom = minidom.parse(urlopen("http://api.wolframalpha.com/v2/query?input={}&appid={}".format(
            keywords.replace("+","%2B"), apikey
            )))

        if dom.childNodes[0].getAttribute("success") != "true":
            for error in dom.childNodes[0].getElementsByTagName("error"):
                for msg in error.getElementsByTagName("msg"):
                    for value in msg.childNodes:
                        irc.error( value.nodeValue.encode("utf-8") )
            return

        res = {}
        prim = None

        for pod in dom.childNodes[0].getElementsByTagName("pod"):
            for subpod in pod.getElementsByTagName("subpod"):
                if subpod.getAttribute("primary") == "true":
                    prim = pod.getAttribute("id")
                for plaintext in subpod.getElementsByTagName("plaintext"):
                    for value in plaintext.childNodes:
                        res[ pod.getAttribute("id") ] = value.nodeValue

        for key in res:
		try:
			message="{} -- {}:{}".format(message,key.encode("UTF-8").replace("\n"," "),res[key].encode("UTF-8").replace("\n"," "))
		except:
			message="{}:{}".format(key.encode("UTF-8"),res[key].encode("UTF-8"))
#            irc.reply( key.encode("UTF-8") + ": " + res[key].encode("utf-8") )
	irc.reply(message)

    wolf = wrap( wolf, ["text"] )




Class = WolframAlpha


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
# kate: space-indent on; indent-width 4; replace-tabs on;
