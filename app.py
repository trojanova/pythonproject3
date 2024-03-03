import json
from typing import Any

from requests_cache import CachedSession, OriginalResponse, CachedResponse
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs
import csv


def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)


session = CachedSession('elections_cache', expire_after=3600)
config = load_config('config.json')
base_url = config['BASE_URL']
csv_file_path = config['csv_file_path']


def fetch_url(url: str) -> OriginalResponse | CachedResponse | None:
    try:
        response = session.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response
    except RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def parse_html(html_content: Any) -> bs | None:
    try:
        return bs(html_content, 'html.parser')
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None


def validate_input_address(address: str, csv_file_path: str) -> int:
    response = fetch_url(f'{base_url}ps3?xjazyk=EN')
    if response is None: return 0
    parsed_html = parse_html(response.text)
    if parsed_html is None: return 0
    addresses_tables_tr_tags = parsed_html.select('table.table tr')
    urls_list = [base_url + tag.find_all('a')[-1].get('href') for tag in addresses_tables_tr_tags if tag.find_all('a')]
    return 1 if address in urls_list and csv_file_path.endswith('.csv') else 0


def get_code_name_result_page(address: str) -> list[dict[str, str]]:
    response = fetch_url(address)
    if response is None: return []
    parsed_html = parse_html(response.text)
    if parsed_html is None: return []
    results = []
    for td_tag in parsed_html.find_all('td', class_='cislo'):
        code = td_tag.text
        location = td_tag.find_next('td', class_='overflow_name').text
        result_link = td_tag.find_next('a')['href']
        result_link_full = base_url + result_link
        results.append({"result_link": result_link_full, "code": code, "location": location})
    return results


def get_election_results(territorial_units: list[dict[str, str]]) -> list[dict[str, str]]:
    for unit in territorial_units:
        response = fetch_url(unit['result_link'])
        if response is None: continue
        parsed_html = parse_html(response.text)
        if parsed_html is None: continue
        tr_tags = parsed_html.find_all('tr')[2]
        unit["registered"] = tr_tags.find('td', headers='sa2').text.strip()
        unit["envelopes"] = tr_tags.find('td', headers='sa3').text.strip()
        unit["valid"] = tr_tags.find('td', headers='sa6').text.strip()
        parties = parsed_html.select('table.table td.overflow_name')
        for party in parties:
            party_name = party.text.strip()
            party_votes = party.find_next('td', class_='cislo').text.strip()
            unit[party_name] = party_votes
    return territorial_units


def elections_scraper_main(address: str, csv_file_path: str) -> None:
    if validate_input_address(address, csv_file_path) == 0:
        print("Input validation failed. Please ensure you have entered a valid address and .csv file name.")
        return
    print("Input validation succeeded. Processing to the next step.")
    territorial_units = get_code_name_result_page(address)
    print("Getting selection results for territorial units...")
    election_results = get_election_results(territorial_units)
    column_names = list(election_results[0].keys()) if election_results else []
    column_names.remove('result_link') if 'result_link' in column_names else None
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        for unit_results in election_results:
            del unit_results['result_link']
            writer.writerow(unit_results)
    print(f"Election results successfully imported into '{csv_file_path}'.")