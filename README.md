# Description

Make `~/.bash_history` or `~/.zsh_history` tidy by filtering out unwanted history lines.


# Usage

1. Compile `unmetafy.c` into `unmetafy` by `make`.
2. Put the following code to a shell script (called `tidy.sh` here):

```sh
mv ~/.zsh_history ~/.zsh_history.bak
python3 /absolute/path/to/tidy_sh_history.py ~/.zsh_history.bak ~/.zsh_history /whatever/path/to/log_output.log
```

3. In `crontab -e` add:

```sh
@hourly /bin/sh /absolute/path/to/tidy.sh
```
