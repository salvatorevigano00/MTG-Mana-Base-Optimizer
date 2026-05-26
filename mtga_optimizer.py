import csv
import os
import time
import glob
import json
import numpy as np
from csv import DictReader

class CardDatabase:
    def __init__(self, filepath="mtg_simulator_db.csv"):
        self.db = {}
        self.load_database(filepath)

    def load_database(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for row in DictReader(f):
                    eng, ita = row['Nome_ENG'].strip().lower(), row['Nome_ITA'].strip().lower()
                    self.db[eng] = row
                    if ita: self.db[ita] = row
        except Exception: pass

    def search_card(self, name):
        return self.db.get(name.strip().lower())

class MTGAnalyzer:
    def __init__(self, db):
        self.db = db
        self.deck = []
        self.target_lands = 24
        self.archetype = "Unknown"

    @property
    def spells(self): return [c for c in self.deck if "Land" not in c['type']]

    @property
    def lands(self): return [c for c in self.deck if "Land" in c['type']]

    def add_card(self, name, copies):
        cd = self.db.search_card(name)
        if not cd: return False
        for c in self.deck:
            if c['name'].lower() == cd['Nome_ENG'].lower():
                c['copies'] += copies
                return True
        self.deck.append({'name': cd['Nome_ENG'], 'copies': copies, 'cmc': int(cd['CMC']), 'w': int(cd['Mana_W']), 'u': int(cd['Mana_U']), 'b': int(cd['Mana_B']), 'r': int(cd['Mana_R']), 'g': int(cd['Mana_G']), 'produced': cd['Mana_Prodotto'], 'rule': cd['Regola_Ingresso'], 'type': cd['Tipo_Pulito']})
        return True

    def remove_card(self, index):
        if 0 <= index < len(self.deck): self.deck.pop(index)

    def update_copies(self, index, copies):
        if 0 <= index < len(self.deck):
            if copies <= 0: self.remove_card(index)
            else: self.deck[index]['copies'] = copies

    def analyze(self):
        if not self.spells: 
            self.archetype = "Unknown"
            self.target_lands = 24
            return
        
        tot = sum(s['copies'] for s in self.spells)
        avg = sum(s['cmc'] * s['copies'] for s in self.spells) / tot if tot else 0
        
        creatures = sum(s['copies'] for s in self.spells if "Creature" in s['type'])
        instants = sum(s['copies'] for s in self.spells if "Instant" in s['type'])
        sorceries = sum(s['copies'] for s in self.spells if "Sorcery" in s['type'])
        instants_sorceries = instants + sorceries
        
        self.target_lands = max(0, 60 - tot)
        
        if avg < 2.6:
            if instants > creatures and creatures <= 12:
                self.archetype = "Tempo"
            elif instants_sorceries >= 20 and creatures <= 10:
                self.archetype = "Burn / Spellslinger"
            else:
                self.archetype = "Aggro"
                
        elif avg <= 3.2:
            if creatures <= 8:
                self.archetype = "Control"
            else:
                self.archetype = "Midrange"
                
        else:
            if creatures <= 8:
                self.archetype = "Control"
            else:
                self.archetype = "Ramp / Big Mana"

class MonteCarloSimulator:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def run(self):
        sc = sum(s['copies'] for s in self.analyzer.spells)
        dc = sum(l['copies'] for l in self.analyzer.lands)
        req = self.analyzer.target_lands - dc
        
        if req < 0: return "You've added more lands than the 60-card limit allows!"
        if self.analyzer.target_lands < 15: return "Warning: Running fewer than 15 lands is mathematically unplayable in Standard."
        
        pips = {'Plains': sum(s['w']*s['copies'] for s in self.analyzer.spells), 'Island': sum(s['u']*s['copies'] for s in self.analyzer.spells), 'Swamp': sum(s['b']*s['copies'] for s in self.analyzer.spells), 'Mountain': sum(s['r']*s['copies'] for s in self.analyzer.spells), 'Forest': sum(s['g']*s['copies'] for s in self.analyzer.spells)}
        tot = sum(pips.values())
        if tot == 0: return "Looks like your spells don't require any colored mana."
        
        dist, rem = {}, req
        for k, v in pips.items():
            if v > 0:
                q = round((v / tot) * req)
                dist[k], rem = q, rem - q
        if rem != 0 and dist: dist[max(pips, key=pips.get)] += rem

        deck_size = sc + self.analyzer.target_lands
        lands_tot = self.analyzer.target_lands
        iters = 100000

        cards_seen = 11 if self.analyzer.archetype == "Control" else 10
        target = 4 if self.analyzer.archetype == "Control" else 3
        
        drawn_lands = np.random.hypergeometric(lands_tot, deck_size - lands_tot, cards_seen, iters)
        real_score = (np.sum(drawn_lands >= target) / iters) * 100

        return {
            "archetype": self.analyzer.archetype,
            "target_total_lands": self.analyzer.target_lands,
            "duals_added": dc,
            "bases": dist, 
            "spells": sc, 
            "score": round(real_score, 2)
        }
    
class AppCLI:
    def __init__(self):
        self.db = CardDatabase()
        self.analyzer = MTGAnalyzer(self.db)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_menu(self):
        spells_count = sum(s['copies'] for s in self.analyzer.spells)
        lands_count = sum(l['copies'] for l in self.analyzer.lands)
        
        print("+" + "-"*56 + "+")
        print("|" + "MTG MANA BASE OPTIMIZER".center(56) + "|")
        print("+" + "-"*56 + "+")
        print(f"| Deck: {spells_count} Spells | {lands_count} Dual/Special Lands".ljust(57) + "|")
        print(f"| Archetype: {self.analyzer.archetype} (Target: {self.analyzer.target_lands} Lands)".ljust(57) + "|")
        print("+" + "-"*56 + "+")
        print("| 1. Add a card manually                                 |")
        print("| 2. Import from a text file (.txt)                      |")
        print("| 3. Manage current deck                                 |")
        print("| 4. Analyze archetype & calculate total lands           |")
        print("| 5. Calculate optimal basic lands & Export              |")
        print("| 6. Reset current deck                                  |")
        print("| 7. Exit                                                |")
        print("+" + "-"*56 + "+")

    def run(self):
        while True:
            self.clear()
            self.draw_menu()
            
            c = input("\nYour choice: ")
            
            if c == '1':
                n = input("\nCard name: ")
                try: 
                    q = int(input("Copies: "))
                    if not self.analyzer.add_card(n, q): print("Couldn't find that card. Check the spelling?")
                except ValueError: print("Please enter a valid number.")
                time.sleep(1.5)
            elif c == '2':
                self.import_deck_menu()
            elif c == '3':
                self.manage_deck()
            elif c == '4':
                self.analyzer.analyze()
                print("\nArchetype analyzed and target lands locked to 60-card limit!")
                time.sleep(1.5)
            elif c == '5':
                self.simulate()
            elif c == '6':
                self.analyzer.deck = []
                self.analyzer.analyze()
                print("\nDeck cleared successfully! Ready for a new brew.")
                time.sleep(1.5)
            elif c == '7':
                print("\nThanks for using the MTG Mana Base Optimizer.")
                break

    def import_deck_menu(self):
        txt_files = glob.glob("*.txt")
        if not txt_files:
            print("\nCouldn't find any .txt files in this folder. Please save your deck file here and try again.")
            time.sleep(2)
            return

        print("\nFound these deck files:")
        for i, f in enumerate(txt_files):
            print(f" [{i}] {f}")

        try:
            choice = input("\nWhich one should I load? (Enter the number or 'q' to cancel): ")
            if choice.lower() == 'q': return
            filepath = txt_files[int(choice)]
            self.process_import(filepath)
        except (ValueError, IndexError):
            print("Invalid choice, let's try again.")
            time.sleep(1)

    def process_import(self, filepath):
        if os.path.getsize(filepath) == 0:
            print(f"\nThe file '{filepath}' is empty. Please check your export.")
            time.sleep(2)
            return

        basics = {"plains", "island", "swamp", "mountain", "forest", "pianura", "isola", "palude", "montagna", "foresta"}
        is_sideboard = False
        cards_added = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.lower() == 'deck' or line.lower() == 'commander': continue
                    
                    if line.lower() == 'sideboard':
                        is_sideboard = True
                        continue
                        
                    if is_sideboard: continue

                    parts = line.split(' (')[0].strip().split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        if parts[1].lower() not in basics:
                            if self.analyzer.add_card(parts[1], int(parts[0])):
                                cards_added += 1
            
            if cards_added == 0:
                print("\nNo valid mainboard cards found in the file.")
            else:
                self.analyzer.analyze()
                print(f"\nSuccessfully imported mainboard cards from {filepath}.")
                print(f"Archetype set to {self.analyzer.archetype}!")
            
        except Exception: 
            print("\nSomething went wrong while reading the file.")
        time.sleep(2)

    def manage_deck(self):
        while True:
            self.clear()
            print("\nManage Your Deck")
            print("-" * 20)
            if not self.analyzer.deck:
                print("Your deck is currently empty.")
            else:
                for i, c in enumerate(self.analyzer.deck): 
                    print(f"[{i}] {c['copies']}x {c['name']}")
            
            print("\nEnter the ID of the card to modify (or 'q' to go back).")
            c = input("Choice: ")
            if c.lower() == 'q': break
            
            if c.isdigit() and 0 <= int(c) < len(self.analyzer.deck):
                try: 
                    new_copies = int(input("New copies (enter 0 to remove it): "))
                    self.analyzer.update_copies(int(c), new_copies)
                    self.analyzer.analyze()
                except ValueError: 
                    print("Invalid number.")
                    time.sleep(1)

    def export_results(self, results):
        export = input("\nDo you want to export these results to a JSON file? (y/n): ")
        if export.lower() == 'y':
            filename = input("Enter filename (leave blank for 'optimizer_result'): ").strip()
            if not filename:
                filename = "optimizer_result"
            
            if not filename.endswith('.json'):
                filename += '.json'
                
            base_name, ext = os.path.splitext(filename)
            counter = 1
            final_name = filename
            
            while os.path.exists(final_name):
                final_name = f"{base_name}_{counter}{ext}"
                counter += 1
                
            try:
                with open(final_name, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=4)
                print(f"\nSuccess! Results exported to {final_name}")
            except Exception as e:
                print(f"\nFailed to export: {e}")

    def simulate(self):
        if not self.analyzer.spells: 
            print("\nPlease add some spells to your deck first.")
            time.sleep(1.5)
            return
        
        print("\nRunning 100,000 simulations. Please wait...")
        r = MonteCarloSimulator(self.analyzer).run()
        
        if isinstance(r, str): 
            print(f"\n{r}")
            time.sleep(2)
            return
            
        print(f"\nOptimal Mana Base Results")
        print("-" * 25)
        print(f"Target Total Lands (for 60 cards): {self.analyzer.target_lands}")
        print(f"Dual/Special Lands already added: {r['duals_added']}\n")
        
        print("Basic lands to add:")
        for k, v in r['bases'].items():
            if v > 0: print(f" + {v}x {k}")
            
        print("-" * 25)
        print(f"Total Spells: {r['spells']}")
        print(f"Consistency Score: {r['score']}% chance to hit your land drops on time.")
        
        self.export_results(r)
        input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    AppCLI().run()