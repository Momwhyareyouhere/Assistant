#!/bin/bash

set -e

ASSISTANT_DIR="$HOME/Assistant"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "== Assistant Installer =="

cd "$ASSISTANT_DIR" || {
    echo "Assistant directory not found!"
    exit 1
}

chmod +x assistant assistant-keyboard

sudo mv assistant assistant-keyboard /usr/bin/

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Cannot detect distro."
    exit 1
fi

echo "Detected distro: $DISTRO"

case "$DISTRO" in
    arch)
        sudo pacman -Sy --noconfirm python python-pip
        ;;
    fedora)
        sudo dnf install -y python3 python3-pip python3-virtualenv
        ;;
    ubuntu|debian|linuxmint|pop)
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
        ;;
    opensuse*|suse)
        sudo zypper install -y python3 python3-pip python3-virtualenv
        ;;
    *)
        sudo apt update && sudo apt install -y python3 python3-pip python3-venv || true
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

if [ -f venv/bin/activate ]; then
    source venv/bin/activate
elif [ -f venv/bin/activate.fish ]; then
    source venv/bin/activate.fish
else
    echo "Could not activate virtual environment"
    exit 1
fi

pip install --upgrade pip
pip install -r requirements.txt

deactivate 2>/dev/null || true

read -p "Do you want to put the assistant in autostart? (Y/N): " AUTOSTART

if [[ "$AUTOSTART" =~ ^[Yy]$ ]]; then
    mkdir -p "$AUTOSTART_DIR"
    cp "$ASSISTANT_DIR/assistant.desktop" "$AUTOSTART_DIR/"
fi

cd "$HOME"

echo
echo "Installation complete!"
echo "To run the assistant:"
echo "  assistant"
echo "Or for keyboard mode:"
echo "  assistant-keyboard"
