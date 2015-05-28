# NU Laundry CLI
### Intro
Why use laundryview.com when you can use a CLI? Check the statuses of all laundry machines in any dorm you wish! You can even set a custom timer for *your* laundry!

A CLI for the laundry system at Northeastern University, which as a result, is also a potential CLI for laundryview.com (since Northeastern utilizes that) and other universities though this has <b>NOT</b> been tested whatsoever.

### Setup
I recommend setting up an alias in your .bash_profile, .zshrc, etc for this like so
```
alias laundry="python /path/to/main.py"
```
Be sure to install the dependencies like so (under the assumption that you have pip installed):
```
pip install -r /path/to/requirements.txt
```

### Commands
```
dorms - Returns the full list of dorms and their corresponding numbers
status <x> - Get status of all laundry machines in dorm number <x>
alert <string> <string> ... - Change the default alert message(s) to the sequence of string(s). Must add at least one.
timer <x> <y> - Will alert you when laundry machine <y> has finished its laundry cycle in dorm number <x>
stop - Stops any timer that was set previously
```

### Dependencies
* BeautifulSoup
* Colorama
* PycURL
* Tabulate

### Other
* Still needs a lot of work, and is probably very buggy at the moment.
* Custom timer messages will only be set for that CLI session (if you exit the script, it will reset to the default messages).

ASCII art intro message for fun

![intro msg](intro.png?raw=true "Optional Title")

Getting list of dorms that have laundry machines on campus

![dorm list](dorms.png?raw=true "Optional Title")

Getting laundry machine statuses in West Village E (corresponding to dorm number 42)

![machine statuses](status.png?raw=true "Optional Title")

Setting a timer for laundry machine 12 in West Village E

![timer](timer.png?raw=true "Optional Title")
