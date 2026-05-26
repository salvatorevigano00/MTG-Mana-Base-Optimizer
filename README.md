# MTG Mana Base Optimizer
MTG Mana Base Optimizer is a command-line application designed to help Magic: The Gathering players calculate the mathematically optimal mana base for their 60-card Constructed decks.

By leveraging the official MTGJSON database and a high-speed Monte Carlo simulation engine, this tool automatically identifies your deck's archetype, locks in the required number of lands, and calculates the exact distribution of basic lands needed to consistently hit your land drops on a curve.

## Features

* **Automated Database Management:** Automatically downloads the latest Standard card database from MTGJSON and parses it into a lightweight, optimized CSV format.
* **Smart Archetype Detection:** Analyzes the ratio of creatures, instants, and sorceries alongside the average Mana Value (CMC) to accurately classify your deck as Aggro, Tempo, Burn, Midrange, Control, or Ramp.
* **Arena Import Compatibility:** Seamlessly imports exported decklists directly from Magic: The Gathering Arena text files (.txt), automatically ignoring basic lands and sideboards.
* **Monte Carlo Simulation:** Uses NumPy to run 100,000 hypergeometric simulations in a fraction of a second, calculating the exact probability of hitting your target land drops based on your specific archetype.
* **JSON Export:** Allows you to export your deck's final statistics and land distribution to a clean JSON file for future reference.

## Project Structure

* `main.py`: The orchestrator script. It handles the initial environment setup, downloads the JSON file (bypassing basic bot protections), triggers the parser, and launches the CLI application.
* `mtg_parser.py`: Processes the raw MTGJSON data, extracting only the necessary parameters (Mana Value, colored pips, card types) and generating `mtg_simulator_db.csv`.
* `mtga_optimizer.py`: The core application containing the interactive menu, deck management logic, archetype analyzer, and the Monte Carlo simulator.

## Prerequisites
To run the application from the source code, you need Python installed on your system along with the `numpy` library.

```bash
pip install numpy
```

## Installation and Usage
1. Clone or download this repository to your local machine.
2. Open your terminal or command prompt and navigate to the project folder.
3. Run the application:

```bash
python main.py
```

On its first run, the application will take a few moments to download the MTGJSON database and build the local CSV file. Subsequent launches will bypass this step and open immediately.

## Importing Decks
To analyze a deck built in MTG Arena:

1. Click "Export" in the MTG Arena deck builder.
2. Paste the clipboard contents into a plain text file (e.g., `my_deck.txt`) and save it in the same directory as the application.
3. Launch the application and select option `2` from the main menu to load it.

## License
This project is licensed under the MIT License. You are free to use, modify, distribute, and build upon this software for both personal and commercial projects without restriction.