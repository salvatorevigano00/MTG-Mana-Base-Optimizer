import json
import csv
import re

class MTGJSONParser:
    def __init__(self, input_filepath: str, output_filepath: str):
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath
        self.mana_regex = re.compile(r'\{(.*?)\}')

    def parse_mana_cost(self, mana_cost: str) -> dict:
        mana_dict = {'genericMana': 0, 'manaW': 0, 'manaU': 0, 'manaB': 0, 'manaR': 0, 'manaG': 0, 'manaC': 0}
        if not mana_cost: return mana_dict
        
        for symbol in self.mana_regex.findall(mana_cost):
            if symbol.isdigit(): mana_dict['genericMana'] += int(symbol)
            else:
                key = f"mana{symbol}"
                if key in mana_dict: mana_dict[key] += 1
        return mana_dict

    def deduce_enter_rule(self, text: str, supertypes: list) -> str:
        if not text: text = ""
        text_lower = text.lower()
        if "Basic" in supertypes: return "untapped"
        if "enters the battlefield tapped unless" in text_lower or "pay 2 life" in text_lower: return "conditional_tapped"
        if "enters the battlefield tapped" in text_lower: return "always_tapped"
        return "untapped"

    def deduce_produced_mana(self, card: dict) -> str:
        if card.get('producedMana'): return ", ".join(card.get('producedMana', []))
        
        mana_map = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}
        produced = [mana_map[sub] for sub in card.get('subtypes', []) if sub in mana_map]
        if produced: return ", ".join(produced)
        
        valid = [m for m in self.mana_regex.findall(card.get('text', '')) if m in ['W', 'U', 'B', 'R', 'G', 'C']]
        if valid: return ", ".join(list(set(valid)))
        return "None"

    def get_italian_name(self, foreign_data: list) -> str:
        for entry in foreign_data:
            if entry.get("language") == "Italian": return entry.get("name", "")
        return ""

    def process_card(self, set_code: str, card: dict) -> dict:
        mana_cost = card.get('manaCost', '')
        parsed = self.parse_mana_cost(mana_cost)
        return {
            'Set': set_code,
            'Nome_ENG': card.get('name', ''),
            'Nome_ITA': self.get_italian_name(card.get('foreignData', [])),
            'Costo_Originale': mana_cost,
            'Costo_Generico': parsed['genericMana'],
            'Mana_W': parsed['manaW'],
            'Mana_U': parsed['manaU'],
            'Mana_B': parsed['manaB'],
            'Mana_R': parsed['manaR'],
            'Mana_G': parsed['manaG'],
            'Mana_C': parsed['manaC'],
            'CMC': int(card.get('manaValue', 0)),
            'Tipo_Pulito': ", ".join(card.get('types', [])),
            'Sottotipi': ", ".join(card.get('subtypes', [])),
            'Layout': card.get('layout', 'normal'),
            'Colori': ", ".join(card.get('colors', [])),
            'Mana_Prodotto': self.deduce_produced_mana(card),
            'Regola_Ingresso': self.deduce_enter_rule(card.get('text', ''), card.get('supertypes', []))
        }

    def run(self):
        try:
            with open(self.input_filepath, 'r', encoding='utf-8') as f: data = json.load(f)
        except FileNotFoundError:
            print(f"Could not find {self.input_filepath}.")
            return

        extracted_cards = []
        for set_code, set_data in data.get("data", data).items():
            for card in set_data.get('cards', []):
                extracted_cards.append(self.process_card(set_code, card))

        with open(self.output_filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=extracted_cards[0].keys())
            writer.writeheader()
            writer.writerows(extracted_cards)
        print("Database ready for use. All cards have been processed and saved to CSV.")