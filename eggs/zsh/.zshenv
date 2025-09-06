export EDITOR=nvim
export LESS='-R'

export PATH=$PATH:~/.local/bin
export PATH=$PATH:~/.cargo/bin
export ZDOTDIR="$HOME/.config/zsh"

# nvm: use system or manual install if available
if [ -f /usr/share/nvm/init-nvm.sh ]; then
    source /usr/share/nvm/init-nvm.sh
elif [ -d "$HOME/.nvm" ]; then
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"
fi

if [ -f /usr/share/vcpkg ]; then
  export VCPKG_ROOT=/usr/share/vcpkg
fi
