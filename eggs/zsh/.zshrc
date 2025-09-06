# ~/.config/zsh/.zshrc

for config_file in ~/.config/zsh/*.zsh; do
  [[ $config_file != *".zshrc" ]] && source "$config_file"
done

