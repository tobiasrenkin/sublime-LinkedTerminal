## sublime-LinkedTerminal.

LinkedTerminal is a plugin for Sublime Text on Linux that connects an external terminal to Sublime Text. The plugin includes a build target that will execute build commands in the linked terminal and a "send" command that sends snippets of code to the terminal.

In contrast to some existing solutions that rely on automated copy and paste functionality, LinkedTerminal uses pipes for communication between Sublime Text and the terminal. It does not require any external packages for its core functionality.

### How to use it
* Download this repository into your Sublime Text Packages folder. Adjust settings in linkedterminal.sublime-settings (per default, linkedterminal will try to open xfce4-terminal with a zsh shell in it).
* Launch LinkedTerminal from within Sublime Text using the "linked_terminal_launch" command.
* Send snippets of code to the terminal using the "linked_terminal_send" command. The code will run in the shell open in the terminal (per default this is bash, but you can open a Python shell, etc.)
* Use "linked_terminal_exec" as a target in build systems to run build commands in the terminal.

### Settings
Default settings are in linkedterminal.sublime-settings.

### Key bindings
Default key bindings are in linkedterminal.sublime-keymap.

### Example build system

This is an example of a build system that runs pdflatex in a linked terminal and then opens the pdf in Xreader:

```JSON
{
	"selector": "text.tex.latex",
	"file_patterns": "*.tex",
	"cmd": "cd \"$file_path\"; pdflatex \"$file\"; nohup xreader \"$file_path/$file_base_name.pdf\">/dev/null 2>&1 &",
	"target": "linked_terminal_exec"
}

