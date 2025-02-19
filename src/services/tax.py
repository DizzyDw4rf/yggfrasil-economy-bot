import json
from paths import ROOT_DIR

tax_file_path = ROOT_DIR / "tax.json"
default_tax_rate = {"tax_rate": 0.02}

class TaxService:

    @staticmethod
    def create_tax_file_if_not_exist() -> None:
        if tax_file_path.exists():
            return
        TaxService.update_tax_file(default_tax_rate)
    
    @staticmethod
    def load_tax_file() -> dict:
        with open(tax_file_path, 'r') as f:
            return json.loads(f.read())
    
    @staticmethod
    def get_tax_rate() -> float:
        TaxService.create_tax_file_if_not_exist()
        data = TaxService.load_tax_file()
        return data.get("tax_rate")
    
    @staticmethod
    def update_tax_file(data: dict) -> None:
        with open(tax_file_path, 'w') as f:
            json.dump(data, f)
    
    @staticmethod
    def update_new_tax_rate(new_tax_rate) -> None:
        data = TaxService.load_tax_file()
        data["tax_rate"] = new_tax_rate
        TaxService.update_tax_file(data)
