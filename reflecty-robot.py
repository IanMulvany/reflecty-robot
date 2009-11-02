"""
reflecty-robot.py
a google appenging robot for google wave that interacts with the ebi
reflect.we api, documentaiton available here:
 http://reflect.cbs.dtu.dk/restAPI.html 
"""

from waveapi import events
from waveapi import robot
import re
import logging
import urllib
from BeautifulSoup import BeautifulStoneSoup

logger = logging.getLogger('reflecty-robot')
logger.setLevel(logging.DEBUG)

current_version = '1.9.4'
HELP_MESSAGE = "I will query http://reflect.cbs.dtu.dk/restAPI.html , but I don't yet, give me a moment!!"       
ABOUT_MESSAGE = "LOREM IPSUM"

 

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

def get_entities_from_query(query_text):
    return_type = 'xml'
    query = generateQueryUrl(query_text, return_type)
    logger.debug('quert url: %s' % query)
    soup = downloadXMLFromReflect(query)
    parsed_entities = parseSoupForEntities(soup)
    logger.debug(parsed_entities)
    logger.debug('result is: %s' % parsed_entities)    
    return parsed_entities


def get_html_from_query(query_text):
    return_type = 'html'
    query = generateQueryUrl(query_text, return_type)
    logger.debug('quert url: %s' % query)
    html = downloadXMLFromReflect(query)    
    logger.debug('result is: %s' % html)    
    return html

def OnRobotAdded(properties, context):
    """
    Invoked when the robot has been added.

    """
    HELLO_MESSAGE = "Hi, I'm reflecty-robot, let me help you annotate your content \
 I'm version " + current_version
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(HELLO_MESSAGE)


def Notify(context):
    """
    We will only notify when the robot is added or updated, not 
    when a new participant is added, this increases clutter in the wave
       
    """
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi everybody!")


def ReplyToBlipWithReflectInfo(properties, context, blip_text, command, blip):
    """
    If we recognize the command, send a query to the Jane API
    If not demur with a polite response

    """
    if command == 'help':
        response = HELP_MESSAGE
    elif command == 'about':
        response = ABOUT_MESSAGE
        blip = context.GetBlipById(properties['blipId']) 
        blip.CreateChild().GetDocument().SetText(response)
    elif command == 'html':
        logger.debug('about to call html from REFLECT')        
        response = get_html_from_query(blip_text)
    elif command == 'xml':
        logger.debug('about to call xml from REFLECT')        
        entities = get_entities_from_query(blip_text)
        response = format_entities(entities)
        logger.debug(response)        
        #respons = "I should be more interesting than I am"
        blip = context.GetBlipById(properties['blipId']) 
        blip.CreateChild().GetDocument().SetText(response)
    else:
        response = "Hmm, I'm not sure what you mean, sorry!,\
         try (reflecty:help) for a list of commands I understand"
        
    #blip = context.GetBlipById(properties['blipId']) 
    blip.CreateChild().GetDocument().SetText(response)
    
    
def OnBlipSubmitted(properties, context):
    """
    Invoked when a blip has been added.

    """
    blip = context.GetBlipById(properties['blipId']) 
    blip_text_view = blip.GetDocument()
    blip_text = blip_text_view.GetText()
    # regex generated using http://txt2re.com/index-python.php3?s=aasfd%20(janey:command)%20aslfkjasf&4&-7&-44&-42&-43
    re1 = '.*?'    # Non-greedy match on filler
    re2 = '(\\()'    # Any Single Character 1
    re3 = '(reflecty)'    # Word 1
    re4 = '(:)'    # Any Single Character 2
    re5 = '((?:[a-z][a-z]+))'    # Word 2
    re6 = '(\\))'    # Any Single Character 3
    rg = re.compile(re1+re2+re3+re4+re5+re6, re.IGNORECASE|re.DOTALL)
    logger.debug('about to search blip text')    
    m = rg.search(blip_text)

    if m:
        command = m.group(4)
        #StripCommandFromBlip(properties, context, blip_text, command)
        ReplyToBlipWithReflectInfo(properties, context, blip_text, command, blip)
        logger.debug('query syntax recognised, command was %s', command)


if __name__ == '__main__':
    logger.debug('text: %s' % "running version " + current_version)
    myRobot = robot.Robot('relfecty-robot', 
            image_url='http://reflecty-robot.appspot.com/assets/icon.png',
            version=current_version,
            profile_url='http://reflecty-robot.appspot.com/')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
    myRobot.Run()