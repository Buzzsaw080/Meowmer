from discord.ext import commands
from discord import app_commands
import discord

from random import randint, choice
import json

CIRCULATION_LIMIT = 100
TEST_MODE = True
# when enabled, instead of sgt.cat everything will go to buzz
# Startup -----------------------------------------------------------------

DATABASE_FILE = "database.json"

if not TEST_MODE:
    REQUEST_CHANNEL = 987862177266405397
    LEADERBOARD_CHANNEL = 1142215406149447751

    with open("token.txt") as file:
        TOKEN = file.read()
else:
    from time import sleep

    print("====== !! TESTING MODE !! ======")
    print("Meowmer is currently in testing mode, if you dont want this, make sure you are pulling from the main branch")
    print("TESTING MODE WILL STOP NORMAL OPERATION!!!")
    sleep(1)
    REQUEST_CHANNEL = 203269515981750279
    LEADERBOARD_CHANNEL = 1141924571784675421

    with open("testingtoken.txt") as file:
        TOKEN = file.read()


intents = discord.Intents.none()

logo = [
    "MMMMMMMMMEEEEEEEOOOOOOOOWWWWWWWWWMMMMMMMMMEEEEEEERRRRRRRRR",
    "M██MMM██ME█████EOO████OOW█WWWWW█WM██MMM██ME█████ER██████RR",
    "M█M█M█M█ME█EEEEEO█OOOO█OW█WW█WW█WM█M█M█M█ME█EEEEER█RRRRR█R",
    "M█MM█MM█ME█████EO█OOOO█OW█WW█WW█WM█MM█MM█ME█████ER██████RR",
    "M█MMMMM█ME█EEEEEO█OOOO█OW█WW█WW█WM█MMMMM█ME█EEEEER█R█RRRRR",
    "M█MMMMM█ME█EEEEEO█OOOO█OW█W█W█W█WM█MMMMM█ME█EEEEER█RR█RRRR",
    "M█MMMMM█ME█████EOO████OOW██WWW██WM█MMMMM█ME█████ER█RRR█RRR",
    "MMMMMMMMMEEEEEEEOOOOOOOOWWWWWWWWWMMMMMMMMMEEEEEEERRRRRRRRR"
]

for i in logo:
    print(i)

bot = commands.Bot(command_prefix="$",intents=intents)

@bot.event
async def on_ready():
    print("Connected to discord")

    print("Syncing bot commands")
    await bot.tree.sync()

    await update_leaderboard()

    print("All set, sir.")
# Commands ------------------------------------------------------------------------------------

# Balance command -----------------
@bot.tree.command(name="balance", description="Check your cat buck balance")
async def balance(interaction):
    check_user_existance(interaction.user.id)
    balance = get_user_balance(interaction.user.id)

    await interaction.response.send_message(f"Your balance is {balance}")

# Say command ---------------------
@bot.tree.command(name="say", description="Make me say anything")
async def say(interaction, words:str):
    if (interaction.user.id != 987862177266405397 and interaction.user.id != 203269515981750279):
        await interaction.response.send_message("kys (keep yourself safe) NOW!", ephemeral=True)
        return # Buzz wtf is this and who is it attached to? o-O

    await interaction.response.send_message("okay", ephemeral=True)
    await interaction.channel.send(words)

#Pay command ----------------------
@bot.tree.command(name="pay", description="Give funds to a user")
async def pay(interaction, amount:int, user:discord.User):
    check_user_existance(user.id)
    check_user_existance(interaction.user.id)

    # Negative cash response/math
    if (interaction.user.id != REQUEST_CHANNEL):
        if amount < 0:
            await interaction.response.send_message("uhm, that would be robbery. you dont want to go to jail do you?")
            return
        # Have cash response/math
        if get_user_balance(interaction.user.id) >= amount: # Not enough money math. see response2
            transfer_user_funds(user.id,amount,sender=interaction.user.id)

            await interaction.response.send_message(f"You sent {amount}$ to <@{user.id}> they now have {get_user_balance(user.id)}$ and you have {get_user_balance(interaction.user.id)}$") # Response1 ---
        else: # Not enough cash response
            await interaction.response.send_message(f"You're too BROKE to send {amount}$, you only have {database['users'][str(interaction.user.id)]['balance']}$ silly") # Response2
            return        
    else: # God gives money response/math
        
        transfer_user_funds(user.id,amount) # Adding money from god. see response3
        
        await interaction.response.send_message(f"You sent {amount}$ to <@{user.id}> they now have {get_user_balance(user.id)}$ (no money was taken because you own the system)")


# Request command --------------------
@bot.tree.command(name="request", description="Request to spend your bucks for Sgt.Cat to do something")
async def request(interaction, request:str):
    if "@everyone" in request:
        interaction.response.send_message("you can't @ everyone D:",ephemeral=True)

    # Behind the scenes
    view = CostSelector()
    view.originalRequester = interaction.user # The person who requested
    view.requestName = request # Defining/Grabbing the request
    # Action
    channel = await bot.fetch_user(REQUEST_CHANNEL)
    await channel.send(f"<@987862177266405397> i need you, <@{interaction.user.id}> has requested {request}. How many big fat sexy bucks do you want for it? ;3", view=view) # Messaging Sgt.Cat
    await interaction.response.send_message("Alright, i'll ask Sgt.Cat and DM you when he picks a price") # Letting the user know Sgt Cat has been messaged
 
# Database command -------------------
@bot.tree.command(name="database", description="read the database")
async def database(interaction):
    await interaction.response.send_message(str(read_database())) # Reads the database

#Backup command ----------------------
@bot.tree.command(name="backup",description="create a database backup")
async def backup(interaction, filename:str):
    save_database(read_database(),filename)
    await interaction.response.send_message(f"A database backup has been created with the filename {filename}")

# Updating the leaderboard duh --------------------------------------------------
async def update_leaderboard(): # Loop start
    print("Updating leaderboard...")

    database = read_database()
    userlist = []
    total = 0
    for userid in database["users"].keys():
        user = await bot.fetch_user(userid)
        username = user.display_name
        total += get_user_balance(userid)
        userlist.append([username, get_user_balance(userid)])

    nlist = userlist
    # bro probably did not fix this :skull: and if he did he forgot to remove the messsage
    # i didnt :( - Buzz
    for passnum in range(len(nlist)-1,0,-1):
        for i in range(passnum):
            if nlist[i][1]>nlist[i+1][1]:
                temp = nlist[i]
                nlist[i] = nlist[i+1]
                nlist[i+1] = temp
    
    nlist.reverse()
    leaderboard = f"# Leaderboard\nTotal - {total}/{CIRCULATION_LIMIT} "
    if total >= CIRCULATION_LIMIT:
        leaderboard += "⚠️"

    leaderboard += "\n\n"
    
    for index, user in enumerate(nlist):
        if user[1] != 0:
            leaderboard += f"#{index + 1} {user[0]} - {user[1]}$\n"
        total += user[1]

    channel = await bot.fetch_channel(LEADERBOARD_CHANNEL)
    if "leaderboardmessage" in database:
        print(database["leaderboardmessage"])
        message = await channel.fetch_message(database["leaderboardmessage"])
        await message.edit(content=leaderboard)
    else:
        print("No leaderboard message present in database, sending a new one!")
        message = await channel.send(leaderboard)
        database["leaderboardmessage"] = message.id
        save_database(database)



#TODO: make opponent optional, so you can make a public challenge
@bot.tree.command(name="coinflip",description="Challenge someone to a coinflip")
async def requestcoinflip(interaction,stakes:int,opponent:discord.User):
    await make_gambling_challenge(interaction,opponent,stakes,"a coin flip",coinflip)

@bot.tree.command(name="blackjack",description="Challenge someone to blackjack")
async def requestblackjack(interaction,stakes:int,opponent:discord.User):
    await make_gambling_challenge(interaction,opponent,stakes,"blackjack",blackjack)

@bot.tree.command(name="blowjob",description="uhh")
async def blowjob(interaction):
    check_user_existance(interaction.user.id)

    reactions = ["ohh yeahhh","*moans*","soo goood","yess daddy","😫","keep going bbg"]
    database = read_database()

    try:
        database["users"][str(interaction.user.id)]["blowjobs"] += 1
    except KeyError:
        database["users"][str(interaction.user.id)]["blowjobs"] = 1

    save_database(database)
    await interaction.response.send_message(f"{choice(reactions)} (you have given meowmer {database['users'][str(interaction.user.id)]['blowjobs']} blowjobs)")

# Checking for existence of a user -----------
def check_user_existance(userid:int):
    database = read_database()

    if str(userid) in database["users"].keys():
        return
    
    print("New user! creating entry")

    database["users"][str(userid)] = {"balance":0, "blowjobs":0}

    save_database(database)

async def make_gambling_challenge(interaction,opponent,stakes,name,callback):
    check_user_existance(interaction.user.id)
    check_user_existance(opponent.id)

    if stakes < 0: # negative numbers aren't alive (0 stakes are though)
        await interaction.response.send_message("uhhh... nuh uh", ephemeral=True)
        return False
    elif get_user_balance(interaction.user.id) < stakes: # if you can't afford it, dont let you make a challenge
        await interaction.response.send_message(f"sorry buddy, i can't hand out loans for gambling, and you only have {get_user_balance(interaction.user.id)}$",ephemeral=True)
        return False
    elif get_user_balance(opponent.id) < stakes: # if they can't afford it, dont let you make a challenge
        await interaction.response.send_message(f"your opponent is too broke for the stakes you put, they only have {get_user_balance(opponent.id)}$",ephemeral=True)
        return False

    view = GamblingAcceptor()
    view.requester = interaction.user
    view.opponent = opponent
    view.callback = callback
    view.stakes = stakes
    view.gambleName = name

    await interaction.response.send_message(f"<@{opponent.id}>, <@{interaction.user.id}> is challenging you to {name}!\nstakes: {stakes}$",view=view)

    return True # if the challenge was created, return true
    # if not, it will return false

def get_user_balance(userid):
    database = read_database()
    return database["users"][str(userid)]["balance"]

def transfer_user_funds(reciever,amount,sender=None):
    database = read_database()

    if sender: # If there's a sender
        database["users"][str(sender)]["balance"] -= amount # Remove money from sender


    database["users"][str(reciever)]["balance"] += amount # Add money to reciever

    save_database(database)

# Database saving proccess ---------------------------
def save_database(database, filename=DATABASE_FILE):
    print("Saving database... do not close")
    with open(filename, 'w') as openfile:
        json.dump(database,openfile, indent=3)
    print("Database save complete")

# Database file error -----------------------
def read_database():
    try:
        with open(DATABASE_FILE, 'r') as openfile:
            database = json.load(openfile)
    except FileNotFoundError: # If database file does not exist, offer to create a new one
        print("Database file does not exist!! If updating your bot version, please move the old DATABASE_FILE file to the new folder, otherwise if you want to make a new file type y")
        if input("create new file?") == "y":
            with open(DATABASE_FILE, 'x') as openfile:
                database = {"users":{}}
                json.dump(database,openfile)
                print("New file created")
        else:
            print("Exiting")
            exit()


    return database

class GamblingAcceptor(discord.ui.View):
    requester = None
    opponent = None
    gambleName = "undefined"
    stakes = 0
    callback = None

    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="💰")
    async def accept_callback(self, interaction, button):

        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message("buddy this challenge aint for you", ephemeral=True)
            return
        
        button.disabled = True

        await interaction.response.edit_message(content=f"<@{self.opponent.id}> has accepted the {self.gambleName}",view=None)
        await self.callback(interaction,self.requester,self.opponent,self.stakes)
        
async def coinflip(interaction,requester,opponent,stakes):
    if randint(0,1) == 0:
        result = f"<@{opponent.id}> won! +{stakes}$"
        transfer_user_funds(opponent.id,stakes,requester.id)
    else:
        result = f"<@{requester.id}> won! +{stakes}$"
        transfer_user_funds(requester.id,stakes,opponent.id)

    await interaction.response.send_message(result)

async def blackjack(interaction,requester,opponent,stakes):
    game = BlackjackGame()

    game.requester = requester
    game.opponent = opponent

    game.stakes = stakes

    await game.show_game_summary(interaction)

    

class BlackjackGame(discord.ui.View):
    requester = None 
    requesterDeck = []

    opponent = None
    opponentDeck = []


    turn = 0
    overviewMessage = None
    stakes = 0
    possibleCards = [2,3,4,5,6,7,8,9,10,10,10,10] * 4

    def __init__(self):
        super().__init__(timeout=30)

    def give_starting_cards(self):
        for i in range(1,2):
            self.requesterDeck += self.draw_card()
            self.opponentDeck += self.draw_card()
        
    def draw_card(self):
        # choose random value between 0 and the length of the possible cards, then remove it from the
        # draw pile and return it
        return self.possibleCards.pop(randint(0,len(self.possibleCards) - 1))

    async def show_game_summary(self,interaction):
        embed = discord.Embed(title="Blackjack", description=f"{self.requester.display_name}'s turn", color=0xff0000)
        embed.add_field(name=f"{self.requester.display_name}'s cards", value=str(self.requesterDeck), inline=True)
        embed.add_field(name="Total", value=":)", inline=False)
        embed.add_field(name=f"{self.opponent.display_name}'s cards", value=str(self.opponentDeck), inline=False)
        embed.add_field(name="Total", value=":)", inline=False)

        if self.overviewMessage == None:
            await interaction.response.send_message("",embed=embed,view=self)
        else:
            await interaction.response.edit_message("",embed=embed,view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.red)
    async def hit(self, interaction, button):
        await interaction.response.send_message("You hit!",ephemeral=True)
        await self.show_game_summary(interaction)
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green)
    async def stand(self, interaction, button):
        if turn == 0:
            turn = 1
            await interaction.response.send_message("You stood. it is now the other player's turn",ephemeral=True)
        else:
            await interaction.response.send_message("You stood. getting winner now...",ephemeral=True)
    
    @discord.ui.button(label="Show cards", style=discord.ButtonStyle.grey)
    async def showcards(self, interaction, button):
        await interaction.response.send_message(f"Your cards: {self.requester.cards}",ephemeral=True)

# Request command button options. see request command for details
class CostSelector(discord.ui.View):
    originalRequester = None
    requestName = "undefined"

    def __init__(self):
        super().__init__(timeout=None) # make the button last forever, even when meowmer is dead
    # Sgt.Cats options for price
    @discord.ui.select(
        placeholder = "Pick Cost", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(label="Free", description="Give it to them for free"),
            discord.SelectOption(label="1"),
            discord.SelectOption(label="2"),
            discord.SelectOption(label="3"),
            discord.SelectOption(label="4"),
            discord.SelectOption(label="5"),
            discord.SelectOption(label="6"),
            discord.SelectOption(label="7"),
            discord.SelectOption(label="8"),
            discord.SelectOption(label="9"),
            discord.SelectOption(label="10"),
            discord.SelectOption(label="20"),
            discord.SelectOption(label="30"),
            discord.SelectOption(label="40"),
            discord.SelectOption(label="50"),
            discord.SelectOption(label="100"),
            discord.SelectOption(label="Reject", emoji="❌", description="Reject this request")
        ]
    )
    async def select_callback(self, interaction, select):
        select.disabled = True
        await interaction.response.edit_message(content=f"[Finished] <@{self.originalRequester.id}> requested {self.requestName} and you chose {select.values[0]}",view=None)
        if not select.values[0] in ["Reject","Free"]:
            view = CostAcceptor()
            view.cost = int(select.values[0])
            view.originalRequester = self.originalRequester
            view.requestName = self.requestName

            await self.originalRequester.send(f"Sgt.cat decided that your request {self.requestName} would cost {select.values[0]}, do you accept?", view=view)
        elif select.values[0] == "Reject":
            await self.originalRequester.send(f"he rejected {self.requestName} lmao cope")
        elif select.values[0] == "Free":
            await self.originalRequester.send(f"Sgt.cat decided to do {self.requestName} for free!... he was a little too eager though...")

class CostAcceptor(discord.ui.View):
    originalRequester = None
    requestName = "undefined"
    cost = 0

    def __init__(self):
        super().__init__(timeout=None) # make the button last forever, even when meowmer is dead

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def yes_callback(self, interaction, button):
        database = read_database()

        if database["users"][str(self.originalRequester.id)]["balance"] < self.cost:
            await interaction.response.send_message("you don't have enough money bozo", ephemeral=True)
            return

        button.disabled = True
        await interaction.response.edit_message(content=f"Alright! *yoinks {self.cost}$ cat bucks* sgt.cat will get right on it", view=None)

        database["users"][str(self.originalRequester.id)]["balance"] -= self.cost
        save_database(database)

        channel = await bot.fetch_user(REQUEST_CHANNEL)
        await channel.send(f"<@{self.originalRequester.id}> accepted {self.requestName} for {self.cost}, get on it!")

print("Testing database")
read_database()

bot.run(TOKEN)
