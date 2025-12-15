# Assistant

Recently I noticed that there are Assistants for phones but not for Desktop Users so I made this Assistant for Desktop Users Its open source and you can add you own commands.

To put you own commands just go to commands.txt put you own command and then go to app.py make you own function and thats it you have you own custom command.

There are also prebuilt commands for Linux Users and here is how to implement it:

1. Activate venv

  To activate venv you need to install it first here is the command and make sure you are in the path ~ or else it wont work.

```
cd ~
python3 -m venv venv
source venv/bin/activate
```
2. Clone the repository

To do that you need to have git installed on you system and to clone it run this:

```
cd ~/Assistant
git clone https://github.com/Momwhyareyouhere/Assistant.git
```
3. Install requirements

To install requirements run this and make sure venv is activated:

```
cd ~/Assistant
pip install -r requirements.txt
```
4. Install espeak

This program requires espeak to install it run:

```
sudo apt install espeak-ng
```

On arch linux:

```
sudo pacman -S espeak-ng
```

5. Run it

After you did all the requirements you can now run the program:

```
python3 app.py voice 2>/dev/null
```

for the keyboard version:

```
python3 app.py keyboard
```
OPTIONAL

This step is optional

If you want to make this a autostart program do this:

1. Chmod the files

You need to chmod the files so that the program can work:

```
cd ~/Assistant
chmod +x assistant-keyboard
chmod +x assistant
```

2. Move them to /usr/bin/

You need to move them to /usr/bin/ so they will work as commands:

```
sudo mv assistant-keyboard /usr/bin/
sudo mv assistant /usr/bin/
```
3. Create a autostart

Now you created the two commands you can now do the autostart:

```
cd ~/Assistant
sudo mv assistant.desktop ~/.config/autostart/
```

Now you are done to test it reboot you system and say assistant
