sudo pacman -Sy --needed base-devel

sudo pacman -S rustup
rustup default stable

git clone https://aur.archlinux.org/paru.git ~/tmp/paru
cd ~/tmp/paru
makepkg -si

paru -S --noconfirm \
  zsh zsh-autosuggestions zsh-completions zsh-syntax-highlighting \
  hyprland hyprpicker hyprpolkitagent hyprlock hyprshade hyprshot xdg-desktop-portal-hyprland grim grimblast-git \
  yolk-bin wtype rofi swww swaync starship slurp rofimoji wlogout keepassxc \
  pavucontrol pamixer neovim less btop waybar walker-bin \
  ttf-jetbrains-mono-nerd ttf-jetbrains-mono ttf-firacode-nerd noto-fonts-cjk noto-fonts-emoji tela-circle-icon-theme-dracula inter-font \
  udiskie fzf eza fd fastfetch dolphin cpupower cliphist btrfs-assistant brightnessctl bluez-utils blueman zen-browser-bin network-manager-applet visual-studio-code-bin

sudo rm -rf /etc/pacman.conf ~/.config/hypr ~/.config/kitty

chsh -s /usr/bin/zsh

yolk sync
