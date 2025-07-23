: ${EDITOR:=nvim}
alias e=$EDITOR
alias se="sudoedit"
alias yolkrc="e ~/.config/yolk/"
alias nvimrc="e ~/.config/nvim/"
alias zrc="e ~/.config/zsh/ ; exec zsh"
alias wrc="e ~/.config/wezterm/wezterm.lua"
# alias ls="lsd --group-directories-first -F"
# alias lsa="ls -A"
alias up="paru -Syu"
alias dmg="sudo dmesg --color=always | less +G -R"
alias c="clear"
alias vencord='sh -c "$(curl -sS https://raw.githubusercontent.com/Vendicated/VencordInstaller/main/install.sh)"' 

# eza
alias ls='eza --icons --group-directories-first -F --hyperlink'
alias la='ls -a'              # show hidden
alias ll='ls -al'             # long + hidden
alias lt='ls --tree'          # tree view
alias lg='ls -l --git'        # git info

# fd
alias fd='fd --color=always'
alias fdf='fd --type f'         # files only
alias fdd='fd --type d'        # dirs only

alias mkdir='mkdir -p'
alias h='history'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

runbg() {
  if [ $# -eq 0 ]; then
    echo "Usage: runbg <command> [args...]"
    return 1
  fi
  "$@" > /dev/null 2>&1 & disown
}
