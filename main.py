from app import elections_scraper_main

#main arguments provided by user - address of region to be scraped and name of csv_file where to save the results
if __name__ == "__main__":
	address = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=EN&xkraj=2&xnumnuts=2101"
	csv_file_path = 'election_results.csv'
	elections_scraper_main(address, csv_file_path)