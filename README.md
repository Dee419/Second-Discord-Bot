# Dee's Discord Bot: CatBot
This is my second attempt at making a Discord bot in Python.

### Features
- Kick, Ban and Warn system
- Chat logging
- Simple purge command
- Database written in JSON
- Several fun commands
- Role reactions

### Requirements
- Python 3.8 or Higher
- discord.py 1.7.3 or lower (1.7.3 recommended)

### Installation
1. Clone this repository to the desired folder
   ```cmd
   git clone https://github.com/Dee419/Second-Discord-Bot
   ```
2. Put your bot's token in `token.txt`

3. Run CatBot.py
   - Windows terminal
   ```cmd
   python CatBot.py
   ```
   - Linux terminal
   ```bash
   python3 CatBot.py
   ```

### Commands:
1. Moderation commands
   - Kick
     - Allows the user to kick a member
     - Usage: `.kick Member-Mention/User-ID (Optional)Reason`
     - Example: `.kick 206398035654213633 Toxic Behaviour`
   - Ban
     - Allows the user to ban a user
     - The user in question does not need to be on the serve
     - Usage: `.ban Member-Mention/User-ID (Optional)Reason`
     - Example: `.ban 206398035654213633 Hate Speech`
   - Warn
     - Allows the user to warn a member
     - Usage: `.kick Member-Mention/User-ID (Optional)Reason`
     - Example: `.warn 206398035654213633 Suggestive Image`
   - Purge
     - Allows the user to purge a given amount of messages
     - You can also choose whose messages are to be purged
     - Usage: `.purge Amount-Of-Messages User-ID`
     - Example: `.purge 10 206398035654213633`
2. Admin commands
   - Add server to database
     - Allows the user to add the server to the database in case the server is not currently in the database
     - Aliases: `.astdb`, `.addservertodb`
     - Usage: `.addservertodatabase`
   - Set chat log channel
     - Allows the user to set the chat log channel
     - Either provide the channel or use in the intended channel
     - Usage: `.setchatlogchannel (Optional)Channel_ID`
     - Examples: `.setchatlogchannel 988180984337928212`, `.setchatlogchannel`
3. Role Reactions
   - Setup for **adding** a role reaction
     - Starts the setup for **adding** a role reaction message.
     - Start by providing the message id
     - Usage: `.rmsetup Message-ID`
     - Example: `.rmsetup 1012345674341298186`
   - Setup for **removing** a role reaction
     - Starts the **removal** for a role reaction message
     - Start by providing the message id
     - Usage: `.rmremove Message-ID`
     - Example: `.rmremove 1012346042072703037`
4. Fun Commands
   - Cat
     - Allows the user to get a random cat image
     - Usage: `.cat`
   - Misery
     - *Every single person is my enemy~*
     - Usage: `.misery`
   - Pet
     - Pets CatBot :)
     - Usage: `.pet`
   - Rock Paper Scissors
     - Allows the user to play Rock Paper Scissors against the bot
     - Usage: `.misery`
