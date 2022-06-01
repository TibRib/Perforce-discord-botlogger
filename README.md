# Perforce Discord Submit logger 📫
A simple python program to use with a scheduler that will notify a provided discord channel when changes have been submitted to a perforce repository

# Requirements
The app is a python script that uses the [p4 changes](https://www.perforce.com/manuals/cmdref/Content/CmdRef/p4_changes.html) command, you need to make sure you have a constant access to `p4 changes`.
You can try to run ```p4 changes -m 1``` to see if you are connected.
### Requirements: [Helix Command-Line Client](https://www.perforce.com/products/helix-core-apps/command-line-client)

## Loggin with p4 (powershell)
The oneliner solution to login to your perforce user, once your perforce is setup globally is to run

```echo PASSWORD|p4 -u USER login```
## Suggestion regarding the login
I recommend creating a batch file (if on windows) (use a bash script on unix) to login.

For instance, I created a `p4login.bat` file containing the following:

```batch
@echo off
Powershell.exe -windowstyle hidden -ExecutionPolicy Unrestricted -command "echo PASSWORD|p4 -u USER login"
```
After that, [add a task to your Windows Scheduler](https://digicruncher.com/task-scheduler-in-windows-10/) to run this batch program on startup and every hour.

## Python requirements
Make sure to run
```
cd app
pip install -r requirements.txt
``` 
before first running the program (python3 required of course).

# Configuration
You need to configure some options declared in the `config.ini` file:
```ini
[Discord]
webhook = YOUR_WEBHOOK_URL_HERE

[Perforce]
#Suggestion : set target to empty for a root changelist
target = //MY_FOLDER/...

[ApplicationSettings]
max_changes = 10
enable_signature = yes
```

## Set the changelist last stamp
As the bot is likely to be used on an already existing perforce environment, you need to change the value in the file ```last_change.ini```. Replace 0 with the latest change number.

Once the bot runs, this file will be updated every time a newer submit is found.
### Exemple:
I get the latest change on my perforce server.
```css
C:\Users\Me> p4 changes -m 1
Change 139208 on 2022/06/01 by someone@MY_LAPTOP 'new feature'
```
The number can now be written to the ini, by opening the file in your text editor or using a terminal.
```sh
echo 139208 > app/last_change.ini
```

## Extras
If you want to use custom bot signatures, make sure that `enable_signature=yes` in the configuration ini file, and modify the content of the `bot_signatures.json` file.
```json
[
    "Provided by the perforce bot 😇",
    "From your favorite bot 😎",
    "Have a nice day ! 🌞"
]
```
# Automated run (Schedule)
Same as for my tip on the loggin, if you are on Windows (use a cron in unix),
1. Create a batch file : (one is provided in the repository)
    ```batch
    @echo off
    python "path\to\bot\folder\app.py"
    exit
    ```
2. Add a task to your [Windows Scheduler](https://digicruncher.com/task-scheduler-in-windows-10/) to run this batch program every 5/10 minutes.
3. That's all ! 

## Notes
- ARM64 is not supported by helix perforce. Given that, a raspberry type dedicated server **cannot** be used to host this bot...
- This bot is well suited for a dedicated python server on cloud instances (AWS, Azure, Google Cloud...)