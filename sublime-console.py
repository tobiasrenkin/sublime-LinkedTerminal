import sublime, sublime_plugin
import os, sys
from subprocess import Popen, check_output, STDOUT
from random import randrange

class LaunchSublimeConsoleCommand(sublime_plugin.WindowCommand):
	def run(self):
		global pipe_location
		global pipe_no
		
		isrunning = int(check_output(['wmctrl -l | grep "Sublime Console" | wc -l'], shell=True).strip())
		if isrunning > 0:
			print("Sublime Console is already open.")
			Popen('wmctrl -a "Sublime Console"', shell=True)
		else:
			pipe_no = str(randrange(100000))
			pipe_location = "/tmp/sublime_console_"+pipe_no
		
			settings = sublime.load_settings("sublime-console.sublime-settings")
			if settings.get("launch_in_cwd"):
				launch_in=self.window.extract_variables()["file_path"]
			else:
				launch_in = "~"

			python_cmd = " ".join([
				"python", sublime.packages_path()+"/sublime-console/run_pty.py",
				"--pipe", pipe_location,
				"--shell", settings.get("shell"),
				"--raise_on_input" if settings.get("raise_on_input")==True else ""
				])
			launch_cmd = " ".join([
				settings.get("terminal"),'--title="Sublime Console {0}"'.format(pipe_no),"-x",
				settings.get("shell"),"-c",
				'"cd '+launch_in+'; '+python_cmd+'"'
				])

			p = Popen(launch_cmd, shell=True)

class SendCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = sublime.load_settings("sublime-console.sublime-settings")

		self.view.run_command("expand_selection", {"to": "line"})
		selection = self.view.sel()
		code = []
		for region in selection:
			code.append(self.view.substr(region).rstrip())
		
		try:
			with open(pipe_location, "w") as fifo:
				fifo.write("\n".join(code) + "\n")
		except:
			print("Error: Can't write to pipe at", settings.get("pipe_exec_location"))

class SublimeConsoleExec(sublime_plugin.WindowCommand):
	def run(self, cmd):
		settings = sublime.load_settings("sublime-console.sublime-settings")
		print(cmd)
		try:
			#settings.get("pipe_exec_location")
			with open(pipe_location, "w") as fifo:
				fifo.write(cmd + "\n")
		except:
			print("Error: Can't write to pipe at", settings.get("pipe_exec_location"))


