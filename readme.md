## Sublime Console

Sublime Console is a plugin for Sublime Text on Linux that connects an external terminal to Sublime Text. The plugin  comes with a build target that will execute build commands in the terminal and a "send" command that sends snippets of code to the terminal.

In contrast to some existing solutions that rely on automated copy and paste functionality, Sublime Control uses pipes for communication between Sublime Text and the terminal. It does not require any external packages for it's core functionality.

### How to use it
* Launch Sublime Console from within Sublime Text using "sublime_console_launch".
* Send snippets of code to the terminal using "sublime_console_send". The code will run in the shell open in the terminal (per default this is bash, but you can open a Python shell, etc.)
* Use "sublime_console_exec" as a target in build systems to run build commands in the terminal.

### Settings
Default settings are in sublime-console.sublime-settings.

### Key bindings
Default key bindings are in sublime-console.sublime-keymap.

### Example build system

This is an example of a build system that runs pdflatex in an open Sublime Console and then opens the pdf in Xreader:

```JSON
{
	"selector": "text.tex.latex",
	"file_patterns": "*.tex",
	"cmd": "cd $file_path; pdflatex $file; nohup xreader $file_path/$file_base_name.pdf>/dev/null 2>&1 &",
	"target": "sublime_console_exec"
}
