#!/bin/bash
set -e

ASSISTANT_DIR="$HOME/Assistant"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "== Assistant Installer =="

cd "$ASSISTANT_DIR" || exit 1

chmod +x assistant assistant-keyboard
sudo mv assistant assistant-keyboard /usr/bin/

. /etc/os-release
DISTRO=$ID

case "$DISTRO" in
    arch)
        sudo pacman -Sy --noconfirm python python-pip python-virtualenv espeak-ng
        ;;
    fedora)
        sudo dnf install -y python3 python3-pip python3-virtualenv espeak-ng
        ;;
    ubuntu|debian|linuxmint|pop)
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv espeak-ng
        ;;
    opensuse*|suse)
        sudo zypper install -y python3 python3-pip python3-virtualenv espeak-ng
        ;;
    *)
        sudo apt update && sudo apt install -y python3 python3-pip python3-venv espeak-ng || true
        ;;
esac

if ! python3 -m venv venv; then
    case "$DISTRO" in
        arch)
            sudo pacman -Sy --noconfirm python-virtualenv
            ;;
        fedora)
            sudo dnf install -y python3-virtualenv
            ;;
        ubuntu|debian|linuxmint|pop)
            sudo apt install -y python3-venv
            ;;
        opensuse*|suse)
            sudo zypper install -y python3-virtualenv
            ;;
    esac
    python3 -m venv venv
fi

[ -f venv/bin/activate ] && source venv/bin/activate || exit 1

pip install --upgrade pip
pip install -r requirements.txt

deactivate 2>/dev/null || true

read -p "Do you want to put the assistant in autostart? (Y/N): " AUTOSTART

[[ "$AUTOSTART" =~ ^[Yy]$ ]] && mkdir -p "$AUTOSTART_DIR" && cp "$ASSISTANT_DIR/assistant.desktop" "$AUTOSTART_DIR/"

cd "$HOME"

echo "Installation complete!"
echo "assistant"
echo "assistant-keyboard"
