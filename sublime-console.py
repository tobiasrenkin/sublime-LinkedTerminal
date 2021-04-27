#!/usr/bin/env python

import sublime, sublime_plugin
import os, sys
import subprocess
from random import randrange
import time
console = None

class SublimeConsole():
	def __init__(self, settings):
		self.pipe_no = randrange(1000000)
		self.pipe_location = "/tmp/sublime_console_" + str(self.pipe_no)
		self.settings = settings
		self.p = None

	def send(self, cmd):
		try:
			with open(self.pipe_location, "w") as fifo:
				fifo.write(cmd + "\n")
		except:
			print("Error: Can't write to pipe at", self.pipe_location)

	def isalive(self):
		if self.p == None:
			return False
		else:
			return (self.p.poll() == None)


	def launch(self, path):
		if self.isalive():
			subprocess.Popen('wmctrl -a "Sublime Console {0}"'.format(self.pipe_no), shell=True)

		else:
			launch_in = path if self.settings.get("launch_in_cwd") else "~"
			python_cmd = " ".join([
				"python", sublime.packages_path()+"/sublime-console/run_pty.py",
				"--pipe", self.pipe_location,
				"--shell", self.settings.get("shell"),
				"--raise_on_input" if self.settings.get("raise_on_input", False) else ""
			])
			launch_cmd = " ".join([
				self.settings.get("terminal"),'--title="Sublime Console {0}"'.format(self.pipe_no),"-x",
				self.settings.get("shell"),"-c",
				'"cd '+launch_in+'; '+python_cmd+'"'
			])
			self.p = subprocess.Popen(launch_cmd, shell=True)
						
class SublimeConsoleLaunchCommand(sublime_plugin.WindowCommand):
	def run(self):
		global console
		pd = self.window.extract_variables().get("project_path", None)
		cwd = self.window.extract_variables().get("file_path", None)
		path = pd if pd else cwd if cwd else "~"
		if not(console):
			settings = sublime.load_settings("sublime-console.sublime-settings")
			console = SublimeConsole(settings)
		console.launch(path)

class SublimeConsoleSendCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global console

		self.view.run_command("expand_selection", {"to": "line"})
		selection = self.view.sel()
		code = []
		for region in selection:
			code.append(self.view.substr(region).strip())
			print(code)
		# TODO: remove excessive indent for python snippets to run
		console.send("\n".join(code))
		
class SublimeConsoleExec(sublime_plugin.WindowCommand):
	def run(self, cmd):
		global console
		console.send(cmd + "\n")
		

