#import packages
from requests import get
from bs4 import BeautifulSoup as bs
import csv

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
	#first, get name and link for each territorial unit
	territorial_units = get_code_name_result_page(address)
	#then iterate through the list and scrape results
	election_results = get_election_results(territorial_units)

	#column names for .csv file
	column_names = list(election_results[0].keys())
	#result link is used above for results scraping, but not necessary for the output
	column_names.remove('result_link')

	with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=column_names)

		#write header
		writer.writeheader()

		#write results
		for territorial_unit_results in election_results:
			del territorial_unit_results['result_link']
			writer.writerow(territorial_unit_results)

#main arguments
if __name__ == "__main__":
	address = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
	csv_file_path = 'election_results.csv'
	elections_scraper_main(address, csv_file_path)