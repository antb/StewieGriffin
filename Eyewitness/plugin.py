###
# Copyright (c) 2011, Anthony Boot
# All rights reserved.
#
# Licence under GPL v2
# In brief, you may edit and distribute this as you want, provided the original
# and modified sources are always available, this license notice is retained
# and the original author is given full credit.
#
# There is no warranty or guarantee, even if explicitly stated, that this
# script is bug and malware free. It is your responsibility to check this
# script and ensure its safe to run prior to execution.
# 
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import random

class Eyewitness(callbacks.Plugin):
    """Contains a basic Eyewitness game to be run on a channel."""
    threaded = False

    #Set to False to disable
    consolechannel = "##sgoutput"

    colours = ["Red","Green","Blue","Cyan","Magenta","Yellow","White","Black","Iron Maiden","Metallica","AC/DC","Rainbow","See-Thru","Justin Bieber"]
    alignment = ["sane","deluded","killer"]
    channel=""
    gameMode=0    
    #0=No Game, 1=Sign-ups, 2=Set-up, 3=sending messages, 4=day
    abort=[]
    votes={}
    roles={}
    roles['sane']=0
    roles['deluded']=0
    roles['killer']=0

    player={}
    player['joined']=[]
    player['name']=[]

    player[0]={}
    player[0]['user']=""
    player[0]['role']=""
    player[0]['colour']=""
    player[0]['voted']=[]

    player[1]={}
    player[1]['user']=""
    player[1]['role']=""
    player[1]['colour']=""
    player[1]['voted']=[]

    player[2]={}
    player[2]['user']=""
    player[2]['role']=""
    player[2]['colour']=""
    player[2]['voted']=[]

    def starteye(self,irc,msg,args,channel):
        """<no args>

        Start a game of Eyewitness for 3 players"""
        if self.gameMode is 0:
            irc.reply("A game of eyewitness for 3 players has begun, use you logic to determine the killer.", prefixNick=False)
            irc.reply("Use $joineye to join.",prefixNick=False)
            self.gameMode=1        
            self.channel=channel
        else:
            irc.reply("There is a game in progress in %s."%self.channel)
    starteye=wrap(starteye,['Channel'])

    def joineye(self,irc,msg,args,channel):
        """<no args>

        Joins a game of eye-witness or starts signups if none have started"""
        if self.gameMode is 0:
            self.starteye(irc,msg,args)
            self.joineye(irc,msg,args)

        elif self.gameMode is 1:
            if channel is not self.channel:
                irc.reply("There are signups in progress in %s."%self.channel)
            if msg.nick.lower() in self.player['joined']:
                irc.reply("You already joined.")
            else:
                self.player['joined']+=[msg.nick.lower()]
                self.player['name']+=[msg.nick]
                irc.reply("%s has joined, %i more players needed."%(msg.nick,3-len(self.player['joined'])),prefixNick=False)
                self._voice(irc, [msg.nick])

            if len(self.player['joined']) is 3:
                self.gameMode=2
                self.setup(irc,msg,args)

    joineye=wrap(joineye, ['Channel'])

    def leaveeye(self,irc,msg,args,channel):
        """<no args>

        Leaves a game of eyewitness during signups"""
        if gameMode is 0:
            irc.reply("There isn't a game in progress")
            return
        elif self.channel is channel:
            try:            
                self.player['joined'].pop(self.player.index(msg.nick.lower()))
                self.player['name'].pop(self.player.index(msg.nick.lower()))
                irc.reply("%s has left the game"%msg.nick, prefixNick=False)
                self._devoice(irc, msg.nick)
            except:
                irc.reply("Your not even in...")        
        else:
            irc.reply("Must be sent in %s."%self.channel)
    leaveye=wrap(leaveeye,['channel'])

    def setup(self,irc,msg,args):
        irc.queueMsg(ircmsgs.mode(self.channel, "+m"))
        self.player[0]['user']   = self.player['joined'][0]
        self.player[1]['user']   = self.player['joined'][1]
        self.player[2]['user']   = self.player['joined'][2]

        self.player[0]['role']   = self.alignment[random.randrange(0,len(self.alignment))]
        self.player[0]['colour'] = self.colours[random.randrange(0,len(self.colours))]
        self.player[1]['role']   = self.alignment[random.randrange(0,len(self.alignment))]
        self.player[1]['colour'] = self.colours[random.randrange(0,len(self.colours))]
        self.player[2]['role']   = self.alignment[random.randrange(0,len(self.alignment))]
        self.player[2]['colour'] = self.colours[random.randrange(0,len(self.colours))]

        while True:
            if self.player[1]['role'] is self.player[0]['role']:
                self.player[1]['role'] = self.alignment[random.randrange(0,len(self.alignment))]
            if self.player[1]['colour'] is self.player[0]['colour']:
                self.player[1]['colour'] = self.colours[random.randrange(0,len(self.colours))]

            if self.player[2]['role'] is self.player[0]['role'] or self.player[2]['role'] is self.player[1]['role']:
                self.player[2]['role'] = self.alignment[random.randrange(0,len(self.alignment))]
            if self.player[2]['colour'] is self.player[0]['colour'] or self.player[2]['colour'] is self.player[1]['colour']:
                self.player[2]['colour'] = self.colours[random.randrange(0,len(self.colours))]

            if(self.player[0]['role'] is not self.player[1]['role'] and
               self.player[0]['role'] is not self.player[2]['role'] and
               self.player[1]['role'] is not self.player[2]['role'] and
               self.player[0]['colour'] is not self.player[1]['colour'] and
               self.player[0]['colour'] is not self.player[2]['colour'] and
               self.player[1]['colour'] is not self.player[2]['colour']):
                break


        x = 0;
        while x < len(self.player['joined']):
            self.log.info(str(self.player[x]))
            if "sane" in self.player[x]['role']:
                self.roles['sane'] = x
            if "deluded" in self.player[x]['role']:
                self.roles['deluded'] = x
            if "killer" in self.player[x]['role']:
                self.roles['killer'] = x
            if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "EYEWITNESS: "+str(self.player[x])))
            x+=1
        self.log.info(str(self.roles))                

        self.gameMode=3

        sane   ="You are a witness and are wearing a %s shirt, you saw a %s shirt leaving the scene."    %(self.player[self.roles['sane']]['colour'],self.player[self.roles['killer']]['colour'])
        deluded="You are a witness and are wearing a %s shirt, you saw a %s shirt leaving the scene." %(self.player[self.roles['deluded']]['colour'],self.player[self.roles['sane']]['colour']),  
        killer ="You are the killer and are wearing a %s shirt. You didn't see anyone so you'd better hope you guess a shirt right..."%(self.player[self.roles['killer']]['colour']),

        irc.reply("%s has been killed! 3 witnesses have come forward, however, one of them is the killer, use your logic skills to find the killer!"%irc.nick,prefixNick=False)

        irc.reply(sane,private=True,to=self.player[self.roles['sane']]['user'])

        irc.reply(deluded,private=True,to=self.player[self.roles['deluded']]['user'])

        irc.reply(killer,private=True,to=self.player[self.roles['killer']]['user'])
        self.gameMode=4

    def vote(self,irc,msg,args,channel,nick):
        """<playername>

           Vote to lynch a player"""
        if channel is not self.channel:
            return
        if self.gameMode is not 4:
            return
        if nick.lower() not in self.player['joined'] and nick.lower() != "abort":
            irc.reply("%s isn't playing..."%nick)
        else:
            if msg.nick.lower() in self.abort:
                self.abort.pop(self.abort.index(msg.nick.lower()))
            if nick is "abort":
                self.abort+=[msg.nick.lower()]
                if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "EYEWITNESS: "+str(self.abort)))
                return
            x=0
            while x<3:
                if msg.nick.lower() in self.player[x]['voted']:
                    self.player[x]['voted'].pop(self.player[x].index(msg.nick.lower()))
                if nick.lower() == self.player[x]['user']:
                    self.player[x]['voted']+=[msg.nick.lower()]
                    irc.reply("%s has voted for %s..."%(msg.nick,nick),prefixNick=False)
                if len(self.player[x]['voted']) is 2:
                    self.endgame(irc,x)
                if len(self.abort) is 2:
                    self.endgame(irc,"abort")
                self.log.info(str(self.player[x]))
                x+=1;

    vote = wrap(vote,['Channel','somethingWithoutSpaces'])

    def unvote(self,irc,msg,args,channel):
        """

        Unvote a player"""
        if self.gameMode is not 4:
            irc.reply("There isn't a game running.")
        elif self.channel is not channel:
            return
        x=1
        while x<4:
            if msg.nick.lower() in player[x]['voted']:
                self.player[x]['voted'].pop(self.player[x].index(msg.nick.lower()))
    unvote = wrap(unvote)

    def endgame(self,irc,whoDied):
        if self.player[whoDied]['role'] is "abort":
            irc.reply("Game has been aborted.",prefixNick=False)
        elif self.player[whoDied]['role'] is "killer":
            irc.reply("Thats the lynch, and the game! The town wins as %s was the killer, wearing a %s shirt!"%(self.player[whoDied]['user'],self.player[whoDied]['colour']),prefixNick=False)
        else:
            irc.reply("Thats the lynch and the killer gets to kill again!", prefixNick=False)
        x=1
        self.stopGame(irc,None,None)


    def stopGame(self,irc,msg,args):
        self.gameMode=0
        x=0
        witness=" "
        while x < 3:
            if self.player[x]['role'] is not "killer":
                witness = "witness "
            else:
                witness = ""
            irc.reply("%s was the %s %swearing a %s shirt."%(self.player['name'][x],self.player[x]['role'],witness,self.player[x]['colour']), prefixNick=False)
            x+=1

        irc.queueMsg(ircmsgs.mode(self.channel, "-m"))
        self._devoice(irc, self.player['joined'])

        self.abort=[]
        self.channel=""
        self.roles={}
        self.roles['sane']=0
        self.roles['deluded']=0
        self.roles['killer']=0

        self.player={}
        self.player['joined']=[]
        self.player['name']=[]

        self.player[0]={}
        self.player[0]['user']=""
        self.player[0]['role']=""
        self.player[0]['colour']=""
        self.player[0]['voted']=[]

        self.player[1]={}
        self.player[1]['user']=""
        self.player[1]['role']=""
        self.player[1]['colour']=""
        self.player[1]['voted']=[]

        self.player[2]={}
        self.player[2]['user']=""
        self.player[2]['role']=""
        self.player[2]['colour']=""
        self.player[2]['voted']=[]

    def helpeye(self,irc,msg,args):
        irc.reply("Quite simply, there is a sane witness, a deluded witness and a killer, The sane witness sees the killer, the deluded witness sees the sane witness, the killer has to guess. Eliminate the killer.")
    helpeye = wrap(helpeye)

##Utilities
    def _sendMsgs(self, irc, nicks, f):
    #Used for setting channel mode, taken from the Channel Plugin
        numModes = irc.state.supported.get('modes', 1)
        for i in range(0, len(nicks), numModes):
            irc.queueMsg(f(nicks[i:i + numModes]))
        irc.noReply()

    def _voice(self, irc, nicks):
    #Adds voice to players
        if not nicks:
            nicks = [msg.nick]
        def f(L):
            return ircmsgs.voices(self.channel, L)
        self._sendMsgs(irc, nicks, f)

    def _devoice(self, irc, nicks):
    #Removes voice from players
        if not nicks:
            nicks = [msg.nick]
        def f(L):
            return ircmsgs.devoices(self.channel, L)
        self._sendMsgs(irc, nicks, f)

Class = Eyewitness


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
