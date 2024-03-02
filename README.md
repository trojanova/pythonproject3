# Election Results Scraper

## Overview
The Election Results Scraper is a Python program designed to scrape election result data from the Czech Statistical Office website. It retrieves election results for territorial units based on the provided address and exports them into a CSV file.

## How It Works
The program consists of several functions. It first validates the address and CSV file path provided by the user. In case these inputs are invalid, the program stops and ask the user for correction. In case both inputs are valid, the program proceeds to fetch the election results for each territorial unit within selected region. Then it saves the collected data into a CSV file.

## Usage
To use the Election Results Scraper, follow these steps:
1. Install the required Python packages using `pip install -r requirements.txt`.
3. Run the `main.py` script with the appropriate arguments.:
- **address**: The absolute URL of the region from which election results should be scraped.
- **csv_file_path**: The name of the output CSV file. This file will be created and filled with the scraped election results. Ensure that the csv_file_path ends with '.csv' to specify the format of the output file.

## Demonstration
1. Clone this git repository:
```
git clone https://github.com/trojanova/pythonproject3
```
2. Open the cloned repository in your IDE.
3. Install required packages:
```
pip install -r requirements.txt
```
4. Choose the municipality you want to scrape:
- At the following page: https://volby.cz/pls/ps2017nss/ps3?xjazyk=EN select you preferred municipality - click the X "button" (column Choice of a municipality)

- Copy the absolute URL and set it to the address parameter in `main.py`.
6. Set csv_file_path to the desired name of the output CSV file.
7. Run the script.
