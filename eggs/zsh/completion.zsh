# completion
ZSH_COMPDUMP="${ZDOTDIR:-$HOME}/.zcompdump"
zstyle ':completion:*' rehash true
autoload -Uz compinit
if [[ -n "$ZSH_COMPDUMP" ]]; then
  compinit -d "$ZSH_COMPDUMP"
else
  compinit -C
fi
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
# zstyle ':completion:*' menu select
zstyle ':completion::complete:*' gain-privileges 1

