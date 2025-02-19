import json
from paths import SERVICES_DIR


jackbot_file_path = SERVICES_DIR / "jackbot.json"
jackbot_default = {"prize_pool": 10000}

class SlotMachineService:

    @staticmethod
    def create_jackbot_file_if_not_exist() -> None:
        if jackbot_file_path.exists():
            return
        SlotMachineService.update_jackbot_file(jackbot_default)
    
    @staticmethod
    def load_jackbot_file() -> dict:
        with open(jackbot_file_path, 'r') as f:
            return json.loads(f.read())
    
    @staticmethod
    def get_jackbot_prize() -> int:
        SlotMachineService.create_jackbot_file_if_not_exist()
        data = SlotMachineService.load_jackbot_file()
        return data.get("prize_pool")

    @staticmethod
    def update_jackbot_file(data: dict) -> None:
        with open(jackbot_file_path, 'w') as f:
            json.dump(data, f)
    
    @staticmethod
    def update_jackbot_prize(new_jackbot_prize: int) -> None:
        data = SlotMachineService.load_jackbot_file()
        data["prize_pool"] = new_jackbot_prize
        SlotMachineService.update_jackbot_file(data)
