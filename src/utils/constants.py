from src.services.tax import TaxService
from src.services.slot_machine import SlotMachineService


class Constants():

    """
    Handles the constant variables in embeds -> Bank, wallet, Coin

    :Attributes: 

    BANK -> `**Bank 🏛**`
    WALLET -> `**Wallet 💰**`
    COIN-> `Main Coin <:Coin_Tails:1340802182705840149>`
    COIN_HEADS -> `<:Coin_Heads:1340802116565995652>`
    Coin_TAILS -> `<:Coin_Tails:1340802182705840149>`
    WORK_REPLIES -> A list of possible work replies 
    CRIME_REPLIES -> A list of possible crime replies
    SLOT_EMOJI -> The emoji of spin button in game jackbot
    SLOT_TEERS -> Icons of slot machine game
    """

    BOT_STATUS = ["/help", f"/jackbot", f"https://tiktok.com/@yggdrasil0707/"]

    # Economy constants
    BANK = '**Bank 🏛**'
    WALLET = '**Wallet 💰**'
    COIN = '<:Coin_Tails:1341570864507785366>' # Used as Main Currency view ex: **Wallet 💰** : 50 🌳
    COIN_HEAD = '<:Coin_Heads:1341570827660820561>'
    COIN_TAILS = '<:Coin_Tails:1341570864507785366>'

    # Activity replies
    WORK_REPLIES = [
        "You have collected eggs",
        "You have chopped wood",
        "You have delivered the mail",
        "You have cleaned the stable",
        "You have fished in the river",
        "You have harvested crops",
        "You have brewed coffee",
        "You have painted the fence",
        "You have repaired the roof",
        "You have baked bread",
        "You have washed the dishes",
        "You have built a chair",
        "You have harvested honey",
        "You have polished the floors",
        "You have watered the garden",
        "You have fed the animals",
        "You have cleaned the windows",
        "You have sorted the mail",
        "You have crafted a table",
        "You have fixed the car",
        "You have dug a well",
        "You have collected",
        "You have painted",
        "You have cleaned the barn",
        "You have harvested berries",
        "You have crafted a basket",
        "You have swept the floors",
        "You have built a fence",
        "You have stitched a blanket",
        "You have repaired the wagon",
        "You have collected herbs",
        "You have watered the plants",
        "You have made a lantern",
        "You have cleaned the garden",
        "You have gathered mushrooms",
        "You have harvested vegetables",
        "You have baked a cake",
        "You have mended clothes",
        "You have fixed the fence",
        "You have picked fruit",
        "You haven't do anything but still get a Paycheck"
    ]
    CRIME_REPLIES = [
        "You\'ve swapped the sugar for salt in the coffee shop",
        "You\'ve taken the last piece of cake from the party",
        "You\'ve left a trail of breadcrumbs leading right to you",
        "You\'ve \'borrowed\' a neighbor\'s lawn chair for a quick nap",
        "You\'ve pulled the old whoopee cushion trick at a formal dinner",
        "You\'ve swapped all the pencils for pens in the office drawer",
        "You\'ve sneaked a peek at someone\'s phone while they were texting",
        "You\'ve eaten all the ice cream from the freezer",
        "You\'ve glued someone\'s shoes to the floor",
        "You\'ve \'accidentally\' swapped someone\'s shampoo with conditioner",
        "You\'ve left a trail of glitter wherever you go",
        "You\'ve locked someone\'s car keys in their car",
        "You\'ve secretly switched all the TV channels to the home shopping network",
        "You\'ve \'accidentally\' spilled water all over the library books",
        "You\'ve stolen the last slice of pizza from the pizza box",
        "You\'ve hidden the TV remote and are now on the run",
        "You\'ve scribbled on someone\'s homework and blamed the dog",
        "You\'ve stuffed a bunch of balloons in someone\'s closet",
        "You\'ve taken a handful of cookies and left nothing but crumbs",
        "You\'ve put a tack on the chair in the meeting room",
        "You\'ve switched all the street signs around the block",
        "You\'ve borrowed someone\'s umbrella and forgotten to return it",
        "You\'ve swapped all the ketchup for mustard in the fridge",
        "You\'ve eaten the last cookie and left the crumbs behind",
        "You\'ve hidden all the spoons in the kitchen drawers",
        "You\'ve \'accidentally\' spilled coffee on someone\'s favorite book",
        "You\'ve sneaked into the movie theater with a full picnic",
        "You\'ve rearranged the furniture just to confuse everyone",
        "You\'ve taken all the Wi-Fi passwords and won\'t share them",
        "You\'ve left a trail of banana peels all over the street",
        "You\'ve \'borrowed\' someone\'s hat and worn it for a week",
        "You\'ve put toothpaste in someone\'s shoes",
        "You\'ve switched out all the signs in the grocery store for the wrong products",
        "You\'ve taken all the batteries out of the remote and hidden them.",
        "You\'ve hidden all the socks from the laundry basket",
        "You\'ve switched the labels on all the jars in the pantry",
        "You\'ve swapped the sugar with the salt in the baking cupboard",
        "You\'ve eaten all the chips and left the empty bag in the pantry",
        "You\'ve secretly set all the clocks in the house an hour forward",
        "You\'ve taped a \'kick me\' sign to someone\'s back without them noticing",
    ]

    # Jacbot emojies
    SLOT_EMOJI = "<:Slot_machine:1341826020902310070>"
    SLOT_TEERS= [
        "<:slot1:1341814840976736370>",
        "<:slot2:1341814864246472745>",
        "<:slot3:1341814881258700902>",
        "<:slot4:1341814899017515068>",
        "<:slot5:1341814918919491605>",
        "<:slot6:1341814938494046311>",
        "<:slot7:1341814959562035200>",
        "<:slot8:1341814981405966418>",
        "<:slot9:1341815007381557339>",
        "<:slot10:1341815028998864937>",
        "<:slot11:1341815052524716264>",
        "<:slot12:1341815082103078912>",
        "<:slot13:1341815106979496016>",
        "<:slot14:1341815138218541157>",
        "<:slot15:1341815167754698793>",
        "<:slot16:1341815192790630420>",
        "<:slot17:1341815225204211773>",
        "<:slot18:1341815244191694848>",
        "<:slot19:1341815264660029450>",
        "<:slot20:1341815291226882119>",
    ]

    SHOP = {
        "5000 - 5K": ["Get the 5k role and gain 1% of the money in your bank as income", 5000, 0.01],
        "50000 - 50K": ["Get the 50k role and gain 2% of the money in your bank as income", 50000, 0.02],
        "100000 - 100K": ["Get the 100K role and gain 5% of the money in your bank as income", 10000, 0.05],
        "500000 - 500K": ["Get the 500k role and gain 7% of the money in your bank as income", 50000, 0.07],
        "1000000 - 1M": ["Get the 1M role and gain 15% of the money in your bank as income", 100000, 0.15],
        "Ramadan Kareem": ["Exclusive role and only avavilable in month of Ramadan and it give you 10% of the money in your bank as income for only **20,000 credits**", 20000, 0.1],
    }
