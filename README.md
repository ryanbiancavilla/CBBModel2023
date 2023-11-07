# College Basketball Betting Model - 2023

This repository contains a Python script for extracting and analyzing sports betting data for college basketball games. The main calculations script is `CBBModel2023.py`, and the Streamlit app for visualizing the projections is `NCAAStreamlit.py`. The README file provides an overview of the code and how to use it.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Script Overview](#script-overview)
- [Customization](#customization)

## Requirements

Before using the script, make sure you have the following prerequisites installed:

- Python 3.x
- Required Python libraries: BeautifulSoup, requests, pandas, json, numpy, streamlit

## Installation

1. Clone this repository to your local machine or download the script.

   ```bash
   git clone https://github.com/yourusername/CollegeBasketballBettingModel.git
   ```

2. Navigate to the project directory.

   ```bash
   cd CollegeBasketballBettingModel
   ```

3. Install the required Python libraries using pip.

   ```bash
   pip install beautifulsoup4 requests pandas numpy streamlit
   ```

## Usage

To use this script, follow these steps:

1. Run the main calculations script to fetch and update the projections.

   ```bash
   python CBBModel2023.py
   ```

2. Run the Streamlit app to visualize the projections.

   ```bash
   streamlit run NCAAStreamlit.py
   ```

3. The main calculations script (`CBBModel2023.py`) will perform the following tasks:
   - Scrape data from KenPom to retrieve team statistics.
   - Fetch sports betting data from Oddsshark using the OddsShark API.
   - Calculate adjusted statistics and projections for each game.
   - Simulate games to generate win percentages, spread edges, and over/under percentages.
   - Update the `proj_scores` DataFrame with the latest projections.

4. The Streamlit app (`NCAAStreamlit.py`) will display the projections in an interactive web interface.

## Script Overview

The main calculations script (`CBBModel2023.py`) consists of several key components:

1. **Data Scraping**: It uses the BeautifulSoup library to scrape team statistics from KenPom and sports betting data from Oddsshark.

2. **`find_team` Function**: This function allows you to find team information by providing the team name as input. It retrieves data from the KenPom dataset.

3. **Data Analysis**: The script calculates adjusted statistics, projected scores, spreads, and over/under values for each game.

4. **Simulation**: It simulates games using Monte Carlo simulations to estimate win percentages, spread edges, and over/under percentages.

5. **`proj_scores` DataFrame**: The updated projections are stored in the `proj_scores` DataFrame, which is used by the Streamlit app.

## Customization

You can customize the main calculations script and the Streamlit app as follows:

- Adjust Monte Carlo simulation parameters by changing `num_simulations` in `CBBModel2023.py`.
- Modify the team name mapping file (`CBBTeamsDatabase.xlsx`) to include the teams you are interested in.
- Customize the Streamlit app interface and styling in `NCAAStreamlit.py`.

For any questions or issues, please create a GitHub issue in this repository.

Enjoy analyzing college basketball games with the 2023 College Basketball Betting Model!