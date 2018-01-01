from bs4 import BeautifulSoup
import os
import requests
import threading
import time


class Transit(object):

    url_protocol = 'http://'
    url_domain_name = 'winnipegtransit.com/'

    def __init__(self, path):

        # define routes information path
        self.url_path = path

        # create an empty dict to hold routes information
        self.routes = {}

        # download the html code using requests
        self.soup = BeautifulSoup(requests.get(self.url_protocol + self.url_domain_name + self.url_path).text,
                                  'html.parser')

    def __str__(self):

        # create a list of routes
        routes_list = list(self.routes.keys())

        # add all routes to a text string
        string_output = ''

        for route in routes_list:
            string_output += 'Route: {}, Title: {}, Type: {}, Link: {}\n'.format(route, self.routes[route]['title'], self.routes[route]['category'], self.routes[route]['link'])

        return string_output

    def get_routes(self, routes_table_id):

        # look for routes information in the 'a' tags of the html table
        table = self.soup.find(id=routes_table_id)
        tags_list = table.find_all('a')

        # add an entry to the dictionary for each route containing route number, title and link to the route web page
        for n in range(len(tags_list)):

            # empty the sub dictionary
            routes_sub_dict = {}

            # determine the route number
            route_number = tags_list[n]['title'].split(' ')[1]

            # load route title to sub dictionary if it exists otherwise value should be blank
            try:
                routes_sub_dict['title'] = tags_list[n]['title'].split(' - ')[1]
            except IndexError:
                routes_sub_dict['title'] = ''

            # load the web page link to the sub dictionary
            routes_sub_dict['link'] = self.url_protocol + self.url_domain_name + tags_list[n]['href']

            # load the route category to the sub dictionary
            if route_number[0] == 'S':
                routes_sub_dict['category'] = 'school'
            else:
                routes_sub_dict['category'] = 'regular'

            # find the route number to use as main dictionary key add sub dictionary information
            self.routes[route_number] = routes_sub_dict

    def get_map(self, route_number):

        # look for all links in the webpage
        for route in route_number:

            route_page = requests.get(self.routes[route]['link'])
            html_doc = route_page.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            a_tags_list = soup.find_all('a')

            for n in range(len(a_tags_list)):
                try:
                    if a_tags_list[n]['href'][-4:] == '.pdf':
                        response = requests.get(self.url_protocol + self.url_domain_name + a_tags_list[n]['href'])
                        response.raise_for_status()
                        with open(os.getcwd() + '\\maps\\' + a_tags_list[n]['href'].split('/')[-1], 'wb') as f:
                            f.write(response.content)
                except:
                    continue

    def get_all_maps(self):

        # make an enumerated list of routes
        keys_list = [(i, route) for i, route in enumerate(list(self.routes.keys()))]

        # create an empty list to hold multiple threads
        download_threads = []

        # run several threads at once to download lists of maps
        for i in range(0, len(keys_list), 5):
            thread_keys_list = [route for (i, route) in keys_list[i:i+5]]
            download_thread = threading.Thread(target=self.get_map, args=(thread_keys_list,))
            download_threads.append(download_thread)
            download_thread.start()

        # wait for all threads to complete before moving on
        for download_thread in download_threads:
            download_thread.join()


if __name__ == '__main__':
    t = Transit('en/routes/list')
    t.get_routes('route_list_table')
    t.get_routes('school_route_list_table')
    t.get_all_maps()
