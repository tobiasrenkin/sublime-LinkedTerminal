#!/usr/bin/env python

from __future__ import print_function
import os, sys, select, signal, termios, fcntl, tty, pty, subprocess, atexit, argparse, struct, time

print('Sublime Console v0.1.')

parser = argparse.ArgumentParser(description='Sublime Console connects your terminal to Sublime Text through a named pipe.')
parser.add_argument('--pipe', 
	default="/tmp/sublime_console.fifo", 
	action="store", 
	dest="pipe", 
	help="Create pipe at this location."
	)
parser.add_argument('--shell', 
	default="bash", 
	action="store", 
	dest="shell", 
	choices=["bash", "sh", "zsh", "fish"], 
	help="Shell to run."
	)
parser.add_argument('--raise_on_input', 
	action="store_true", 
	dest="raise_on_input", 
	help="Terminal is raised to top of window list on input."
	)
args = parser.parse_args()

def delete_fifo():
	if os.path.exists(args.pipe):
		os.remove(args.pipe)

# set event handler
def sigintHandler(signum, frame):
	os.close(fifo_fd)
	delete_fifo()
	termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_tty)
	sys.exit("Closing Sublime Console.")
	
signal.signal(signal.SIGINT, sigintHandler)
signal.signal(signal.SIGHUP, sigintHandler)
signal.signal(signal.SIGTERM, sigintHandler)
atexit.register(delete_fifo)

# make sure parent terminal and pty master have same dimensions; always resize on start
pty_size_h = 0
pty_size_w = 0
def ensure_equal_size():
	global pty_size_h, pty_size_w
	parent_shell_h, parent_shell_w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
	if parent_shell_h!=pty_size_h or parent_shell_w!=pty_size_w:
		tiocswinsz = getattr(termios, 'TIOCSWINSZ', -2146929561)
		size_update = struct.pack('HHHH', parent_shell_h, parent_shell_w, 0, 0)
		fcntl.ioctl(master_fd, tiocswinsz, size_update)
		pty_size_h=parent_shell_h
		pty_size_w=parent_shell_w

def set_focus():
	try:
		subprocess.Popen('wmctrl -a "Sublime Console"', shell=True)
	except:
		pass

##############################################################################

# create fifo;
if os.path.exists(args.pipe):
	sys.exit("Error: pipe "+args.pipe+" already exists.")
else:
	os.mkfifo(args.pipe, 0644)
	print("Listening to stdin and "+args.pipe)

# save original tty setting then set it to raw or cbreak mode
old_tty = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin.fileno())

# open pty and bash subprocess; connect all pipes of bash subprocess to slave half of pty.
master_fd, slave_fd = pty.openpty()
p = subprocess.Popen(args.shell,
	preexec_fn=os.setsid,
	stdin=slave_fd,
	stdout=slave_fd,
	stderr=slave_fd,
	universal_newlines=True)

# open named pipe, forward stdin/pipe input to pty master, forward master to stdout
fifo_fd = os.open(args.pipe, os.O_RDWR)
last_resize_check = 0
last_focus_set = 0

while p.poll() is None:
	try:
		r, w, e = select.select([sys.stdin, master_fd, fifo_fd], [], [])
		
		# on select, ensure pty and parent tty have same dimensions; at most once every second.
		if time.time()-last_resize_check>1:
			ensure_equal_size()
			last_resize_check = time.time()

		if sys.stdin in r or fifo_fd in r:
			if sys.stdin in r:
				pty_input = os.read(sys.stdin.fileno(), 10240)
			elif fifo_fd in r:
				pty_input = os.read(fifo_fd, 10240)
			
			if pty_input:
				os.write(master_fd, pty_input)
				if args.raise_on_input and time.time() - last_focus_set >1:
					set_focus()
					last_focus_set = time.time()

		elif master_fd in r:
			o = os.read(master_fd, 10240)
			if o:
				os.write(sys.stdout.fileno(), o)

	except select.error as ex:
		if ex[0] == 4:
			pass
		else:
			raise