import sublime, sublime_plugin
import os, sys
from subprocess import Popen

class LaunchSublimeConsoleCommand(sublime_plugin.WindowCommand):
	def run(self):
		settings = sublime.load_settings("sublime-console.sublime-settings")
		if settings.get("launch_in_cwd"):
			launch_in=self.window.extract_variables()["file_path"]
		else:
			launch_in = "~"

		python_cmd = " ".join([
			"python", sublime.packages_path()+"/sublime-console/run_pty.py",
			"--pipe_exec", settings.get("pipe_exec_location"),
			"--shell", settings.get("shell")
			])
		launch_cmd = " ".join([
			settings.get("terminal"),'--title="Sublime Console"',"-x",
			settings.get("shell"),"-c",
			'"cd '+launch_in+'; '+python_cmd+'"'
			])

		if os.path.exists(settings.get("pipe_exec_location")) and not(settings.get("allow_multiple_inst")):
			print("Warning:", settings.get("pipe_exec_location"), "already exists. There is probably already a Sublime Console running and I won't open a new one.")
		else:
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
			with open(settings.get("pipe_exec_location"), "w") as fifo:
				fifo.write("\n".join(code) + "\n")
		except:
			print("Error: Can't write to pipe at", settings.get("pipe_exec_location"))

