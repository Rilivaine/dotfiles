sudo pacman -Sy --needed base-devel

sudo pacman -S rust

if ! command -v paru &>/dev/null; then
  git clone https://aur.archlinux.org/paru.git ~/tmp/paru
  cd ~/tmp/paru || exit
  makepkg -si
  cd ~ || exit
  rm -rf ~/tmp/paru
else
  echo "paru is already installed."
fi

sudo pacman -S gum --noconfirm --quiet --noprogressbar

paru -S --noconfirm --needed --noprogressbar \
  zsh zsh-autosuggestions zsh-completions zsh-syntax-highlighting \
  hyprland hyprpicker hyprpolkitagent hyprlock hyprshade hyprshot xdg-desktop-portal-hyprland grim grimblast-git \
  yolk-bin ydotool wtype rofi swww swaync starship slurp swappy rofimoji wlogout keepassxc gnome-keyring nvm \
  pavucontrol pamixer neovim less btop waybar walker-bin \
  ttf-jetbrains-mono-nerd ttf-jetbrains-mono ttf-firacode-nerd noto-fonts-cjk noto-fonts-emoji tela-circle-icon-theme-dracula inter-font \
  udiskie fzf eza fd fastfetch dolphin cpupower cliphist btrfs-assistant brightnessctl bluez-utils blueman zen-browser-bin network-manager-applet visual-studio-code-bin

paru -Rns --noconfirm vim htop 2>/dev/null || true

chsh -s /usr/bin/zsh

if command -v yolk &>/dev/null; then
  sudo rm -rf /etc/pacman.conf ~/.config/hypr ~/.config/kitty
  yolk sync
else
  echo "yolk is not installed."
fi
