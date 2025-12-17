# Assistant

Recently I noticed that there are Assistants for phones but not for Desktop Users so I made this Assistant for Desktop Users Its open source and you can add you own commands.

To put you own commands just go to commands.txt put you own command and then go to app.py make you own function and thats it you have you own custom command.

There are also prebuilt commands for Linux Users and here is how to make it:

2. Clone the repository

To do that you need to have git installed on you system and to clone it run this:

```
cd ~
git clone https://github.com/Momwhyareyouhere/Assistant.git
```

4. Run the installation

After you did all the steps you can now install it by running this command:
```
cd ~/Assistant
chmod +x install.sh
./install.sh
```
If the command wont work try to install espeak-ng on you system:
```
sudo apt install espeak-ng
```
on arch linux:
```
sudo pacman -S espeak-ng
```
