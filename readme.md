## Sublime Console v0.1.

A plugin for Sublime Text on Linux that connects an external terminal to Sublime Text.

### What does the plugin do?

Sublime Console is a Sublime Text plugin that opens a terminal. The terminal is connected to a named pipe. It can receive code from both the system stdin and the pipe. Sublime Text (or any other application) can communicate with the terminal through the pipe.

### Why is this useful?
* The plugin comes with a built-in "send" command. The send command sends text selected in a Sublime Text to the terminal and the text is then interpreted by the shell (or whatever other program is open in the terminal).
* You can write build systems that send build commands directly to the pipe. The build command then runs in the external terminal instead of within Sublime. This is useful for interactive programs, debugging, or if you just like your external terminal.

### Settings
Default settings are in sublime-console.sublime-settings.

### Key bindings
Default key bindings are in sublime-console.sublime-keymap.

### Example build system

This is an example for a build system that runs latexmk in an open console:

```JSON
{
	"selector": "text.tex.latex",
	"file_patterns": "*.tex",
	"shell": true,
	"shell_cmd": "echo \"latexmk -cd -pdf -quiet $file\">/tmp/sublime_console.fifo"
}
