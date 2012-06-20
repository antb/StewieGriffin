###
# Copyright (c) 2011, Anthony Boot
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class QuickMessage(callbacks.Plugin):
	"""Add the help for "@plugin help QuickMessage" here
	This should describe *how* to use this plugin."""

	threaded = True
	regexps = ['catchNote','showNote']

	def _saveFile(self,irc):
		try:
			with open("MSGS","w") as f:
				f.write(json.dumps(self.notes,indent=8,sort_keys=true))
		except Exception, e:
			irc.error("Error occured. {}".format(e))

	def _loadFile(self):
		try:
			with open("MSGS","r") as f:
				self.notes=json.load(f)
		except Exception, e:
			irc.error("Error occured. {}".format(e))
			self.notes={}

	def tell (self,irc,msg,args,nick,mesg):
		self.catchNote(irc,msg,args,"{} {}".format(nick,mesg))

	def catchNote(self,irc,msg,args,match):
		r"^[Ss]tew[ie]{2}?[,]? tell .*"
		try:	all = match.group(0)
		except:	all = str(match)

		sendTo = all.split("tell")[1].split(" ")[0].lower()
		message = all.split("tell")[1].split(" ")[1:]

		x=0
		try:	self.notes
		except: self._loadFile()
		try:	self.notes[sendTo]
		except: self.notes[sendTo]={}
	
		while True:
			try:
				self.notes[sendTo][x]
			except:
				self.notes[sendTo][x]={"from":" ", "msg":" "}
				break
		self.notes[sendTo][x]["from"]=msg.nick
		self.notes[sendTo][x]["msg"]=message
		self._saveFile()
		self.log.info("QUICKMESSAGE\n\tTo: {}\n\tFrom:\n\t:Message:{}".format(sendTo,msg.nick,message))
		irc.replySucess()
	catchNote = urlSnarfer(catchNote)

	def showNote(self,irc,msg,args,match):
		r"."
		try:
			self.notes[msg.nick]
		except:
			return 0

		self.log.info("QUICKMESSAGE - Sending messages to {}".format(msg.nick))
		for each in self.notes[msg.nick]:
#			irc.reply("{} says \"{}\"".format(self.notes[each]["from"],self.notes[each]["msg"]))
			irc.reply("{} says \"{}\"".format(each["from"],each["msg"]))
#			self.log.info("\tFrom: {}\n\tMessage: {}".format(self.notes[each]["from"],self.notes[each]["msg"]))
			self.log.info("\tFrom: {}\n\tMessage: {}".format(each["from"],each["msg"]))
			del self.notes[msg.nick][each]
		return 1
	showNote = urlSnarfer(showNote)
		

Class = QuickMessage


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
