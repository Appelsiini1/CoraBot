# CoraBot

[![Deployment](https://github.com/Appelsiini1/CoraBot/actions/workflows/main.yml/badge.svg)](https://github.com/Appelsiini1/CoraBot/actions/workflows/main.yml)

A Discord bot.

This Discord bot is a fun little side project to see what kinds of cool stuff I can make in Python & Discord.

## Current Features:

### The bot's command prefix is `!c` and must be always used when directly interacting with the bot.

* Inspire
Get an inspring quote from a famous person.
Usage: `!c inspire`

* Insult
Insult someone! You can choose to tag them or not.
Usage: `!c insult \[user]`

* F
Pay your respects.
Usage: `!c f` or `!c F`

* Choose
Helps you choose between options you give.
Usage: `!c \[option1] | \[option2] ...`


* Vaccine statistics
Get the current number of vaccinated people in Finland. First and second dose shown separately. Area codes can be spesified to view the statistics for a certain area.
Uses the API from Finnish Institute for Health and Welfare (thl.fi)
Usage: `!c vacc \[Area code or empty for all areas | help]`

* Polling!
The polling feature has two different polls: basic polls and advanced polls. They differ most by their voting method. Basic are voted by reacting to an emoji that corresponds to the emoji shown next to the option.
Advanced polls are voted by using the `!c vote` command. The voting is anonymous and the server admins may spesify how many votes each role has. For example, one role could have one vote, while a higher role could have two or three. Multiple votes can be spread out to different options.
Both polls can have a maximum of 20 options. For all the info, see `!c poll help`.
Usage: `!c poll new \[-r] ...`
Usage: `!c poll end \[Poll ID]`
Usage: `!c vote \[Poll ID] \[option:votes], \[option:votes], ...`

* Digital bubblewrap!
Pop digital bubblewrap straight in your Discord client!
Usage: `!c pop \[number between 1-14]`

* Dice rolling!
Roll all kinds of dice with this command!
For all the options and explanations, see `!c dice help`
Usage: `!c dice \[help | \[N]dS | \[N]wS | \[N]uS]`

* Giveaways!
Initiate and end giveaways easily!
Entry to the giveaway is via reaction to the correct emoji on the giveaway message.
Usage: `!c giveaway`