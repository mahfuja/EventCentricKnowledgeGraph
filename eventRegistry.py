from eventregistry import *
from SPARQLWrapper import SPARQLWrapper, JSON , XML
import json
import pandas as pd
import simplejson as json
import io

def event_kg(sparql_query):
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    eventkg_output = (json.dumps(results, indent=4))
    entities = []
    entities = results["head"]["vars"]
    dictionary = {}
    for ent in entities:
        values = []       
        for result in results["results"]["bindings"]:
            if (result.get(ent)):
                values.append(result[ent]["value"])
            else: 
                values.append("")
        dictionary[ent] = values
    with open("eventKG_result.json", "wb") as f:
        f.write(json.dumps(dictionary, indent=4).encode("utf-8"))
    return dictionary, entities



def event_registry_event(event, lang):
    iter = QueryEventsIter(
        conceptUri=er.getConceptUri(event),
        keywords=event,
        keywordsLoc="title",
        lang=[lang])
    for art in iter.execQuery(er, sortBy = "rel"):
        event_output = (json.dumps(art, indent=4))
        break
    return event_output


def event_registry_event_mapping(event, event_output, lang, entities):
    dictionary = {}
    loc = []
    event_output = json.loads(event_output)
    if event_output["uri"] is not None:
        dictionary["event"] = event_output["uri"]
    for i in event_output["concepts"]:
        if i["label"]["eng"] == event:            
            if i["type"] == "wiki":
                dictionary["wiki"] = i["uri"]                
        if i["type"] == "loc" and i["score"] > 30:
                loc.append(i["uri"])
    dictionary["location"] = loc      
    dictionary["eventName"] = event
    dictionary["type"] = "Event"
    if event_output["eventDate"]:
        dictionary["eventDate"] = event_output["eventDate"]
    if event_output["summary"][lang]:
        info = (event_output["summary"][lang][:500] + '..') if len(event_output["summary"][lang]) > 500 else event_output["summary"][lang]
        dictionary["description"] = info
    if event_output["title"][lang]:
        dictionary["title"] = event_output["title"][lang]
    if event_output["totalArticleCount"]:
        dictionary["totalArticleCount"] = event_output["totalArticleCount"]
    for each in entities:
        if dictionary.get(each) is None:
            dictionary[each] = ""
    for each in dictionary.keys():
        if each != "location":
            value = [] 
            for lst in list(loc):                           
                value.append(dictionary[each])
            dictionary[each] = value 
    with open("ERevent_result.json", "wb") as f:
        f.write(json.dumps(dictionary, indent=4).encode("utf-8"))
    
    return dictionary



def event_registry_article(event, lang):
    q = QueryArticles(
        conceptUri=er.getConceptUri(event),
        keywords=event,
        keywordsLoc="title",
        lang=[lang])
    q.setRequestedResult(RequestArticlesInfo(count=20, sortBy="rel"))
    res = er.execQuery(q)
    json_res = json.dumps(res, indent=4)
    return json_res



def event_registry_article_mapping(eventName, article_output, entities):
    lstDic = []
    article_output = json.loads(article_output)
    for item in article_output['articles']['results']:
        dictionary = {}
        if (item['title'].lower().count(eventName.lower()) > 0):
            dictionary["eventName"] = eventName
            if item["uri"]:
                dictionary["event"] = item["uri"]
            if item["title"]:
                dictionary["title"] = item["title"]
            if item["date"]:
                dictionary["eventDate"] = item["date"]
            if item['body']:
                info = (item['body'][:500] + '..') if len(item['body']) > 500 else item['body']
                dictionary["description"] = info
            if item['eventUri']:
                dictionary["event"] = item["eventUri"]
            if item['url']:
                dictionary["event_url"] = item['url']
            if item['dataType']:            
                dictionary["UriType"] = item['dataType']
            dictionary["type"] = 'Article'
            for each in entities:
                if dictionary.get(each) is None:
                    dictionary[each] = ""
        for each in dictionary.keys():        
            value = [] 
            if dictionary[each]:                          
                value.append(dictionary[each])
            else:
                value.append("")
            dictionary[each] = value 
        lstDic.append(dictionary)
    with open("ERarticle_result.json", "wb") as f:
        f.write(json.dumps(lstDic, indent=4).encode("utf-8"))
    return lstDic



def event_preprocess(sparql_query):
    sparql.setQuery(sparql_query)
    query_string = sparql.queryString
    event = re.findall(r"dbr:([^ <]+)",query_string)
    lang = ""
    if not event:
        event = re.findall(r"rdfs:label \"(.*)\"",query_string)
        lang = re.findall(r"@(.*).",query_string)
    if not event:
        event = re.findall(r"rdfs:label \'(.*)\'",query_string)
        lang = re.findall(r"@(.*).",query_string)
    
    if lang == "":
        lang = "en"
    event = "".join(event)
    event = event.replace("_", " ")
    lang = "".join(lang)
    return event, lang



def integrated_model(sparql_query):
    event_kg_result, entities = event_kg(sparql_query)
    event, lang = event_preprocess(sparql_query)
    if lang == "de":
        lang = "deu"
    elif lang == "ru":
        lang = "rus"
    elif lang == "fr":
        lang = "fra"
    else:
        lang="eng"
    event_registry_event_result = {}
    event_registry_article_result = {}
    if event:
        event_ouput = event_registry_event(event, lang)    
        event_registry_event_result =  event_registry_event_mapping(event, event_ouput, lang, entities)
        
        article_output = event_registry_article(event, lang)
        event_registry_article_result =  event_registry_article_mapping(event, article_output, entities)
        
    final_result = {}
    for ent in entities:
        values = []
        if(event_kg_result.get(ent)):
            if not event_kg_result[ent]:
                pass
            else:
                values += event_kg_result[ent]
        if(event_registry_event_result.get(ent)):
            if not event_registry_event_result[ent]:
                pass
            else:
                values += event_registry_event_result[ent]
        for Dic_item in list(event_registry_article_result):
            if(Dic_item.get(ent)):
                if not Dic_item[ent]:
                    pass
                else:
                    values += Dic_item[ent]
        final_result[ent] = values
        
    return final_result, event_kg_result, event_registry_event_result, event_registry_article_result

def generate_html_output(final_result):
    #f = open("integrated_output.html", "w+")
    size = 0
    for each in final_result.keys():
        if(size<len(final_result[each])):
            size = len(final_result[each])
    items = '<table border="1"><tr><th>' + '</th><th>'.join(final_result.keys()) + '</th></tr>'
        
    for k in range(size):
        items += '<tr>'
        for each in final_result.keys():
            if final_result[each][k]== "":
                items += '<td>'+str(" ")+'</td>'
            elif "http" in final_result[each][k]:
                items += '<td><a href="'+final_result[each][k]+'">'+final_result[each][k]+'</a></td>'
            else:
                items += '<td>'+str(final_result[each][k])+'</td>'
        items += '</tr>'
    items += '</table>\n'
    
    with io.open("integrated_output.html", "w+", encoding="utf-8") as f:
        f.write(items)
    

er = EventRegistry(apiKey = "API_KEY")

sparql = SPARQLWrapper("http://eventkginterface.l3s.uni-hannover.de/sparql")
sparql_query = input("Please enter the sparql query : ")

final_result, event_kg_result, event_registry_event_result, event_registry_article_result = integrated_model(sparql_query)

dataFrame = pd.DataFrame.from_dict(data=final_result, orient='columns')
nan_value = float("NaN")
dataFrame.replace("",nan_value, inplace = True)
dataFrame = dataFrame.dropna(axis=0, how='all')
export_csv = dataFrame.to_csv (r'integrated_output.csv', index = None, header=True) 

dataFrame.replace(nan_value,"", inplace = True)
Final_dict = dataFrame.to_dict()

generate_html_output(Final_dict)
