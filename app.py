"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Tereza Trojanová
email: trojanovate@gmail.com
discord: tereza4859
"""

#import packages
from requests import get
from bs4 import BeautifulSoup as bs
from requests_cache import CachedSession, OriginalResponse, CachedResponse
from requests.exceptions import RequestException
import csv

#set variables
election_addresses = 'https://volby.cz/pls/ps2017nss/ps3?xjazyk=EN'
result_link_base = 'https://volby.cz/pls/ps2017nss/'

#create cached session
session = CachedSession('elections_cache', expire_after=3600)

#define fetch_url and parse_html functions to raise HTML/parsing error for invalid responses
def fetch_url(url: str) -> OriginalResponse | CachedResponse | None:
    try:
        response = session.get(url)
        response.raise_for_status()
        return response
    except RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
def parse_html(html_content) -> bs | None:
    try:
        return bs(html_content, 'html.parser')
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

#check if both arguments are valid
def validate_input_address(address: str, csv_file_path: str) -> int:
	main_page_response = fetch_url(election_addresses)
	if main_page_response is None: return 0
	main_page_response_parsed = parse_html(main_page_response.text)
	if main_page_response_parsed is None: return 0
	addresses_tables_tr_tags = main_page_response_parsed.select('table.table tr')

	#prepare empty list and append all valid urls from the main page
	urls_list = []

	for tag in addresses_tables_tr_tags:
		a_tags = tag.find_all('a')
		if a_tags:
			last_a_tag = a_tags[-1]
			href = result_link_base + last_a_tag.get('href')
			if href:
				urls_list.append(href)

	if address in urls_list and csv_file_path.endswith('.csv'):
		return 1  # valid arguments
	else:
		return 0  # invalid address or csv name

#get code, name and result page link for each territorial unit
def get_code_name_result_page(address: str) -> list[dict[str, str]]:
	response = session.get(address)
	parsed_html = bs(response.text, 'html.parser')
	td_tags_codes = parsed_html.find_all('td', class_='cislo')
	results = []
	for td_tag in td_tags_codes:
		code = td_tag.text
		location = td_tag.find_next('td', class_='overflow_name').text
		result_link = td_tag.find_next('a')['href']
		result_link_full = result_link_base + result_link
		results.append({'result_link': result_link_full,'code': code, 'location': location})

	return (results)

#get general statistics (number of registered voters, envelopes and valid votes) and number of voted for each party
def get_election_results(territorial_units: list[dict[str, str]]) -> list[dict[str, str]]:
	election_results = []
	for territorial_unit in territorial_units:
		result_response = session.get(territorial_unit['result_link'])
		result_response_parsed = bs(result_response.text, 'html.parser')
		tr_tags = result_response_parsed.find_all('tr')[2]


		#extract general statistics for territorial unit
		registered = tr_tags.find('td', headers='sa2').text.strip()
		envelopes = tr_tags.find('td', headers='sa3').text.strip()
		valid = tr_tags.find('td', headers='sa6').text.strip()

		#insert these statistics into the dictionary
		territorial_unit["registered"] = registered
		territorial_unit["envelopes"] = envelopes
		territorial_unit["valid"] = valid

		#get names and number of votes for all political parties
		parties = result_response_parsed.select('table.table td.overflow_name')
		for party_name in parties:
			party_name_text = party_name.text.strip()
			party_votes = party_name.find_next('td', class_='cislo').text.strip()
			territorial_unit[party_name_text] = party_votes

	return territorial_units

#main function
def elections_scraper_main(address: str, csv_file_path: str) -> None:
	# validate input address and csv file path
	validation_result = validate_input_address(address, csv_file_path)

	if validation_result == 0:
		print("Input validation failed. Please ensure you have entered a valid address and .csv file name. For more information check the readme.md file.")
		return
	else:
		print("Input validation succeeded. Processing to the next step.")
		#get name and link for each territorial unit
		print("Getting codes, names and result pages for territorial units within your selected region...")
		territorial_units = get_code_name_result_page(address)
		#then iterate through the list and scrape results
		print("Getting selection results for territorial units...")
		election_results = get_election_results(territorial_units)

		#column names for .csv file
		print("Formatting .csv file...")
		column_names = list(election_results[0].keys())
		#result link is used above for results scraping, but not necessary for the output
		column_names.remove('result_link')

		with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=column_names)

			#write header
			print("Importing results...")
			writer.writeheader()

			#write results
			for territorial_unit_results in election_results:
				del territorial_unit_results['result_link']
				writer.writerow(territorial_unit_results)

	print("Election results successfully imported into '" + csv_file_path + "'.")