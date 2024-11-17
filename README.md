### Setup

Use python version 3.11.6

(this was intended to bet setup on a mac, setup might look different on windows)

```bash
brew install pyenv
pyenv install 3.11.6
pyenv shell #set the current shell to version 3.11.6
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Discord setup

1. Create a new server in discord
2. Go to discord developer portal and create a New Application https://discord.com/developers/applications
3. In the `Installation` tab, check `Guild Install`, in default setting at the bottom `add the bot to the scope` and in permissions add `administrator`(it could probably be scoped down to have less permissions but since you're the owner it's fine)
4. Copy the discord provided link into your browser and install into your server, you should see in your arrivals channel that the bot got added(if you just created the server it should be in general)
5. Go into the `Bot` tab and click `Reset Token` copy the token and paste it to the .env
6. In your discord server, right click the channel and at the bottom you should see a button that says `Copy Channel ID`, grab it and paste them into your .env
   - if you don't see the option at the bottom it's likely because you need to `Enable Developer Mode` in discord.
   - You can achieve this by click the gear icon at the bottom left(User Settings) and then click on `Advanced` and enable `Developer Mode`

## Run it

You're ready to go, run it

```bash
python bot.py
```

You can also run it as a process in the background by running

```
nohup python bot.py
```

> Nohup, short for no hang up is a command in Linux systems that keep processes running even after exiting the shell or terminal. Nohup prevents the processes or jobs from receiving the SIGHUP (Signal Hang UP) signal. This is a signal that is sent to a process upon closing or exiting the terminal.

### Quick Shoutout

This repo uses [JobSpy library](https://github.com/Bunsly/JobSpy), a Jobs scraper library for LinkedIn, Indeed, Glassdoor, Google & ZipRecruiter, made possible by [@cullenwatson](https://github.com/cullenwatson) and the talented engineers at [Bunsly](https://github.com/Bunsly) so go show some love and give them a follow
