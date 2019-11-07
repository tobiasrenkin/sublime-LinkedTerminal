#!/usr/bin/env python

from __future__ import print_function
import os, sys, select, signal, termios, fcntl, tty, pty, subprocess, atexit, argparse, struct, time

parser = argparse.ArgumentParser(description='Sublime Console connects your terminal to Sublime Text through a named pipe.')
parser.add_argument('--pipe_exec', default="/tmp/sublime_console.fifo", action="store", dest="pipe_exec", help="Create pipe at this location.")
parser.add_argument('--shell', default="bash", action="store", dest="shell", choices=["bash", "sh", "zsh", "fish"], help="Shell to run.")
args = parser.parse_args()
shell_cmd = args.shell
fifo_exec_loc = args.pipe_exec

print('Sublime Console v0.1.')

def delete_fifo():
	if os.path.exists(fifo_exec_loc):
		os.remove(fifo_exec_loc)

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
mstr_h = 0
mstr_w = 0
def ensure_equal_size():
	global mstr_h, mstr_w
	prnt_h, prnt_w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
	if prnt_h!=mstr_h or prnt_w!=mstr_w:
		tiocswinsz = getattr(termios, 'TIOCSWINSZ', -2146929561)
		size_update = struct.pack('HHHH', prnt_h, prnt_w, 0, 0)
		fcntl.ioctl(master_fd, tiocswinsz, size_update)
    	mstr_h=prnt_h
    	mstr_w=prnt_w


# create fifo;
if os.path.exists(fifo_exec_loc):
	print("Warning: pipe "+fifo_exec_loc+" already exists. Other processes may read from it. Expect strangeness.")
else:
	os.mkfifo(fifo_exec_loc, 0644)
	print("Executing from "+fifo_exec_loc)

# save original tty setting then set it to raw or cbreak mode
old_tty = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin.fileno())

# open pty and bash subprocess; connect all pipes of bash subprocess to slave half of pty.
master_fd, slave_fd = pty.openpty()
p = subprocess.Popen(shell_cmd,
	preexec_fn=os.setsid,
	stdin=slave_fd,
	stdout=slave_fd,
	stderr=slave_fd,
	universal_newlines=True)

# open pipe, forward stdin/fifo to pty master, write master to stdout
fifo_fd = os.open(fifo_exec_loc, os.O_RDWR)
last_resize_check = 0

while p.poll() is None:
	try:
		r, w, e = select.select([sys.stdin, master_fd, fifo_fd], [], [])
		
		# check for terminal resize when input or output is received; at most once every second
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

		elif master_fd in r:
			o = os.read(master_fd, 10240)
			if o:
				os.write(sys.stdout.fileno(), o)

	except select.error as ex:
		if ex[0] == 4:
			pass
		else:
			raise