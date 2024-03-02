"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Tereza Trojanov8
email: trojanovate@gmail.com
discord: tereza4859
"""

#import packages
from requests import get
from bs4 import BeautifulSoup as bs
import csv

#check if both arguments are correct
def validate_input_address(address, csv_file_path):
	volby_addresses = 'https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ'
	main_page_response = get(volby_addresses)
	main_page_response_parsed = bs(main_page_response.text, 'html.parser')
	addresses_tables_tr_tags = main_page_response_parsed.select('table.table tr')

	#prepare empty list and append all valid urls from the main page
	urls_list = []

	for tag in addresses_tables_tr_tags:
	    a_tags = tag.find_all('a')
	    if a_tags:
	        last_a_tag = a_tags[-1]
	        href = "https://volby.cz/pls/ps2017nss/" + last_a_tag.get('href')
	        if href:
	            urls_list.append(href)

	if address not in urls_list:
		return 0    #invalid address
	elif csv_file_path == '' or not ".csv" in csv_file_path:
		return 0    #invalid csv name
	else:
		return 1    #input is valid

#get code, name and result page link for each territorial unit
def get_code_name_result_page(address):
	response = get(address)
	parsed_html = bs(response.text, 'html.parser')
	td_tags_codes = parsed_html.find_all('td', class_='cislo')
	results = []
	for td_tag in td_tags_codes:
		code = td_tag.text
		location = td_tag.find_next('td', class_='overflow_name').text
		result_link = td_tag.find_next('a')['href']
		result_link_full = "https://volby.cz/pls/ps2017nss/" + result_link
		results.append({"result_link": result_link_full,"code": code, "location": location})

	return (results)

#get general statistics (number of registered voters, envelopes and valid votes) and number of voted for each party
def get_election_results(territorial_units):
	election_results = []
	for territorial_unit in territorial_units:
		result_response = get(territorial_unit['result_link'])
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
def elections_scraper_main(address, csv_file_path):
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

#main arguments
if __name__ == "__main__":
	address = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102"
	csv_file_path = 'election_results.csv'
	elections_scraper_main(address, csv_file_path)