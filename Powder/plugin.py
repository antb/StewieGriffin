###
# Copyright (c) 2011, AntB
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

import supybot.ircmsgs as ircmsgs
import json,random,urllib

class Powder(callbacks.PluginRegexp):
    """Contains all sorts of random stuff."""
    threaded = True
    regexps = ['powderSnarfer','forumSnarfer']
    consolechannel = "##sgoutput"
    
    def git(self, irc, msg, args, user, project, branch):
        """<username> [project] [branch]

        Returns information about a user GitHub Repo. Project and Branch arguments are optional. Defaults to the-powder-toy/master if no other arguments are given."""

        if(not(branch)):
            branch="master";
        if(not(project)):
            project="the-powder-toy"
        user=user.lower()
        branch=branch.lower()
        if(user=="simon" or user=="isimon" or user=="ximon"):
            user="facialturd"
        if user=="doxin":
            user="dikzak"

        giturl = "http://github.com/api/v2/json/commits/show/%s/%s/%s"%(user,project,branch)
        try:
            data = json.loads(utils.web.getUrl(giturl))
        except:
            try:
                branch = project
                project = "the-powder-toy"
                giturl = "http://github.com/api/v2/json/commits/show/%s/%s/%s"%(user,project,branch)
                data = json.loads(utils.web.getUrl(giturl))
            except:
                irc.error("HTTP 404. Please check and try again.", prefixNick=False)
                if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "GIT: Returned 404 on %s:%s"%(user,branch)))
                return
        data = data["commit"]

        data["committed_date"] = data["committed_date"].split("T")
        data["message"] = data["message"].replace("\n"," ") 
        data["message"] = data["message"].replace("\t"," ")

        if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "GIT: user:%s project:%s branch:%s called by %s sucessfully."%(user,project,branch,msg.nick)))
        irc.reply("Last commit to %s's %s repo, %s branch, was by %s on %s at %s. Commit message was \"%s\" - https://github.com/%s/%s/tree/%s"%(user,project,branch,data["committer"]["name"],data["committed_date"][0],data["committed_date"][1],data["message"],user,project,branch), prefixNick=False)


    git = wrap(git,['somethingWithoutSpaces',optional('somethingWithoutSpaces'),optional('somethingwithoutspaces')])

    def dl(self, irc, msg, args, ver, sse):
        """<win|lin|sdl|bz2> <sse|sse2|sse3>

            Provides download links for AntB's Mod"""

        if(ver=="sdl" or ver=="bz2"):
            irc.reply("http://tinyurl.com/"+ver+"dll")

        if(not(sse)):
            sse="2"
        if(sse=="sse"):
            sse=" "

        if(ver=="win"):
            irc.reply("http://tinyurl.com/ab-powder"+sse[-1])

        if(ver=="lin"):
            irc.reply("http://tinyurl.com/ab-tpt-lin"+sse[-1])
#    dl = wrap(dl,['somethingWithoutSpaces',optional('somethingWithoutSpaces')])

    def browse(self, irc, msg, args, ID, blurb):
        """<SaveID|URL>

            Returns information about a save."""
        self._getSaveInfo(irc, ID, 0)
    browse = wrap(browse,['somethingWithoutSpaces',optional('text')])

    def powderSnarfer(self, irc, msg, match):
        r"http://powdertoy.co.uk/Browse/View.html\?ID=[0-9]+|^[~][0-9]+"
        self.log.info("powderSnarfer - URL Found")
        self._getSaveInfo(irc, match.group(0), 1)
    powderSnarfer = urlSnarfer(powderSnarfer)

    def _getSaveInfo(self, irc, ID, urlGiven):
        if ID[0]=="h" or ID[0]=="p":
            ID = (ID.split("="))[1]
        elif ID[0]=="~":
	    ID=ID[1:]
            urlGiven=False

        data = json.loads(utils.web.getUrl("http://powdertoy.co.uk/Browse/View.json?ID="+ID))
        if(data["Username"]=="FourOhFour"):
            saveMsg = "Save "+ID+" doesn't exist."
        else:
            saveMsg = "Save "+ID+" is "+data["Name"].replace('&#039;','\'').replace('&gt;','>')+" by "+data["Username"]+". Score: "+str(data["Score"])+"."
            if(not urlGiven):
                saveMsg+=" http://powdertoy.co.uk/Browse/View.html?ID="+ID
        irc.reply(saveMsg,prefixNick=False)
        if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "SAVE: %s"%saveMsg))

    def frontpage(self,irc,msg,args):
		"""

		Returns the front page of saves via notices - abuse will not be tolerated."""
		data = json.loads(utils.web.getUrl('http://powdertoy.co.uk/Browse.json'))['Saves']

		outMsg = ''
		x=0
		for each in data:
			outMsg='{0}\x02Save:\x02 {1:<24} - \x02By:\x02 {2:<14} - \x02ID: \x02{3:<6} - \x02Votes:\x02 {4:<4}'.format(outMsg,each['Name'].replace('&#039;','\''),each['Username'],str(each['ID']),str(each['Score']))
			x+=1
			if x%2 is 0:
				irc.queueMsg(ircmsgs.privmsg(msg.nick,outMsg))
				outMsg=''
							continue
					outMsg='{0} -- '.format(outMsg)

	#	irc.queueMsg(ircmsgs.privmsg(msg.nick,outMsg))
    frontpage = wrap(frontpage)

    def forumSnarfer(self,irc,msg,match):
        r"http://powdertoy[.]co[.]uk/Discussions/Thread/View[.]html[?]Thread=[0-9]+"
        threadNum = match.group(0).split("Thread=")
        self.log.info("Forum thread found.")

        data = json.loads(utils.web.getUrl("http://powdertoy.co.uk/Discussions/Thread/View.json?Thread=%s"%(threadNum[1])))
        cg = data["Info"]["Category"]
        tp = data["Info"]["Topic"]

        irc.reply("Forum post is \"%s\" in the %s section, posted by %s and has %s replies. Last post was by %s at %s"%
                (tp["Title"],cg["Name"],tp["Author"],tp["PostCount"]-1,tp["LastPoster"],tp["Date"]),prefixNick=False)
        if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "FORUMSNARF: Thread %s found. %s in the %s section"%(threadNum[1],tp["Title"],cg["Name"])))
    forumSnarfer = urlSnarfer(forumSnarfer)


    def profile(self, irc, msg, args, user):
        """<username|ID>

          returns a link to the users profile and some brief information"""

        try:
            userPage = utils.web.getUrl("http://powdertoy.co.uk/User.html?Name="+user)
            userID = userPage.split("<a href=\"/User.html?ID=")[1].split("\"")[0];
            userData = json.loads(utils.web.getUrl("http://powdertoy.co.uk/User.json?Name="+user))
            uDu = userData['User']
            irc.reply('http://powdertoy.co.uk/User.html?Name={0} | {0} (ID {1}) | Has {2} saves - Average score {3} - Highest score {4} | Posted {5} topics -  {6} posts - Has {7} reputation.'.format(user,userID,uDu['Saves']['Count'],uDu['Saves']['AverageScore'],uDu['Saves']['HighestScore'],uDu['Forum']['Topics'],uDu['Forum']['Replies'],uDu['Forum']['Reputation']), prefixNick=False)

        except Exception, e:
            try:
              	userPage = utils.web.getUrl("http://powdertoy.co.uk/User.html?ID="+user)
                userName = userPage.split("<h1 class=\"SubmenuTitle\">")[1].split("</h1>")[0]
                userData = json.loads(utils.web.getUrl("http://powdertoy.co.uk/User.json?ID="+user))
                uDu = userData['User']
                irc.reply('http://powdertoy.co.uk/User.html?ID={0} | {1} (ID {0}) | Has {2} saves - Average score {3} - Highest score {4} | Posted {5} topics -  {6} posts - Has {7} reputation.'.format(user,userName,uDu['Saves']['Count'],uDu['Saves']['AverageScore'],uDu['Saves']['HighestScore'],uDu['Forum']['Topics'],uDu['Forum']['Replies'],uDu['Forum']['Reputation']), prefixNick=False)

            except Exception, e:
                irc.reply("User or ID doesn't exist - or Xeno screwed it again... {}".format(e))
                
        finally:
            return None

    profile = wrap(profile,['something'])


    def network(self, irc, msg, args):
        irc.reply("https://github.com/facialturd/The-Powder-Toy/network");
    network = wrap(network)

    def randomsave(self,irc,msg,args):
        """

        Returns a random save from powdertoy.co.uk"""
        random.seed()
        random.seed(random.random())
        found = False
        while found is False:
            saveID = str(int(random.random()*250000))
            page = json.loads(utils.web.getUrl("http://powdertoy.co.uk/Browse/View.json?ID="+saveID))
            if(page["Username"]!="FourOhFour"):
                found = True

        self._getSaveInfo(irc,saveID,0) 
    randomsave = wrap(randomsave)


Class = Powder

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
