from discord.ext import commands
from discord import app_commands
import discord

import json

TEST_MODE = True
# when enabled, instead of sgt.cat everything will go to buzz

TOKEN = "MTEzODkxODMzMjAxNjM3Nzk1OQ.GFPtj2.yJx37uEUW_gvm1M0vftV56VJV3l5AXUfvGFyOU"
LEADERBOARD_CHANNEL = 1088591989106286612
DATABASE_FILE = "database.json"

if not TEST_MODE:
    REQUEST_CHANNEL = 987862177266405397
else:
    REQUEST_CHANNEL = 203269515981750279


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

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
    print("All set, sir.")

@bot.tree.command(name="balance", description="Check your cat buck balance")
async def balance(interaction):
    check_user_existance(interaction.user.id)
    database = read_database()

    await interaction.response.send_message(f"Your balance is {database['users'][str(interaction.user.id)]['balance']}")

@bot.tree.command(name="pay", description="Add funds to a user")
async def pay(interaction, amount:int, user:discord.User):
    
    check_user_existance(user.id)
    database = read_database() 

    database["users"][str(user.id)]["balance"] += amount
    save_database(database)

    await interaction.response.send_message(f"You paid <@{user.id}> {amount} cat bucks, their balance is now {database['users'][str(user.id)]['balance']}")

@bot.tree.command(name="request", description="Request to spend your bucks for sgt.cat to do something")
async def request(interaction, request:str):
    if "@everyone" in request:
        interaction.response.send_message("you can't @ everyone stupid",ephemeral=True)


    view = CostSelector()
    view.originalRequester = interaction.user
    view.requestName = request

    channel = await bot.fetch_user(REQUEST_CHANNEL)
    await channel.send(f"<@987862177266405397> i need you, <@{interaction.user.id}> has requested {request}, how many bucks do you want for it?", view=view)
    await interaction.response.send_message("Alright, i'll ask sgt.cat and DM you when a cost is picked")

@bot.tree.command(name="database", description="read the database")
async def database(interaction):
    await interaction.response.send_message(str(read_database()))

@bot.tree.command(name="backup",description="create a database backup")
async def backup(interaction, filename:str):
    save_database(read_database(),filename)
    await interaction.response.send_message(f"A database backup has been created with the filename {filename}")


def check_user_existance(userid:int):
    database = read_database()

    if str(userid) in database["users"].keys():
        return
    
    print("New user! creating entry")

    database["users"][str(userid)] = {"balance":0}

    save_database(database)

def save_database(database, filename=DATABASE_FILE):
    print("Saving database... do not close")
    with open(filename, 'w') as openfile:
        json.dump(database,openfile, indent=3)
    print("Database save complete")

def read_database():
    try:
        with open(DATABASE_FILE, 'r') as openfile:
            database = json.load(openfile)
            print(database)
    except FileNotFoundError:
        print("Database file does not exist!! If updating your bot version, please move the old DATABASE_FILE file to the new folder, otherwise if you want to make a new file type y")
        if input("create new file?") == "y":
            with open(DATABASE_FILE, 'x') as openfile:
                database = {"users":{}}
                json.dump(database,openfile)
                print("New file created")
        else:
            print("Exiting")
            exit()
    
    print(f"rd database {database}")
    return database

class CostSelector(discord.ui.View):
    originalRequester = None
    requestName = "undefined"

    def __init__(self):
        super().__init__(timeout=None) # make the button last forever, even when meowmer is dead

    @discord.ui.select(
        placeholder = "Pick Cost", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
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
        if not select.values[0] == "Reject":
            view = CostAcceptor()
            view.cost = int(select.values[0])
            view.originalRequester = self.originalRequester
            view.requestName = self.requestName

            await self.originalRequester.send(f"Sgt.cat decided that your request {self.requestName} would cost {select.values[0]}, do you accept?", view=view)
        else:
            await self.originalRequester.send(f"he rejected {self.requestName} lmao cope")


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
        await interaction.response.edit_message(content=f"Alright! i'll take {self.cost} cat bucks from you now, and sgt.cat will get right on it", view=None)

        database["users"][str(self.originalRequester.id)]["balance"] -= self.cost
        save_database(database)

        channel = await bot.fetch_user(REQUEST_CHANNEL)
        await channel.send(f"<@{self.originalRequester.id}> accepted {self.requestName} for {self.cost}, get on it!")

print("Testing database")
read_database()

bot.run(TOKEN)