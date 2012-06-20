###
# Copyright (c) 2010, Anthony Boot
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

import re
import simplejson as json

class VoteActions(callbacks.Plugin):
    """Keeps track of who wants what action on who."""
    threaded = True

    banvotes={}
    kickvotes={}
    kbanvotes={}

    def voteban(self,irc,msgs,args,to,reasoning):
        """<nick> <reason>

        Add you vote to ban/mute <nick>"""
        user = self._getUserID(to)
        nick = self._getNick(to)

        #self voting not allowed.
        if self._chkNick(irc,nick,msgs.nick):
            return
        self._listCheck(user)

        #Check the person hasn't already voted.
        if(msgs.nick in self.banvotes[user]["voted"]):
            irc.reply("You've already voted to kick %s"%(nick))
            return

        #Removing vote from existing list.
        self._removeVotes(msgs.nick,user)

        #Adding vote
        self.banvotes[user]["votes"]+=1
        self.banvotes[user]["voted"].append(msgs.nick)
        self.banvotes[user]["reason"].append(reasoning)
        irc.reply("%s has voted to ban/mute %s. There are now %i votes for this"%(msgs.nick,nick,self.banvotes[user]["votes"]),prefixNick=False)
        
    def votekick(self,irc,msgs,args,to,reasoning):
        """<nick> <reasoning>

        Add you vote to kick <nick>"""
        user = self._getUserID(to)
        nick = self._getNick(to)

        #self voting not allowed.
        if self._chkNick(irc,nick,msgs.nick):
            return
        self._listCheck(user)

        #Check the person hasn't already voted.
        if(msgs.nick in self.kickvotes[user]["voted"]):
            irc.reply("You've already voted to kick %s"%(nick))
            return

        #Removing vote from existing list.
        self._removeVotes(msgs.nick,user)

        #Adding vote
        self.kickvotes[user]["votes"]+=1
        self.kickvotes[user]["voted"].append(msgs.nick)
        self.kickvotes[user]["reason"].append(reasoning)
        irc.reply("%s has voted to kick %s. There are now %i votes for this"%(msgs.nick,nick,self.kickvotes[user]["votes"]),prefixNick=False)
        

    def votekban(self,irc,msgs,args,to,reasoning):
        """<nick> <reasoning>

        Add you vote to kickban <nick>"""
        if self._chkNick(irc,nick,msgs.nick):
            return
        nick = self._getNick(to)

        #self voting not allowed.
        self._chkNick(nick,msgs.nick)
        self._listCheck(user)

        #Check the person hasn't already voted.
        if(msgs.nick in self.kbanvotes[user]["voted"]):
            irc.reply("You've already voted to kban %s"%(nick))
            return

        #Removing vote from existing list.
        self._removeVotes(msgs.nick,user)

        #Adding vote
        self.kbanvotes[user]["votes"]+=1
        self.kbanvotes[user]["voted"].append(msgs.nick)
        self.kbanvotes[user]["reason"].append(reasoning)
        irc.reply("%s has voted to kickban %s. There are now %i votes for this"%(msgs.nick,nick,self.kbanvotes[user]["votes"]),prefixNick=False)
        

    def listvotes(self,irc,msgs,args,to):
        """<nick> <reasoning>

        Lists the votes <nick> has agaisnt them."""
        user = self._getUserID(to)
        nick = self._getNick(to)

        try:
            bancount = self.banvotes[user]["votes"]
            banppl = str(self.banvotes[user]["voted"])
        except:
            bancount = 0
        try:
            kickcount = self.kickvotes[user]["votes"]
            kickppl = str(self.kickvotes[user]["voted"])
        except:
            kickcount = 0
        try:
            kbancount = self.kbanvotes[user]["votes"]
            kbanppl = str(self.kbanvotes[user]["voted"])
        except:
            kbancount = 0

        if(kbancount==0 and kickcount==0 and bancount==0):
            irc.reply("%s has no votes at all."%(nick),prefixNick=False)
        else:
            irc.reply("Ban/Mute: %i %s; Kick: %i %s; KickBan: %i %s"%(bancount,banppl,kickcount,kickppl,kbancount,kbanppl), prefixNick=False)

    def unvote(self,irc,msgs,args,to):
        """<nick>

        Removes your vote for action agaisnt a user"""
        user = self._getUserID(to)
        nick = self._getNick(to)
        
        try:
            if(msgs.nick in self.banvotes[user]["voted"]):   
                removal = self.banvotes[user]["voted"].index(msgs.nick)
                self.banvotes[user]["voted"].remove(msgs.nick)
                self.banvotes[user]["votes"]-=1
                self.banvotes[user]["reason"].pop(removal)
                irc.reply("You have removed your vote to ban %s"%(nick))

            elif(msgs.nick in self.kbanvotes[user]["voted"]):
                removal = self.kbanvotes[user]["voted"].index(msgs.nick)
                self.kbanvotes[user]["voted"].remove(msgs.nick)
                self.kbanvotes[user]["votes"]-=1
                self.kbanvotes[user]["reason"].pop(removal)
                irc.reply("You have removed your vote to kickban %s"%(nick))

            elif(msgs.nick in self.kickvotes[user]["voted"]):
                removal = self.kickvotes[user]["voted"].index(msgs.nick)
                self.kickvotes[user]["voted"].remove(msgs.nick)
                self.kickvotes[user]["votes"]-=1
                self.kickvotes[user]["reason"].pop(removal)
                irc.reply("You have removed your vote to kick %s"%(nick))

            else:
                irc.reply("You weren't voting to do anything to %s."%(nick))
        except:
            
            irc.reply("%s hasnt even been voted for yet... go away."%(nick))

    def removevote(self, irc, msgs, args, voter, voted):
        """<voter> <voted>

        Removes the vote of voter from voted"""
        if not "antb" in msgs.user:
            irc.reply("Only AntB can do that")
            return
        
        user = self._getUserID(voted)
        nick = self._getNick(voted)

        self._removeVotes(voter,user)
        irc.reply("%s's vote has been removed from %s. (Even if it didn't exist)"%(voter,nick),prefixNick=False)
        

    def viewreasons(self,irc,msgs,args,to):
        """<nick>

        Returns the reasons given behind actions"""
        user = self._getUserID(to)
        nick = self._getNick(to)

        string = "Votes against %s: "%nick
        try:
            for all in self.banvotes[user]["voted"]:
                string += all+": "
                xx = self.banvotes[user]["voted"].index(all)
                string += self.banvotes[user]["reason"][xx]
                string += "; "
        except:
            string += "None to ban; "

        try:
            for all in self.kbanvotes[user]["voted"]:
                string += all+": "
                xx = self.kbanvotes[user]["voted"].index(all)
                string += self.kbanvotes[user]["reason"][xx]
                string += "; "
        except:
            string += "None to kban; "

        try:
            for all in self.kickvotes[user]["voted"]:
                string += all+": "
                xx = self.kickvotes[user]["voted"].index(all)
                string += self.kickvotes[user]["reason"][xx]
                string += "; "
        except:
            string += "None to kick; "
        irc.reply(string, prefixNick=False)


    def resetvb(self,irc,msgs,args,to):
        if ("antb" not in msgs.user):
            irc.error("Only AntB can do that :P")
            return

        user = self._getUserID(to)
        nick = self._getNick(to)

        if(nick == "StewieGriffin"):
            self.banvotes={}
            self.kickvotes={}
            self.kbanvotes={}
            irc.reply("All votes have been reset",prefixNick=False)
            return

        self.banvotes[user]={"votes":0,"voted":[],"reason":[]}
        self.kbanvotes[user]={"votes":0,"voted":[],"reason":[]}
        self.kickvotes[user]={"votes":0,"voted":[],"reason":[]}

        irc.reply("%s has had their votes reset."%(nick),prefixNick=False)

        bm = bm.replace(".","?").replace("-","?")
        irc.reply("*!*@*"+bm+"*")

    def getjson(self,irc,msgs,args,which):
        if which == "k":
            irc.reply("'"+json.dumps(self.kickvotes)+"'",prefixNick="False")
        elif which == "b":
            irc.reply("'"+json.dumps(self.banvotes)+"'",prefixNick="False")
        elif which == "kb":
            irc.reply("'"+json.dumps(self.kbanvotes)+"'",prefixNick="False")        
        else:
            irc.error("Needs either of <k|b|kb>")

#    def setjson(self,irc,msgs,args,which,votestring):
#        """<b|k|kb> <json string>

#            Restores votes"""
#        self.log.info("setjson: ")
#        self.log.info("  which="+which)
#        self.log.info("  json="+votestring)
#        if "antb" not in msgs.user:
#            irc.error("Your not allowed to do that %s..."%msgs.nick,prefixNick=False)
#            return
##        irc.reply(votestring.replace("'",""),prefixNick=False)
#        if which == "b":
#            self.banvotes = json.loads(votestring.replace("'",""))
#        elif which == "k":
#            self.kickvotes = json.loads(json.loads(votestring))
#        elif which == "kb":
#            self.kbanvotes = json.loads(json.loads(votestring))
#        else:
#            irc.reply("You didn't specify <k|b|kb>")

    def _getUserID(self,hostmask):
        return hostmask.split("!")[1].split("@")[0].replace("~","")

    def _getNick(self,hostmask):
        return hostmask.split("!")[0]

    def _chkNick(self,irc,voted,voter):
        if(voted == voter):
            irc.reply("%s has voted for %s, but as that peron is trying to vote for themselves it doesnt count."%(voter,voted,voter), prefixNick=False)
            return 1
        elif(voted == "StewieGriffin"):
            irc.reply("StewieGriffin has voted to kick %s, there are now over NINE THOUSAAAAAAAAAAAND votes for this."%voter, prefixNick=False)
            return 1
        else:
            return 0

    def _listCheck(self,user):
        if(user not in self.kbanvotes):
            self.kbanvotes[user]={"votes":0,"voted":[],"reason":[]}
            self.banvotes[user]={"votes":0,"voted":[],"reason":[]}
            self.kickvotes[user]={"votes":0,"voted":[],"reason":[]}

    def _removeVotes(self,voter,voted):
        if(voter in self.kbanvotes[voted]["voted"]):
            removal = self.kbanvotes[voted]["voted"].index(voter)
            self.kbanvotes[voted]["voted"].remove(voter)
            self.kbanvotes[voted]["votes"]-=1
            self.kbanvotes[voted]["reason"].pop(removal)

        if(voter in self.kickvotes[voted]["voted"]):
            removal = self.kickvotes[voted]["voted"].index(voter)
            self.kickvotes[voted]["voted"].remove(voter)
            self.kickvotes[voted]["votes"]-=1
            self.kickvotes[voted]["reason"].pop(removal)

        if(voter in self.banvotes[voted]["voted"]):
            removal = self.banvotes[voted]["voted"].index(voter)
            self.banvotes[voted]["voted"].remove(voter)
            self.banvotes[voted]["votes"]-=1
            self.banvotes[voted]["reason"].pop(removal)

    voteban = wrap(voteban, ["hostmask",rest("something")])
    votekick = wrap(votekick, ["hostmask",rest("something")])
    votekban = wrap(votekban, ["hostmask",rest("something")])
    listvotes = wrap(listvotes, ["hostmask"])
    unvote = wrap(unvote,["hostmask"])
    resetvb = wrap (resetvb, ["hostmask"])
    viewreasons = wrap(viewreasons, ["hostmask"])
    removevote = wrap(removevote, ["something","hostmask"])
    getjson = wrap(getjson, ["something"])
#    setjson = wrap(setjson, ["somethingWithoutSpaces",rest("anything")])

Class = VoteActions

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
