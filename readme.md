# Sublime Console v0.1.

## What is Sublime Console?

Sublime Console is a Sublime Text plugin that opens a terminal. The terminal is connected to a pipe, and Sublime Text (or any other application) can communicate with the terminal through the pipe.

## Applications
* The plugin comes with a built-in "send" command. The send command sends text selected in a Sublime Text view to be executed in the terminal.
* You can write build systems that write build commands directly to the pipe. The file is then built in an external terminal instead of within Sublime. This is useful for interactive programs, debugging, or if you just like your external terminal.

## Settings
Default settings are in sublime-console.sublime-settings.

* "terminal" sets the terminal emulator to use. Default is terminator.
* "shell" sets the shell to use. Default is bash.
* "pipe_exec_location" sets the location of the named pipe to create when Sublime Console is launched. Default is /tmp/sublime_console.fifo. 
* "allow_multiple_inst" keeps you from opening more than one console. Because both would read from the same pipe, this would result in strange behavior.

## Key bindings
Default key bindings are in sublime-console.sublime-keymap.

* "ctrl+d" sends selected text to terminal.
* "ctrl+keypad0" opens console.

## Example build system

This is an example for a build system that runs latexmk in an open console:

```JSON
{
	"selector": "text.tex.latex",
	"file_patterns": "*.tex",
	"shell": true,
	"shell_cmd": "echo \"latexmk -cd -pdf -quiet $file\">/tmp/sublime_console.fifo"
}
'''