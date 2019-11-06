## Sublime Console v0.1.

### What is Sublime Console?

Sublime Console is a Sublime Text plugin that opens a terminal. The terminal is connected to a pipe, and Sublime Text (or any other application) can communicate with the terminal through the pipe.

### Applications
* The plugin comes with a built-in "send" command. The send command sends text selected in a Sublime Text view to be executed in the terminal.
* You can write build systems that write build commands directly to the pipe. The file is then built in an external terminal instead of within Sublime. This is useful for interactive programs, debugging, or if you just like your external terminal.

### Settings
Default settings are in sublime-console.sublime-settings.

* _terminal:_ terminal emulator to use. Default is terminator.
* _shell:_ shell to use. Default is bash.
* _pipe_exec_location:_ location of named pipe to create. The pipe is created when the console is launched and deleted when it is closed. Default location is /tmp/sublime_console.fifo. 
* _allow_multiple_inst_ allow more than one open console. per default, opening more than one console is disabled. Since all instances would read from the same pipe, it is not recommended to enable this option without adding handling of multiple pipes to the plugin.

### Key bindings
Default key bindings are in sublime-console.sublime-keymap.

* _ctrl+keypad0_ opens console
* _ctrl+d_ sends selected text

### Example build system

This is an example for a build system that runs latexmk in an open console:

```JSON
{
	"selector": "text.tex.latex",
	"file_patterns": "*.tex",
	"shell": true,
	"shell_cmd": "echo \"latexmk -cd -pdf -quiet $file\">/tmp/sublime_console.fifo"
}
