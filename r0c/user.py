# -*- coding: utf-8 -*-
from __future__ import print_function
if __name__ == '__main__':
	raise RuntimeError('\r\n{0}\r\n\r\n  this file is part of retr0chat.\r\n  enter the parent folder of this file and run:\r\n\r\n    python -m r0c <telnetPort> <netcatPort>\r\n\r\n{0}'.format('*'*72))

from .util import *

PY2 = (sys.version_info[0] == 2)



class User(object):
	def __init__(self, world, address):
		self.world = world
		self.client = None           # the client which this object belongs to
		self.chans = []              # UChannel instances
		self.active_chan = None      # UChannel
		self.new_active_chan = None  # set for channel change
		self.nick = None             # str
		self.nick_re = None          # regex object for ping assert
		
		plain_base = u'lammo/{0}'.format(address[0])

		for sep in u'/!@#$%^&*()_+-=[]{};:<>,.':

			plain = plain_base
			while True:
				#print(plain)
				nv = hashlib.sha256(plain.encode('utf-8')).digest()
				if PY2:
					nv = int(nv.encode('hex'), 16)
				else:
					nv = int.from_bytes(nv, 'big')
				#nv = base64.b64encode(nv).decode('utf-8')
				nv = b35enc(nv)
				nv = nv.replace('+','').replace('/','')[:6]

				ok = True
				for user in self.world.users:
					if user.nick == nv:
						ok = False
						break

				if ok:
					self.set_nick(nv)
					break
				else:
					if len(plain) > 100:
						break
					plain += '/{0}'.format(address[1])

			if self.nick:
				break
		
		if not self.nick:
			raise RuntimeError("out of legit nicknames")

	def post_init(self, client):
		self.client = client

	def create_channels(self):
		# while true; do tail -n +3 ansi | iconv -t 'cp437//IGNORE' | iconv -f cp437 | while IFS= read -r x; do printf "$x\n"; done | sed -r "s/$/$(printf '\033[K')/"; printf '\033[J'; sleep 0.2; printf '\033[H'; done
		
		if self.client.codec in ['utf-8','cp437','shift_jis']:
			
			# the simple version
			text = u"""\
`1;30m________ ___ ________
`1;30m░▒▓█▀▀▀▀`37m █▀█ `30m▀▀▀▀█▓▒░   `0;36m┌──[`0mretr0chat 0.9`36m]──┐
`1;30m ░▒▓`36m █▀█ █ █ █▀▀ `30m▓▒░    `0;36m│`0mgithub.com/9001/r0c`36m│
`1;30m  ░▒`34m █   █▄█ █▄▄ `30m▒░     `0;36m╘═══════════════════╛
                             `34m  b. build_date `0m
"""
			# the messy version
			text = u"""\
`1;30m________ `37m__`36m_ `30m________
`1;30m░▒▓█▀▀▀▀`37m █▀`46m▓`0;1;30m ▀▀▀▀█▓▒░   `0;36m┌──[`0mretr0chat 0.9`36m]──┐
`1;30m ░▒▓ `34;46m▒`0;1;36m▀█ `37;46m▓`0m `1;37;46m▓`0m `1;36m█▀`34m▀ `30m▓▒░    `0;36m│`0mgithub.com/9001/r0c`36m│
`1;30m  ░▒ `34m█   `36m█▄█ `34;46m▒`0;1;34m▄▄ `30m▒░     `0;36m╘═══════════════════╛
                             `34m  b. build_date `0m
"""
			
		else:
			# the simple version
			text = u"""
  `1;37m     /^\\           `0mretr0chat 0.9 `36m-----
  `1;36m/^^  | |  /^^      `0mgithub.com/9001/r0c
  `1;34m|    \\_/  \\__      `0;36m------b. build_date `0m
"""

			# the messy version
			text = u"""`1;30m______    `37m_`30m    ______
`1;30m\\\\\\\\\\\\\\  `37m/ \\  `30m///////   `0mretr0chat 0.9 `36m-----
 `1;30m\\\\ `36m/`37m^^  | |  `36m/^`0;36m^`1;30m //    `0mgithub.com/9001/r0c
  `1;30m\\ `0;36m|    `1m\\_/  `0;36m\\__ `1;30m/     `0;36m------b. build_date `0m
"""

		text = text.replace(u'`', u'\033[').replace('build_date', '2018-01-10')

		text += u"""
Useful commands:
   \033[36m/nick\033[0m  change your nickname
   \033[36m/help\033[0m  full commands listing

Text formatting:
  \033[36mCTRL-O\033[0m  reset text formatting
  \033[36mCTRL-B\033[0m  bold/bright text on/off
  \033[36mCTRL-K\033[0m  followed by a colour code:
       \033[36m2\033[0m  \033[32mgreen\033[0m,
    \033[36m15,4\033[0m  \033[1;37;44mbold white on blue\033[0m --
          say \033[1m/cmap\033[0m to see all options

Switching channels:
  \033[36mCTRL-A\033[0m  jump to previous channel
  \033[36mCTRL-X\033[0m  jump to next channel
  \033[36m/3\033[0m      go to channel 3
  \033[36m/0\033[0m      go to this channel

Creating or joining the "general" chatroom:
  \033[36m/join #general\033[0m

Leaving a chatroom:
  \033[36m/part\033[0m

Changing your nickname:
  \033[36m/nick new_name\033[0m

Keybinds:
  \033[36mUp\033[0m / \033[36mDown\033[0m       input history
  \033[36mLeft\033[0m / \033[36mRight\033[0m    input field traversing
  \033[36mHome\033[0m / \033[36mEnd\033[0m      input field jump
  \033[36mPgUp\033[0m / \033[36mPgDown\033[0m   chatlog scrolling... \033[1mtry it :-)\033[0m

if you are using a mac, PgUp is fn-Shift-PgUp

"""

# cp437 box æøå
#\xc9\xcd\xcd\xcd\xcd\xcd\xbb
#\xba \x91\x94\x86 \xba
#\xc8\xcd\xcd\xcd\xcd\xcd\xbc

#  >> if your terminal is blocking the CTRL key,
#  >> press ESC followed by the 2nd key instead

# æ     ø     å
# c3 a6 c3 b8 c3 a5 utf-8 to putty, works
# c3 a6 c3 b8 c3 a5 utf-8 from putty, fucked

		if False:
			lipsum1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
			lipsum2 = "Lorem ipsum dolor sit amet, \033[1;31mconsectetur\033[0m adipiscing elit, sed do eiusmod tempor incididunt ut \033[1;32mlabore et dolore magna\033[0m aliqua. Ut enim ad minim veniam, quis nostrud \033[1;33mexercitation ullamco laboris nisi ut aliquip ex ea\033[0m commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est labo\033[1;35mrum."
			for n in range(10):
				text += lipsum1 + "\n"
				text += lipsum2 + "\n"

		uchan = self.world.join_priv_chan(self, 'r0c-status')
		nchan = uchan.nchan
		nchan.topic = 'r0c readme (and status info)'

		msg = Message('-nfo-', nchan, time.time(), text)
		nchan.msgs.append(msg)

		self.new_active_chan = uchan
		


		if False:
			uchan = self.world.join_pub_chan(self, 'general')
			nchan = uchan.nchan
			if len(nchan.msgs) < 100:
				for n in range(1,200):
					#txt = u'{0:03}_{1} EOL'.format(
					#	n, u'_dsfarg, {0:03}_'.format(n).join(
					#		str(v).rjust(3, '0') for v in range(1, min(48, n))))
					txt = u'{1}_{0:03}     \\\\\\\\'.format(n,
						u'_{0:03}     \\\\\\\\\n'.format(n).join(
							str(v).rjust(v+4, ' ') for v in range(0, 12)))
					self.world.send_chan_msg(self.nick, nchan, txt)

		if False:
			uchan = self.world.join_pub_chan(self, 'smalltalk')
			nchan = uchan.nchan
			for n in range(1,3):
				txt = u'  message {0}\n      mes {0}'.format(n)
				self.world.send_chan_msg(self.nick, nchan, txt)

		self.client.handshake_world = True



	def exec_cmd(self, cmd_str):
		inf = self.world.get_priv_chan(self, 'r0c-status').nchan
		cmd = cmd_str # the command keyword
		arg = None    # single argument with spaces
		arg1 = None   # 1st of 2 arguments
		arg2 = None   # 2nd of 2 arguments
		
		ofs = cmd.find(' ')
		if ofs > 0:
			cmd = cmd_str[:ofs]
			arg = cmd_str[ofs+1:]
		cmd = cmd.lower()

		if arg:
			ofs = arg.find(' ')
			if ofs > 0:
				arg1 = arg[:ofs].lower()
				arg2 = arg[ofs+1:]

		if cmd == 'me':
			self.world.send_chan_msg('***', self.active_chan.nchan,
				'\033[1m{0}\033[22m {1}'.format(self.nick, arg))

		elif cmd == 'nick' or cmd == 'n':
			if not arg:
				self.world.send_chan_msg('-err-', inf, """[invalid argument]
  usage:     /nick  new_nickname
  example:   /nick  spartacus
""")
				return

			if arg.startswith('-'):
				self.world.send_chan_msg('-err-', inf, """[invalid argument]
  nicks cannot start with "-" (dash)
""")
				return

			if u' ' in arg or u'\t' in arg:
				self.world.send_chan_msg('-err-', inf, """[invalid argument]
  nicks cannot contain whitespace
""")
				return

			other_user = None
			with self.world.mutex:
				for usr in self.world.users:
					if usr.nick == arg:
						other_user = usr
						break
				
				if other_user is not None:
					self.world.send_chan_msg('-err-', inf, """[invalid argument]
  that nick is taken
""")
					return

				for uchan in self.chans:
					self.world.send_chan_msg('--', uchan.nchan,
						'\033[1;36m{0}\033[22m changed nick to \033[1m{1}'.format(self.nick, arg))
				
				# update title in DM windows
				for nchan in self.world.priv_ch:
					for usr in nchan.uchans:
						if usr.alias == self.nick:
							usr.alias = arg

				self.set_nick(arg)



		elif cmd == 'topic' or cmd == 't':
			if not arg:
				self.world.send_chan_msg('-err-', inf, """[invalid argument]
  usage:     /topic  the_new_topic
  example:   /topic  cooking recipes
""")
				return

			uchan = self.active_chan
			nchan = uchan.nchan
			if nchan in self.world.priv_ch:
				self.world.send_chan_msg('-err-', inf, """[error]
  cannot change the topic of private channels
""")
				return

			old_topic = nchan.topic
			nchan.topic = arg
			self.world.send_chan_msg('--', nchan,
				'\033[36m{0} has changed the topic from [\033[0m{1}\033[36m] -to-> [\033[0m{2}\033[36m]\033[0m'.format(
				self.nick, old_topic, arg))



		elif cmd == 'join' or cmd == 'j':
			if not arg or len(arg) < 2:
				self.world.send_chan_msg('-err-', inf, """[invalid arguments]
  usage:     /join  #channel_name
  example:   /join  #general
""")
				return
			
			if not arg.startswith('#'):
				self.world.send_chan_msg('-err-', inf, """[error]
  illegal channel name:  {0}
  channel names must start with #
""".format(arg))
				return

			nchan = self.world.join_pub_chan(self, arg[1:]).nchan
			# this is in charge of activating the new channel,
			# rapid part/join will crash us without this
			self.client.refresh(False)
			
			if False:
				# measure performance on chans with too many messages
				if len(self.active_chan.nchan.msgs) < 1048576:
					for n in range(0,1048576):
						if n % 16384 == 0:
							print(n)
						self.world.send_chan_msg('--', self.active_chan.nchan, 'large history load test {0}'.format(n))



		elif cmd == 'part' or cmd == 'p':
			if self.active_chan.alias == 'r0c-status':
				self.world.send_chan_msg('-err-', inf, """[error]
  cannot part the status channel
""".format(arg))
				return

			self.world.part_chan(self.active_chan)
			# this is in charge of activating the new channel,
			# rapid part/join will crash us without this
			self.client.refresh(False)



		elif cmd == 'msg' or cmd == 'm':
			if not arg1 or not arg2:
				self.world.send_chan_msg('-err-', inf, """[invalid arguments]
  usage:     /msg   nickname   your message text
  example:   /msg   ed   hello world
""")
				return

			found = None
			for usr in self.world.users:
				if usr.nick == arg1:
					found = usr
					break

			if not found:
				self.world.send_chan_msg('-err-', inf, """[user not found]
  "{0}" is not online
""".format(arg1))
				return

			uchan = self.world.join_priv_chan(self, arg1)
			self.new_active_chan = uchan
			self.world.send_chan_msg(self.nick, uchan.nchan, arg2)



		elif cmd == 'up' or cmd == 'u':
			self.client.scroll_cmd = -(self.client.h - 4)
		
		elif cmd == 'down' or cmd == 'd':
			self.client.scroll_cmd = +(self.client.h - 4)
		
		elif cmd == 'latest' or cmd == 'l':
			self.active_chan.lock_to_bottom = True
			self.client.need_full_redraw = True
			self.client.refresh(False)

		elif cmd == 'redraw' or cmd == 'r':
			self.client.need_full_redraw = True
			self.client.refresh(False)



		elif cmd == 'sw':
			try: arg = int(arg)
			except: pass
			
			if not arg:
				self.world.send_chan_msg('-err-', inf, """[invalid arguments]
  usage:     /sw  your_screen_width
  example:   /sw  80
""")
				return

			self.client.w = arg



		elif cmd == 'sh':
			try: arg = int(arg)
			except: pass
			
			if not arg:
				self.world.send_chan_msg('-err-', inf, """[invalid arguments]
  usage:     /sh  your_screen_height
  example:   /sh  24
""")
				return

			self.client.h = arg



		elif cmd == 'cls':
			msg = Message(
				'-nfo-', self.active_chan.nchan, time.time(),
				u'\033[1;36m{0}\033[22m wiped the chat'.format(self.nick))
			msg.sno = 0
			self.active_chan.nchan.msgs = [msg]
			
		elif cmd == 'sd':
			msg = "\033[31mserver shutdown requested by \033[1m{0}".format(self.nick)
			self.world.broadcast(msg, 2)
			
			def killer():
				time.sleep(0.5)
				self.world.core.shutdown()
			
			thr = threading.Thread(target=killer)
			thr.daemon = True
			thr.start()



		else:
			self.world.send_chan_msg('-err-', inf, """invalid command:  /{0}
  if you meant to send that as a message,
  escape the leading "/" by adding another "/"
""".format(cmd_str))

	def set_nick(self, new_nick):
		self.nick = new_nick
		self.nick_re = re.compile(
			'(^|[^a-zA-Z0-9]){0}([^a-zA-Z0-9]|$)'.format(
				re.escape(self.nick)))
