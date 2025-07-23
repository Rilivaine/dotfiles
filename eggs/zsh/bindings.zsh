bindkey '^[[5~' up-line-or-search     # Page Up: search backward in history
bindkey '^[[6~' down-line-or-search   # Page Down: search forward in history
bindkey -M vicmd '?' history-incremental-search-backward
bindkey "^[m" copy-earlier-word
bindkey "^[." insert-last-word

