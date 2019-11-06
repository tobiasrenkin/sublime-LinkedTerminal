#!/usr/bin/env python

from __future__ import print_function
import os, sys, re, readline, select, signal, termios, tty, pty, threading, time, subprocess, atexit, argparse

parser = argparse.ArgumentParser(description='Sublime Console connects your terminal to Sublime Text through a named pipe.')
parser.add_argument('--pipe_exec', default="/tmp/sublime_exec.fifo", action="store", dest="pipe_exec", help="Create pipe at this location.")
parser.add_argument('--pipe_print', default="/tmp/sublime_print.fifo", action="store", dest="pipe_print", help="Create pipe at this location.")
parser.add_argument('--shell', default="bash", action="store", dest="shell", choices=["bash", "sh", "zsh", "fish"], help="Shell to run.")
args = parser.parse_args()
shell_cmd = args.shell
fifo_exec_loc = args.pipe_exec
fifo_print_loc = args.pipe_print

print('Sublime Console v0.1.')

def delete_fifo():
	if os.path.exists(fifo_exec_loc):
		os.remove(fifo_exec_loc)

# set event handler
def sigintHandler(signum, frame):
	os.close(fifo_exec)
	delete_fifo()
	termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_tty)
	sys.exit("Closing Sublime Console.")
signal.signal(signal.SIGINT, sigintHandler)
signal.signal(signal.SIGHUP, sigintHandler)
signal.signal(signal.SIGTERM, sigintHandler)
atexit.register(delete_fifo)

# create fifo;
if os.path.exists(fifo_exec_loc):
	print("Warning: pipe "+fifo_exec_loc+" already exists. Other processes may read from it. Expect strangeness.")
else:
	os.mkfifo(fifo_exec_loc, 0777)
	print("Executing from "+fifo_exec_loc)

# save original tty setting then set it to raw or cbreak mode; that means everything will be passed to pty immediately
# as it is typed and parent terminal will not translate ctrl+c etc. into signals.
old_tty = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin.fileno())

# open pty and bash subprocess; connect all pipes of bash to slave half of pty.
# writing to master_fd is input to slave_fd and hence bash.
# output of bash is output in slave_fd and hence is an input in master_fd
master_fd, slave_fd = pty.openpty()
p = subprocess.Popen(shell_cmd,
	preexec_fn=os.setsid,
	stdin=slave_fd,
	stdout=slave_fd,
	stderr=slave_fd,
	universal_newlines=True)

# connect tty I/O to pty
fifo_exec = os.open(fifo_exec_loc, os.O_RDWR)
while p.poll() is None:
	try:
		r, w, e = select.select([sys.stdin, master_fd, fifo_exec], [], [])
		if sys.stdin in r:
			stdinput = os.read(sys.stdin.fileno(), 10240)
			if stdinput:
				os.write(master_fd, stdinput)
		elif fifo_exec in r:
			fifoinput = os.read(fifo_exec, 10240)
			if fifoinput:
				os.write(master_fd, fifoinput)
		elif master_fd in r:
			o = os.read(master_fd, 10240)
			if o:
				os.write(sys.stdout.fileno(), o)
	except select.error as ex:
		if ex[0] == 4:
			pass
		else:
			raise