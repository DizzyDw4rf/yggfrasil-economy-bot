import os
from dotenv import load_dotenv


load_dotenv()

class BotStatus:

    """
    
    Class to control debug/production stat of the bot so we control which commands for public,
    and which for debug

    :Attributes:
    debug (bool): The cuurent state of the bot.

    :Methods:
    `get_server()`: returns the id of the server depending on the debug bool value.
    
    `set_debug(status: bool)`: set the stat of the bot depending on the bool value you give as param. 
    
    """

    debug = True
    
    @staticmethod
    def __debug_phase():
        """ Set the server to debug """
        server = os.getenv('GUILD_ID')
        return server
    
    @staticmethod
    def __production_phase():
        """ Set the server to production """
        server = os.getenv('GUILD_ID')
        return server

    @staticmethod
    def get_server():
        """ Returns the ID of the server """
        if BotStatus.debug:
            SERVER = BotStatus.__debug_phase()
        else:
            SERVER = BotStatus.__production_phase()
        return SERVER

    @staticmethod
    def set_debug(status: bool) -> None:
        """ 
        Set the stat of the debug to True of False depending on the status pram 
        
        :params: status: bool 
        """
        if status:
            BotStatus.debug = True
        else:
            BotStatus.debug = False

