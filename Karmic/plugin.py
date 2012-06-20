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
import json,os,time

class Karmic(callbacks.PluginRegexp):
    """JSON based karma"""
    threaded = True
    regexps=['alterKarma']

    powderOps=['facialturd','simon','ximon','xenocide','cracker64','catelite','devast8a','stewiegriffin','doxin','triclops200','frankbro','ief015']

    def userInChannel(self, irc, user, channel):
        self.log.info('Finding {0} in {1}'.format(user, channel))
        tuser = ircutils.IrcString(user)
        for cuser in irc.state.channels[channel].users():
            self.log.info('{0}:{1}'.format(user, cuser))
            if tuser == cuser:
                return 1
        return 0

    def alterKarma(self,irc,msg,match):
        r"^[A-Za-z0-9+-.?!]*([+]{2}|[-]{2})$"
	#Preemptive double check
        try: self.karmaCount
        except: self._loadKarma()

        if msg.nick.lower() not in self.powderOps and msg.nick.lower() not in self.karmaCount['g']:
             irc.error('You don\'t have any yarn to give (You don\'t have permission)')
             return 0

        match = match.group(0)
        item = str(match[:-2])
        upOrDown = match[-1]
        self.log.info('Karma -> {0} by {1}'.format(match, msg.nick))

#        if item.lower() in msg.nick.lower():
#            irc.error('No self karma allowed.')
#            return 0

        if item.lower() in 'rap':
            upOrDown='-'

#        elif upOrDown is '-':
#            if ('powdertoy' in item.lower() or 'powder-toy' in item.lower()) or item.lower() in self.powderOps:
#                item=msg.nick

#        try:
#            if (time.time()-self.karmaCount['t'][msg.nick.lower()])<300 and 'xeno' not in msg.nick.lower():
#                irc.error('You need to wait 1 minute from your last karmic action before you can use it again.')
#                irc.error('You need to wait 5 minutes to give more yarn.')
#                return 0
#        except: pass

#        print self.karmaCount

        if upOrDown in '+':
            try:    self.karmaCount['k'][item.lower()]+=1
            except: self.karmaCount['k'][item.lower()]=1

        elif upOrDown in '-':
            try:    self.karmaCount['k'][item.lower()]-=1
            except: self.karmaCount['k'][item.lower()]=-1

#	self.karmaCount['t'][msg.nick.lower()]=time.time()

#        irc.reply('Karma for {0} is {1}.'.format(item,self.karmaCount['k'][item.lower()]),prefixNick=False)
#        if item.lower() in 'kitty':
 #           irc.reply('Kitty already has all the yarn =^.^=')
        if item.lower() in 'doxin':
            irc.reply('Doxin already has all the yarn =^.^=')
        else:
            irc.reply('{0} now has {1} ball(s) of yarn.'.format(item,self.karmaCount['k'][item.lower()]),prefixNick=False)
        self._saveKarma()
    alterKarma = urlSnarfer(alterKarma)

    def karma(self,irc,msg,args,item):
        """<item>

        Displays the current karmic value of \x02<item>\x02"""

	if not item: item=msg.nick

        try:    self.karmaCount
        except: self._loadKarma()

        try:    karmic = self.karmaCount['k'][item.lower()]
        except: karmic = 0
 
#        irc.reply('Karma for {0} is {1}.'.format(item,karmic))
#        if item.lower() in 'kitty':
#            irc.reply('Kitty has ALL the yarn =^.^=')
        if item.lower() in 'doxin':
            irc.reply('Doxin has ALL the yarn =^.^=')
        else:
            irc.reply('{0} has {1} ball(s) of yarn.'.format(item,karmic))
    karma = wrap(karma, [optional('text')])

    def rekarma(self,irc,msg,args):
	"""

	ohai mniip!"""
	self._loadKarma()
	irc.replySuccess()
    rekarma = wrap(rekarma)


    def giveKarma(self,irc,msg,args,nick):#,isOp):
	"""<user>

	Gives a user the ability to give and take karma"""
	try: self.karmaCount
	except: self._loadKarma()

	if nick.lower() in self.karmaCount['g']:
		irc.error('User already added')

	else:
		self.karmaCount['g']+=[nick.lower()]
		self._saveKarma()
		irc.replySuccess()
    mkkarma = wrap(giveKarma,['nickInChannel','op'])

    def takeKarma(self,irc,msg,args,nick):#,isOp):
	"""<user>

	Removes the ability for user to give and take karma"""
	try: self.karmaCount
	except: self._loadKarma()

	if nick.lower() not in self.karmaCount['g']:
		irc.error('User doesn\'t have that power.')
	else:
		self.karmaCount['g'].pop(self.karmaCount['g'].index(nick.lower()))
		self._saveKarma()
		irc.replySuccess()
    rmkarma = wrap(takeKarma,['nickInChannel','op'])

    def _loadKarma(self):
        try:
            with open('KARMA','r') as f:
                self.karmaCount = json.load(f)
        except:
#            os.execute('mv KARMA KARMA.old')
            self.karmaCount={'t':{},'k':{},'g':[]}
            with open('KARMA','w') as f:
                json.dump(self.karmaCount,f)


    def _saveKarma(self):
        with open('KARMA','w') as f:
	        f.write(json.dumps(self.karmaCount,sort_keys=True,indent=4))


Class = Karmic


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
