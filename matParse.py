# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from bs4 import BeautifulSoup as bs4
from bs4 import element as elm
import requests as req
import libs.tree_visualizer as tv
import libs.tor_session as ts

tor_session, process = ts.make_session()

resp = tor_session.get("http://www.matweb.com/search/datasheet_print.aspx?matguid=675469b4fe1b45309143f469889bbe62")

# + jupyter={"outputs_hidden": true}
resp.text
# -

matsoup = bs4(resp.text, 'html.parser')
tables = matsoup.select('div[id*=DataSheet]>table')


len(tables)



# Format:
# `{"Category":{"PropertyName":[[metricValue,EnglishValue,Comment],[metricValue,englishValue,Comment],[]]`

# +
class Properties:
        name = ""
        entries = dict()

class Value:
    units = "ul"
    unitID = None
    value = 0
    condition = ""
    
    def __init__(self,name,value=None, units=None):
        # If just plugging in values
        if isinstance(name,str):
            if isinstance(value,(float,int,tuple,str)) and isinstance(units,(str)):
                if isinstance(value,tuple) and len(value) != 2:
                    raise ValueError("If a range is provided, a maximum and minimum must be given")
                self.name = name
                self.units = units
                self.value = value
            else:
                raise TypeError("Value must be a number or tuple, units must be a string")

class Info:
    # Categorys as a tuple of name and ID
    categories = list()
    notes= ""
    keywords = list()
    # Other feilds, with limited processing.
    other = dict()
    def _parse_info(self,info_tag):
        # Take a provided tag object, and exctract data from it.
        rows = info_tag.select('tr')
        info_dict = dict()
        for row in rows:
            if row.th is not None:
                self.name = row.th.get_text()
                continue
            cells = row.select('td')
            if len(cells) != 2:
                continue
            prop_name = cells[0].get_text()
            prop_value = cells[1]
            info_dict[prop_name] = prop_value
        return info_dict
    
    def _parse_Categories(self, tag):
        
        for cat in tag.find_all("a"):
            cat. 
            name = tag.string 
            
                
    def __init__(self,tag):
        dat= self._parse_info(tag)
        for name, entry in dat.items():
            print("-"*5, name, "-"*5)
            print(entry.prettify())


class Material:
   
    
    
    def _parse_props(self,prop_tag):
        self.prop_dict = dict()
        category = None
        for row in prop_tag.select('tr'):
            if row.th is not None:
                category = row.th.string.replace("Properties","")
                self.prop_dict[row.th.string.replace("Properties","")]= set()
                continue
                
            if category is None or row.find(class_='dataCell') is None:
                continue
            
            print(row.attrs)

            self.prop_dict[category].add(Value(row)) 
# -

Info(tables[0])

# + jupyter={"outputs_hidden": true}
stuff = Material()
stuff._parse_info(tables[0])


# -

stuff.info_dict

for key,value in  stuff.prop_dict.items():
    print(key)
    print(value)


for key,value in stuff.info_dict.items():
    print(key,"=\n",value,"\n-------------------------\n")


