#!/usr/bin/env python
# coding: utf-8

 # Used to parse webpages
import requests               as req
from bs4 import BeautifulSoup as bs4
from bs4 import element       as bel
import re

# Used for some very minor string processing
from string import printable




# ## Method Definitions

class regexes:
    """a container object for compiled regexes used in matIDfetch """
    tagloc  = re.compile(r'.*Replacing.*')
    matguid = re.compile(r'matguid=([0-9a-f]{32})') 

################### Methods for getting GUID-name pairs #######################

def pageprocess(thispage, *args, display=None, **kwargs):
    """
    A single, compact function that fully extracts matUUID's and material names
    from the provided page.
    
    Args:
        thispage (req.Response): A response object from which to extract
        matUUIDs and material names
        
        display: A object able to indicate progress of the page processing
    
    """
    matdict = dict()
    pagesoup = bs4(thispage.text, 'html.parser')
    selection = pagesoup.select("body > form > div > ul > li > a")
    
    
    def Rstringify(tag):
        """
        A recursive function to convert html sub tags into latex format
        
        Args:
            tag: A tag to be recursively expanted into latex
        
        Raises:
            ValueError: If it encounters something other than a sub tag
        
        Returns:
            String, with no HTML tags in it.
        
        """
        workingstring = ""
        for item in tag.children:
            if type(item) is bel.NavigableString:
                workingstring += str(item)
            if type(item) is bel.Tag:
                if item.name == 'sub':
                    workingstring+='_{'
                    workingstring+=Rstringify(item)
                    workingstring+='}'
                elif item.name == 'sup':
                    workingstring+='^{'
                    workingstring+=Rstringify(item)
                    workingstring+='}'
                
                elif item.name == 'font':
                    workingstring+=Rstringify(item)
                else:
                    errorlist = (str(item),thispage.url)
                    raise ValueError(
                        """
                        {0}
                        for page
                        {1}
                        """.format(*errorlist)
                    )
        return workingstring
    
    for entry in selection:
        guid_re = regexes.matguid.search(entry['href'])
        guid = int(guid_re[1],16)
        name = Rstringify(entry)
        matdict[guid] = name
    return matdict


def list_of_pages (allmats="http://www.matweb.com/search/GetAllMatls.aspx",
                   n=None):
    """
    Accumulates the URLS of all pages that contain individual materials.
    Returns them all in a list
    
    Args:
       allmats: the url of the page that contains all page links. 
    """
    index_page = req.get(allmats)
    if index_page.status_code != 200:
        raise ValueError("Failed to fetch page {0}!".format(allmats))
    index_soup = bs4(index_page.text,'html.parser')
    selection = index_soup.select("body > form > div > ul > li > a")
    prefix = allmats.rstrip(printable.replace('/',''))
    if n is None:
        return [prefix+sel_tag['href'] for sel_tag in selection]
    return [prefix+sel_tag['href'] for sel_tag in selection][:n]