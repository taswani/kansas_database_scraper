from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

keywords = ['bill', 'utility', 'child', 'care', 'pregnancy', 'education', 'employment', 'food', 'clothing', 'health', 'management', 'medical', 'medication', 'housing', 'mental', 'treatment', 'facilities', 'older', 'adult', 'primary', 'care', 'healthcare', 'support', 'groups', 'transportation', 'accessibility', 'alcohol', 'drug', 'addiction', 'substance', 'abuse', 'subsidy']
resources_dict = {}

with open('resources.txt', "w", encoding="utf-8") as f:
    for i in range(1, 455):
        print('Currently working on page {}'.format(i))
        url = 'https://211kansas.bowmansystems.com/index.php/component/cpx/?task=search.query&view=&page={page}&search_history_id=131817532&unit_list=0&akaSort=0&query=%20&simple_query='.format(page = i)
        raw_html = simple_get(url)
        soup = BeautifulSoup(raw_html, 'html.parser')
        services = soup.findAll('p', {'class', 'services'})
        for j in services:
            # This section is for removing all the white spaces and everything else that isn't needed.
            new = j.text.strip()
            pattern = re.compile("^\s+|\s*,\s*|\s+$")
            new = [x for x in pattern.split(new)]
            final = [x.split('/') for x in new]
            flat_list = []
            for sublist in final:
                for item in sublist:
                    flat_list.append(item)
            flat_list = [x.split(' ') for x in flat_list]
            flatter_list = []
            for sublist in flat_list:
                for item in sublist:
                    flatter_list.append(item)
            for word in flatter_list:
                if word.lower() in keywords:
                    # This section is for parsing out page specifics from each page
                    page_url = 'https://211kansas.bowmansystems.com' + j.parent.h4.a.get('href')
                    page_html = simple_get(page_url)
                    page_soup = BeautifulSoup(page_html, 'html.parser')

                    name = page_soup.find('p', id='view_field_name_top')
                    address = page_soup.find('p', id='view_field_primaryAddressId')
                    for br in address.find_all("br"):
                        br.replace_with("\n")
                    phone = page_soup.find('p', id='view_field_primaryTelephone')
                    description = page_soup.find('p', id='view_field_description')
                    hours = page_soup.find('p', id='view_field_hours')

                    if name not in resources_dict:
                        try:
                            resources_dict[name.text] = [address.text, phone.text, description.text, hours.text, word]
                        except AttributeError:
                            resources_dict[name.text] = [address.text, 'No phone provided for this location', description.text, 'No hours provided for this location', word]

    for k, v in resources_dict.items():
        f.write(k)
        f.write('\n')
        f.write(v[0])
        f.write(v[1])
        f.write('\n')
        f.write(v[2])
        f.write('\n')
        f.write(v[3])
        f.write('\n')
        f.write(v[4])
        f.write('\n')
        f.write('\n')

f.close
