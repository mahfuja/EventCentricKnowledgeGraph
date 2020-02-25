# EventCentricKnowledgeGraph
Integration of EventKG and EventRegistry data model

# Cloning the repository
git clone https://github.com/mahfuja/EventCentricKnowledgeGraph

# Required python packages 
install packages by "pip install packageName"
1. eventregistry
2. SPARQLWrapper
3. json
4. simplejson

# Get API_KEY from EventRegistry
website: http://eventregistry.org/
By signing up, you can generate API_KEY and get data access from EventRegistry

# SPARQLWrapper
Is a SPARQL endpoint which will gives integrated data from different RDF sources (eg: DBPedia, Yago, EventKG etc.)
I have used http://eventkginterface.l3s.uni-hannover.de/sparql as a SPARQL endpoint.

Getting access from EventRegistry and SPARQL endpoints,
you can run the EventCentricKnowledgeGraph by following command

python eventRegistry.py

As a input parameter user needs to give SPARQL query.
sparql_example.txt as a reference query example.
