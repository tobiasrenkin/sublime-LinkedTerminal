import sublime, sublime_plugin
import os, sys
import subprocess
from random import randrange

console = None

class SublimeConsole():
	def __init__(self, settings):
		self.pipe_no = randrange(100000)
		self.pipe_location = "/tmp/sublime_console_" + str(self.pipe_no)
		self.p = None
		self.settings = settings

	def send(self, cmd):
		try:
			with open(self.pipe_location, "w") as fifo:
				fifo.write(cmd + "\n")
		except:
			print("Error: Can't write to pipe at", self.pipe_location)

	def isalive(self):
		#open_consoles = int(check_output(['wmctrl -l | grep "Sublime Console {0}" | wc -l'.format(self.pipe_no)], shell=True).strip())
		if self.p == None:
			return False
		else:
			response = self.p.poll()
			print("response", response)
			if response == None:
				return True
			else:
				return False

	def launch(self):
		if self.isalive():
			subprocess.Popen('wmctrl -a "Sublime Console {0}"'.format(self.pipe_no), shell=True)
			print("Console is alive")
		else:
			if self.settings.get("launch_in_cwd"):
				#launch_in=self.window.extract_variables()["file_path"]
				launch_in = "~"
			else:
				launch_in = "~"
			python_cmd = " ".join([
				"python", sublime.packages_path()+"/sublime-console/run_pty.py",
				"--pipe", self.pipe_location,
				"--shell", self.settings.get("shell"),
				"--raise_on_input" if self.settings.get("raise_on_input")==True else ""
			])
			launch_cmd = " ".join([
				self.settings.get("terminal"),'--title="Sublime Console {0}"'.format(self.pipe_no),"-x",
				self.settings.get("shell"),"-c",
				'"cd '+launch_in+'; '+python_cmd+'"'
			])
			self.p = subprocess.Popen(launch_cmd, shell=True)
			print(self.p.poll())

class SublimeConsoleLaunchCommand(sublime_plugin.WindowCommand):
	def run(self):
		global console
		if not(console):
			settings = sublime.load_settings("sublime-console.sublime-settings")
			console = SublimeConsole(settings)
		console.launch()

class SublimeConsoleSendCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global console

		self.view.run_command("expand_selection", {"to": "line"})
		selection = self.view.sel()
		code = []
		for region in selection:
			code.append(self.view.substr(region).rstrip())
		
		console.send("\n".join(code) + "\n")
		
class SublimeConsoleExec(sublime_plugin.WindowCommand):
	def run(self, cmd):
		global console
		console.send(cmd)
		

