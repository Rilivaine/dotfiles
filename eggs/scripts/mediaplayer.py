#!/usr/bin/env python3
import sys
import os
import json
import signal
import argparse
import logging

import gi
gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl, GLib


def _write_output(text: str, player_name: str, tooltip: str = ""):
    payload = {
        "text": text,
        "class": f"custom-{player_name}",
        "alt": player_name,
        "tooltip": tooltip or text,
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def signal_term_handler(signum, frame):
    sys.stdout.write("\n")
    sys.stdout.flush()
    sys.exit(0)


class WaybarPlayerctl:
    def __init__(self, player_filter=None):
        self.filter = player_filter.lower() if player_filter else None
        self.manager = Playerctl.PlayerManager()
        self.loop = GLib.MainLoop()
        self.manager.connect("name-appeared", self._on_name_appeared)
        self.manager.connect("player-vanished", self._on_player_vanished)

    def start(self):
        signal.signal(signal.SIGINT, signal_term_handler)
        signal.signal(signal.SIGTERM, signal_term_handler)

        self._discover_players()
        GLib.idle_add(self._check_initial)
        self.loop.run()

    def _discover_players(self):
        for pname in self.manager.props.player_names:
            name_str = pname.name
            if self.filter and name_str.lower() != self.filter:
                continue
            player = Playerctl.Player.new_from_name(pname)
            player.connect("playback-status", self._on_status)
            player.connect("metadata", self._on_metadata)
            self.manager.manage_player(player)

    def _check_initial(self):
        names = [pname.name.lower() for pname in self.manager.props.player_names]
        if self.filter and self.filter not in names:
            _write_output(f"No {self.filter.title()} instance", self.filter)
        elif not names:
            _write_output("No media players found", 'playerctl')
        else:
            self._show_active()
        return False

    def _show_active(self):
        players = self.manager.props.players[::-1]
        active = next((p for p in players if p.props.status.lower() == 'playing'), None)
        target = active or (players[0] if players else None)
        if target:
            self._update_output(target)
        else:
            sys.stdout.write("\n")

    def _on_name_appeared(self, _, pname):
        name_str = pname.name
        if self.filter and name_str.lower() != self.filter:
            return
        player = Playerctl.Player.new_from_name(pname)
        player.connect("playback-status", self._on_status)
        player.connect("metadata", self._on_metadata)
        self.manager.manage_player(player)
        self._update_output(player)

    def _on_player_vanished(self, _, player):
        # When a player closes, refresh; if filtered player gone, show fallback
        current_names = [pname.name.lower() for pname in self.manager.props.player_names]
        if self.filter and self.filter not in current_names:
            _write_output(f"No {self.filter.title()} instance", self.filter)
        else:
            self._show_active()

    def _on_status(self, player, status):
        self._update_output(player)

    def _on_metadata(self, player, metadata):
        self._update_output(player)

    def _update_output(self, player):
        name = player.props.player_name.lower()
        artist = player.get_artist() or ''
        title = player.get_title() or ''
        
        # Safely extract trackid string
        try:
            trackid_variant = player.props.metadata.lookup_value(
                'mpris:trackid', GLib.VariantType.new('s')
            )
            trackid = trackid_variant.get_string()
        except Exception:
            trackid = ''

        if name == 'spotify' and ':ad:' in trackid:
            text = 'Advertisement'
        else:
            text = f"{artist} - {title}" if artist and title else title or ''

        icon = '' if player.props.status.lower() == 'playing' else ''
        display = f"{icon} {text}" if text else ''

        _write_output(display, name, tooltip=text)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--player", help="filter to a specific player")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("--enable-logging", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    level = max((3 - args.verbose) * 10, logging.WARNING)
    if args.enable_logging:
        log_file = os.path.join(os.path.dirname(__file__), 'media-player.log')
        logging.basicConfig(filename=log_file, level=logging.DEBUG,
                            format="%(asctime)s %(levelname)s:%(message)s")
    logging.getLogger().setLevel(level)

    controller = WaybarPlayerctl(player_filter=args.player)
    controller.start()


if __name__ == "__main__":
    main()

