import urllib
from BeautifulSoup import BeautifulStoneSoup


class reflectEntity:
    def __init__(self, entity_string):
        entity = entity_string
        number = 0

class reflectItem:
    def __init__(self, name):
        identified_string = name
        count = 0
        entities = []
        

def generateQueryUrl(query_text, return_type):
    """
    If the command is to graph, then we pull more results in order to find
    an overlap between authors.
    
    """
    if return_type == "xml":
        root_url = "http://reflect.cbs.dtu.dk/REST/GetEntities?document="
    elif return_type == "html":
        root_url = 'http://reflect.cbs.dtu.dk/REST/GetHTML?document='         
    else:
        root_url = 'http://reflect.cbs.dtu.dk/REST/GetHTML?document='
    encoded_query_text = urllib.quote(query_text.rstrip().lstrip())
    setup = {"autodetect":1, "autodetectDOI":0, "entity_types":"9606 10090"}
    setup_url = urllib.urlencode(setup)
    query_url = root_url + encoded_query_text + "&" + setup_url
    return query_url

def downloadXMLFromReflect(query_url):
    try:
        html = urllib.urlopen(query_url)
        document = html.read()
        vanilla_doc = document.decode('us-ascii', 'ignore')
        soup = BeautifulStoneSoup(vanilla_doc)
    except:
        return "error"
    return soup
    
def parseSoupForEntities(soup):
    parsed_entities = {}
    items = soup.findAll('item')
    for item in items:
        item_name = item.findAll('name')[0].contents[0]
        item_count = item.findAll('count')[0].contents[0]
        entities = item.findAll('entity')
        found_entities = []
        for entity in entities:
            entity_type = entity.findAll('type')[0].contents[0]
            entity_identifier = entity.findAll('identifier')[0].contents[0]
            found_entities.append((entity_type, entity_identifier))
        parsed_entities[item_name] = found_entities
    return parsed_entities

def get_entities_from_query(query_text):
    return_type = 'xml'
    query = generateQueryUrl(query_text, return_type)
    soup = downloadXMLFromReflect(query)
    parsed_entities = parseSoupForEntities(soup)
    return parsed_entities

def get_html_from_query(query_text):
    return_type = 'html'
    query = generateQueryUrl(query_text, return_type)
    html = downloadXMLFromReflect(query)    
    return html
    
def format_entities(entities):
    return_text = ""
    found_items = entities.keys()
    for found_item in found_items:
        return_text = return_text + found_item + " :"
        item_entities = entities[found_item]
        for entity in item_entities:
            item_type = entity[0]
            identifier = str(entity[1])
            print identifier, item_type
            return_text = return_text + item_type + identifier + "\n"
    return return_text
    
document_text = "<html><head></head><body>p53 actin</body></html> "
#result = get_html_from_query(document_text)
result = get_entities_from_query(document_text)
print_text = format_entities(result)
print print_text
