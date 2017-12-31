from bs4 import BeautifulSoup
import requests
import shelve

def create_routes_dict(soup_object, url_protocol_and_domain_name):
    # create empty dictionaries
    output_dict = {}

    # add an entry to the dictionary for each route containing route number, title and link to the route web page
    for n in range(len(soup_object)):

        # empty the sub dictionary
        output_sub_dict = {}

        # load route title to sub dictionary if it exists otherwise value should be blank
        try:
            output_sub_dict['title'] = soup_object[n]['title'].split(' - ')[1]
        except IndexError:
            output_sub_dict['title'] = ''

        # load webpage link and type to sub dictionary
        output_sub_dict['link'] = url_protocol_and_domain_name + soup_object[n]['href']
        output_sub_dict['category'] = 'regular'

        # find the route number to use as main dictionary key add sub dictionary information
        route_number = soup_object[n]['title'].split(' ')[1]
        output_dict[route_number] = output_sub_dict

    return output_dict


def human_sort_string_type_integers_list(input_list):

        # create empty lists
        output_list = []
        integer_list = []

        # convert each input list element to type integer
        for elem in input_list:
            try:
                integer_list.append(int(elem))
            except TypeError:
                print('{} could not be converted to type integer'.format(elem))
                integer_list.append(int(elem))
                continue

        # sort the list of integers
        integer_list.sort()

        # create a new list and change each element back to type string
        for elem in integer_list:
            output_list.append(str(elem))

        return output_list


def make_soup(protocol, domain_name, path):

    # create url variable
    url = protocol + domain_name + path

    # download the html code using requests
    r = requests.get(url)
    html_doc = r.text
    return BeautifulSoup(html_doc, 'html.parser')


def parse_html_table_a_tags(soup_obj, table_id):

    # look for routes information in the 'a' tags of the html table
    table = soup_obj.find(id='route_list_table')
    return table.find_all('a')


if __name__ == '__main__':

    url_protocol = 'http://'
    url_domain_name = 'winnipegtransit.com/'
    url_path = 'en/routes/list'
    table_id = 'route_list_table'

    soup = make_soup(url_protocol, url_domain_name, url_path)
    a_tags_list = parse_html_table_a_tags(soup, table_id)
    routes_dict = create_routes_dict(a_tags_list, url_protocol + url_domain_name)
    routes_list_sorted = human_sort_string_type_integers_list(list(routes_dict.keys()))

for route in routes_list_sorted:
        print('Route: {}, Title: {}, Type: {}, Link: {} '
              .format(route, routes_dict[route]['title'], routes_dict[route]['category'], routes_dict[route]['link']))
