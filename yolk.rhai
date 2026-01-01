export let eggs = #{
    hypr: #{
      targets: "~/.config/hypr",
    },
    waybar: #{
	    targets: "~/.config/waybar",
    },
    walker: #{
      targets: "~/.config/walker",
    },
    rofi: #{
    	targets: "~/.config/rofi",
    },
    swaylock: #{
    	targets: "~/.config/swaylock",
    },
    swaync: #{
    	targets: "~/.config/swaync",
    },
    quickshell: #{
        targets: "~/.config/quickshell",
    },
    eww: #{
    	targets: "~/.config/eww",
    },
    wlogout: #{
    	targets: "~/.config/wlogout",
    },
    dunst: #{
    	targets: "~/.config/dunst",
    },
    kitty: #{
    	targets: "~/.config/kitty",
    },
    fastfetch: #{
    	targets: "~/.config/fastfetch",
    },
    zsh: #{
    	targets: #{
		    ".": "~/.config/zsh",
		    ".zshenv": "~/.zshenv",
	    },
    },
    starship: #{
    	targets: #{
        "starship.toml": "~/.config/starship.toml"
      },
    },
    nvim: #{ 
    	targets: "~/.config/nvim", 
    },
    scripts: #{
      targets: "~/.dotscripts",
    },
    global_config: #{
      targets: #{
        "kdeglobals": "~/.config/kdeglobals",
        "pacman.conf": "/etc/pacman.conf",
      },
    },
    menus: #{
      targets: "~/.config/menus",
    },
    paru: #{
      targets: "~/.config/paru"
    },
    themes: #{
      targets: "~/.themes"
    },
    btop: #{
      targets: "~/.config/btop"
    },
    pacman_hooks: #{
      targets: "/etc/pacman.d/hooks",
      templates: ["discord-vencord.hook"]
    },
    desktop_files: #{
        targets: "~/.local/share/applications",
        strategy: "merge"
    }
};
