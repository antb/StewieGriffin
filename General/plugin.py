###
# Copyright (c) 2011, Anthony Boot
# All rights reserved.
#
# Licenced under GPLv2
# In brief, you may edit and distribute this as you want, provided the original
# and modified sources are always available, this license notice is retained
# and the original author is given full credit.
#
# There is no warrenty or guarentee, even if explicitly stated, that this
# script is bug and malware free. It is your responsibility to check this
# script and ensure its safety.
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re,time,json,random
import supybot.ircmsgs as ircmsgs
import supybot.schedule as schedule


class General(callbacks.PluginRegexp):
	"""Some general purpose plugins."""
	threaded=True
#	All regexps
#	regexps=['capsKick','selfCorrect','userCorrect','saveLast','greeter','awayMsgKicker','ytSnarfer','pasteSnarfer']

#Remove from this array to disable any regexps
	regexps=['selfCorrect','saveLast','greeter','awayMsgKicker','ytSnarfer','pasteSnarfer']

	#Set to false to disable.
	consolechannel = "##sgoutput"
	buffer={}
	buffsize = 10
	alpha=[]
	alpha+='QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
	annoyUser=[]
	random.seed()
	random.seed(random.random())
	kickuser={}

#####################
###   Commands	###
#####################
	def banmask(self, irc, msg, args, hostmask):
		"""<nick|hostmask>

		Gets IP based hostmask for ban. """
		failed = False
		ipre = re.compile(r"[0-9]{1,3}[.-][0-9]{1,3}[.-][0-9]{1,3}[.-][0-9]")
		bm = ipre.search(hostmask)
		try:		
			bm = bm.group(0)
			bm = bm.replace(".","?")
			bm = bm.replace("-","?")
			irc.reply("*!*@*"+bm+"*")
			if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "BANMASK: *!*@*"+bm+"* returned for "+msg.nick))
		except:
			hostmask = hostmask.split("@")[1]
			count=0;
			while count<10:
				hostmask = hostmask.replace(str(count),"?")
				count+=1
			irc.reply("*!*@%s"%(hostmask),prefixNick=False)
			if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "BANMASK: *!*@%s returned for %s"%(hostmask,msg.nick)))
	banmask = wrap(banmask, ["hostmask"])

	def rand(self,irc,msg,args,min,max,num):
		"""[min] <max> [amount]

		Generates a random number from [min] to <max>, [amount] number of times."""
		random.seed()
		random.seed(random.random())

		if min > max and not num:
			num = max
			max = min
			min = 0
		elif min > max:
			min,max = max,min

		if not num:
			num = 1
		if not max:
			max = min
			min = 0

		try:
			min = int(min)
			max = int(max)
			num = int(num)
		except:
			irc.error("Non numeric value(s) given")
			return 0

		if num > 25:
			num = 25
		x = 0;
		output = ""
		while x < num:
			output+=str(int(random.randint(min,max)))+" "
			x+=1
		irc.reply(output)

	rand = wrap(rand,['int',optional('int'),optional('int')])

	def stewieQuote(self, irc, msg, args):
		data = utils.web.getUrl("http://smacie.com/randomizer/family_guy/stewie_griffin.html")
		quote = data.split('<td valign="top"><big><big><big><font face="Comic Sans MS">')[1].split('</font></big></big></big></td>')[0]
		irc.reply(quote,prefixNick=False)
#	stewie = wrap(stewieQuote)

	def geoip(self,irc,msg,args,ohostmask):
		ohostmask = ohostmask.split('@')[1]
		if msg.nick.lower() in ohostmask:
			irc.reply('Unable to locate IP - User cloak detected'%ohostmask)
			return None

		ipre = re.compile(r"[0-9]{1,3}[.-][0-9]{1,3}[.-][0-9]{1,3}[.-][0-9]")
		hostmask = ipre.search(ohostmask)
		if hostmask:
			try:		
				hostmask = hostmask.group(0)
				hostmask = hostmask.replace("-",".")
			except:
				hostmask = hostmask
		else:
			hostmask = ohostmask 

		self.log.info("GeoIP: %s",hostmask)
#		if 'gateway' in hostmask:
 #		   hostmask = hostmask.split('ip.')[1]

		data = utils.web.getUrl('http://infosniper.net/?ip_address=%s'%hostmask)
		data = data.split('<!-- ################################################################################## -->')[5]
		data = re.split('<[^<>]+>|\\n|&nbsp;|	|   |  ',data)

		x = 0
		info = []
		while x < len(data):
			if data[x] is '' or (len(data[x])<2 and ' ' in data[x]) :
				pass
			else:
				info+=[data[x]]
			x+=1

		country = info[20]
		city = info[5]
		tz = info[27]
		to = info[30]
		if '-' not in to:
			to = '+%s'%to
		lat = info[13]
		lon = info[21]
		provider = info[11]

		if 'EUKHOST LTD' in provider:
			irc.reply("Unable to locate IP - Not found")
			return None

		tinyurl=utils.web.getUrl('http://tinyurl.com/api-create.php?url=http://maps.google.com/maps?q=%s,%s'%(lat,lon))

		irc.reply('%s is near %s in %s (%s). The timezone is %s and is UTC/GMT%s. The provider is %s'%(hostmask,city,country,tinyurl,tz,to,provider))
		return None
	geoip = wrap(geoip, ['hostmask'])

	def report(self,irc,msg,args,user,reason):
		"""<User> <reason>

		Reports a user to Xenocide for him to act on when he comes back from afk or [NotHere]."""
		t = time.localtime()

		if int(t[2]) < 10: date = '0{0}'.format(t[2])
		else: date = str(t[2])

		if int(t[1]) < 10: month = '0{0}'.format(t[1])
		else: month = str(t[1])

		if int(t[3]) < 10: h = '0{0}'.format(t[3])
		else: h = str(t[3])

		logFile = '#powder.{0}-{1}-{2}.log'.format(date,month,t[0])
	#	irc.queueMsg(ircmsgs.privmsg('[NotHere]','User {0} has reported {1} for {2}. Log file is {3} and log time will be around {4}{5}'.format(msg.nick,user,reason,logFile,h,t[4])))
	#	irc.queueMsg(ircmsgs.privmsg('Xenocide','User {0} has reported {1} for {2}. Log file is {3} and log time will be around {4}{5}'.format(msg.nick,user,reason,logFile,h,t[4])))
		irc.queueMsg(ircmsgs.privmsg('Memoserv','SEND Xenocide User {0} has reported {1} in {6} for {2}. Log file is {3} and log time will be around {4}{5}'.format(msg.nick,user,reason,logFile,h,t[4],msg.args[0])))
		irc.replySuccess('Report sent.')
	report = wrap(report,['nick','text'])

	def bug(self,irc,msg,args,cmd):
		"""<plugin>

		Use this command when Stewie has a bug. It places a note in the logs and sends Xenocide a message."""
		self.log.error("****Error in {} reported by {}****".format(cmd,msg.nick))
		irc.queueMsg(ircmsgs.privmsg('Memoserv','SEND Xenocide Bug found in {} by {}.'.format(cmd,msg.nick)))
		irc.replySuccess("Bug reported.")
	bug = wrap(bug,['something'])

	def kicked(self,irc,args,channel,nick):
		"""[user]

		Shows how many times [user] has been kicked and by who. If [user] isn't provided, it returns infomation based on the caller."""
		if not nick: ref = msg.nick.lower()
		else: ref = nick.lower()

		with open('KCOUNT','r') as f:
			kickdata = json.load(f)
		
		try:
			kickdata = kickdata[ref]
			reply = "{} has been kicked {} times, ".format(nick, kickdata['total'])
			for each in kickdata:
				if each in 'total': continue
				reply='{} {} by {},'.format(reply,kickdata[each],each)
			irc.reply(reply[:-1].replace("o","\xF0"))
		except:
			irc.reply('{} hasn\'t been kicked it seems.'.format(nick))
	kicked = wrap(kicked,[optional('nick')])

	def annoy(self,irc,msg,args,channel,nick,mins):
		"""[channel] <nick> [mins]

		Makes stewie repeat everything the user says via a NOTICE for 2 minutes if [mins] is not specified. Blame Doxin for this."""

		if not mins or mins == 0: mins = 2

		expires = time.time()+(mins*60)

		try:
			def f():
				self.annoyUser.pop(self.annoyUser.index(nick.lower()))
				self.log.info('ANNOY -> No longer annoying {}'.format(nick))
			schedule.addEvent(f,expires)
		except:
			irc.error("I borked.")
			return 0

		self.log.info('ANNOY -> Annoying {} for {} minutes'.format(nick,mins))
		self.annoyUser+=[nick.lower()]
	annoy = wrap(annoy,['op','nickInChannel',optional('float')])

	def justme(self,irc,msg,args,url):
		"""<url>

		Checks if a website is up or down (using isup.me)"""
		try: url = url.split("//")[1]
		except: pass
		data = utils.web.getUrl('http://isup.me/{}'.format(url))
		if 'is up.' in data: irc.reply("It's just you.")
		elif 'looks down' in data: irc.reply("It's down.")
		else: irc.error("Check URL and try again")
	justme = wrap(justme,(['something']))

	def multikick(self,irc,msg,args,channel,nick,num,message):
		"""<nick> <num> [message]

		Kicks <nick> every time [s]he talks up to <num> (max 10) times with [message]. Use #n to insert number of remaining kicks."""
		if not channel: channel = "#powder"
		try: num = int(num)
		except:
			irc.error("Non-numeric value given.")
			return 0
		if num > 10: num = 10
		nick = nick.lower()
		self.kickuser[nick]={}
		self.kickuser[nick]['num'] = num
		if not message or message == "":
			message  = "#n kick(s) remaining."
		self.kickuser[nick]['msg'] = message

		irc.queueMsg(ircmsgs.notice(msg.nick,("Kicking anyone with {} in their nick {} times.".format(nick,num))))
	multikick = wrap(multikick, ['op',('haveOp','Kick a user'),'something','something',optional('text')])

#####################
###	RegExps	###
#####################
	def greeter(self, irc, msg, match):
		r"^(hello|hi|sup|hey|o?[bh]ai|wa+[sz]+(a+|u+)p?|Bye+|cya+|later[sz]?)[,. ]+(stewi?e?[griffin]?|bot|all|there)"
		if "," in match.group(0):
			hail = match.group(0).split(",")[0]
		elif "." in match.group(0):
			hail = match.group(0).split(".")[0]
		else:
			hail = match.group(0).split(" ")[0]
		self.log.info("Responding to %s with %s"%(msg.nick, hail))
		if(self.consolechannel): irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "GREETER: Responding to %s with %s"%(msg.nick,hail)))
		irc.reply("%s, %s"%(hail,msg.nick), prefixNick=False)
	greeter = urlSnarfer(greeter)

	def awayMsgKicker(self, irc, msg, match):
		r"(is now (set as)? away [-:] Reason |is no longer away : Gone for|is away:)"
		self.log.info("KICKING %s for away announce"%msg.nick)
		if(self.consolechannel):irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "KICK: %s for away announcement (automatic)"%msg.nick))
		self._sendMsg(irc, ircmsgs.kick(msg.args[0], msg.nick, "Autokick: Spam (Away/Back Announce)"))
	awayMsgKicker = urlSnarfer(awayMsgKicker)

	def ytSnarfer(self, irc, msg, match):
		r".+youtube[.]com.+v=[0-9A-z\-_]{11}.*"
		self.log.info("ytSnarfer - Active")
		url = match.group(0)
		url = url.split(" ")

		for x in url:
			if "youtu" in x:
				url = url[url.index(x)]

		if url.find("v=") != -1 or url.find("&") != -1:
			if url.find("v=") != -1:
				url = url.split("v=")[1]
			if url.find("&") != -1:
			   url = url.split("&")[0]
		else:
			url = url[-11:]
		
		self.log.info("ytSnarfer - Video ID: %s"%(url))

		url="http://www.youtube.com/watch?v="+url

		data = utils.web.getUrl(url)
#	data = data.split("&#x202a;")[1].split("&#x202c;")[0]
		data = data.split('<title>')[1].split('</title>')[0].split('\n')[1].strip()

		data = data.replace("&quot;","\'").replace("&#39;", "'").replace("&amp;","&")	

		irc.reply('Youtube video is "%s"'%data, prefixNick=False)
		self.log.info("ytSnarfer - Done.")
		if(self.consolechannel):irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "%s is %s"%(url,data)))
		return None
	ytSnarfer = urlSnarfer(ytSnarfer)

	def capsKick(self,irc,msg,match):
		r".+"
		data = match.group(0)
		data=data.strip('\x01ACTION').strip('\x01').strip('\x02').strip('\x07').strip('\x0f')

		knownCapsNicks = ['UBERNESS','ADL']
		for each in knownCapsNicks:
			data = data.strip(each)
		data = list(data)

		if len(data) < 15: return 0 #Simon: Increased from 5 to 15, was making quite a few people unhappy

		length=0
		caps=0
		for each in data:
			if each in self.alpha:
				length+=1
				if each in each.upper(): 
					caps+=1

		self.log.warning('{0} {1} {2}'.format(length,caps,int((float(caps)/length)*100)))

		if int((float(caps)/length)*100) > 60:
			self.log.info('Kicking {0} from {1} for caps rage.'.format(msg.nick,msg.args[0]))
			if(self.consolechannel):irc.queueMsg(ircmsgs.privmsg(self.consolechannel, "KICK: %s for excessive caps. (automatic)"%msg.nick))

			with open('KCOUNT','r') as f:
				kd = json.load(f)

			with open('KCOUNT','w') as f:
				try:	  kd[msg.nick.lower()]+=1
				except:   kd[msg.nick.lower()]=1
				f.write(json.dumps(kd,sort_keys=True,indent=4))

			reason='{0} - Kicked {1} time'.format('Excessive Caps',kd[msg.nick.lower()])
			if kd[msg.nick.lower()] > 1:
				reason = '{0}s'.format(reason)

			del kd
			irc.queueMsg(ircmsgs.kick(msg.args[0], msg.nick, reason))
	capsKick = urlSnarfer(capsKick)

	def pasteSnarfer(self,irc,msg,match):
		r"http://pastebin[.]com/[A-Za-z0-9]{8}"
		url = match.group(0)
		self.log.info('Pastbin Found - {0}'.format(url))
		page = utils.web.getUrl(url)

		paste={}
		paste['name']=page.split('<h1>')[1].split('</h1>')[0]

		page = page.split('<div class="paste_box_line2">')[1].split('</div>')[0].strip().split('|')

		try: 
			paste['by']=page[0].split('">')[1].split('</a>')[0]
		except:
			paste['by']=page[0].split(':')[1]
		paste['date']=page[1][1:-1]
		paste['syntax']=page[2].split('>')[1].split('<')[0]
		paste['size']=page[3].split(':')[1][1:-1]
		paste['expires']=page[5].split(':')[1][1:]

		if 'None' in paste['syntax']: paste['syntax']='Plain Text'

		irc.reply('Pastebin is {0} by {1} posted on {2} and is written in {3}. The paste is {4} and expires {5}'.format(paste['name'],paste['by'],paste['date'],paste['syntax'],paste['size'],paste['expires']),prefixNick=False)
	pasteSnarfer = urlSnarfer(pasteSnarfer)

	def selfCorrect(self,irc,msg,match):
		r"^s[/].*[/].*$"
		match = match.group(0)
		data = match.split('/')

		newData = []
		x=0
		while x < len(data):
			if '\\' in data[x]:
				newData+=['{0}/{1}'.format(data[x][:-1],data[x+1])]
				x+=2
			else:
				newData+=[data[x]]
				x+=1

		data=newData

		channel = msg.args[0]

		for each in self.buffer[channel]:
		   if msg.nick in each[0]:
			   output = each[1]
			   if (len(data)-1)%2 is 0:
				   x=1
				   while x < len(data):
					   output=output.replace(data[x],data[x+1])
					   x+=2

			   self.log.info('Changing {0} to {1}'.format(each[1],output))
			   irc.reply('<{0}> {1}'.format(each[0],output),prefixNick=False)
			   return 0

		irc.error('Not found in buffer')

	selfCorrect = urlSnarfer(selfCorrect)

	def userCorrect(self,irc,msg,match):
		r"^u[/].*[/].*[/].*$"
		match = match.group(0)
		data = match.split('/')
		user = data[1]

		newData = []
		x=0
		while x < len(data):
			if '\\' in data[x]:
				newData+=['{0}/{1}'.format(data[x][:-1],data[x+1])]
				x+=2
			else:
				newData+=[data[x]]
				x+=1

		data=newData

		channel = msg.args[0]

		for each in self.buffer[channel]:
		   print user.lower(),each[0].lower(),user.lower() is each[0].lower()
		   if user.lower() in each[0].lower():
			   output = each[1]
			   x=2
			   try:
				   while x < len(data):
					   output=output.replace(data[x],data[x+1])
					   x+=2
			   except: irc.error('Not enough arguments')

			   self.log.info('Changing {0} to {1}'.format(each[1],output))
			   irc.reply('<{0}> {1}'.format(each[0],output),prefixNick=False)

			   return 0

		irc.error('Not found in buffer')

	userCorrect = urlSnarfer(userCorrect)

	def saveLast(self,irc,msg,match):
		r".+"
		channel = msg.args[0]

		try: self.buffer[channel]
		except: self.buffer[channel]=[]

# Stuff for multikick
		for each in self.kickuser:
			if each in msg.nick.lower() and not self.kickuser[each]['num'] <= 0:
				irc.queueMsg(ircmsgs.ban(msg.args[0], msg.nick))
				irc.queueMsg(ircmsgs.kick(msg.args[0], msg.nick, "{}".format(self.kickuser[each]['msg'].replace('#n',str(self.kickuser[each]['num'])))))
				self.kickuser[each]['num']-=1
				def un():
					irc.queueMsg(ircmsgs.unban(msg.args[0],msg.nick))
				schedule.addEvent(un,time.time()+random.randint(30,120))
# END
		line = match.group(0).replace('\x01ACTION','*').strip('\x01')

		if msg.nick.lower() in self.annoyUser:
			def fu():
				irc.queueMsg(ircmsgs.IrcMsg('NOTICE {} :\x02\x03{},{}{}'.format(msg.nick,random.randint(0,15),random.randint(0,15),line)))
			schedule.addEvent(fu,time.time()+random.randint(2,60))

		self.buffer[channel].insert(0,[msg.nick,line])
		if len(self.buffer[channel]) > self.buffsize: self.buffer[channel].pop(self.buffsize)
		return 1
	saveLast = urlSnarfer(saveLast)

#####################
###   Utilities   ###
#####################
	def _sendMsg(self, irc, msg):
		irc.queueMsg(msg)
		irc.noReply()

Class = General


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
