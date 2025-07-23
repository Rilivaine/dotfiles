bindkey -v
bindkey "^H" backward-kill-word
bindkey "^[[3~" delete-char
bindkey "^[[3;5~" kill-word
export KEYTIMEOUT=1

WORDCHARS=''

zle-line-init() {
  zle -K viins
  echo -ne '\e[6 q'
}
zle -N zle-line-init

delete_or_kill_line() {
  if [[ -z $LBUFFER ]]; then
    BUFFER=""        # remove entire line
    CURSOR=0         # reset cursor
  else
    zle backward-delete-char
  fi
}
zle -N delete_or_kill_line

bindkey -M viins '^?' delete_or_kill_line
bindkey -M viins '^H' delete_or_kill_line

echo -ne '\e[6 q'
preexec() { echo -ne '\e[6 q' ;}

# in vi insert mode, bind Enter (CR) to insert a newline + indent
bindkey -M viins $'\e\r' self-insert-unmeta

