# ~/.config/zsh/.zshrc

for config_file in ~/.config/zsh/*.zsh; do
  [[ $config_file != *".zshrc" ]] && source "$config_file"
done


# pnpm
export PNPM_HOME="/home/Deo/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
# pnpm end
