
# coding: utf-8

# In[ ]:


#from textblob import TextBlob
#from attributegetter import *
from generatengrams import ngrammatch
from Contexts import *
import json
from Intents import *
import random
import os
import re


# In[ ]:
# Read Json File
def getRestaurants(location, cuisine, costpref):
    with open('restaurants.json') as resta_file:
        try:
            restaList = json.load(resta_file)
        except:
            print("no json file loaded for finding restaurants")

    #print(restaList)
    print("given attributes...:",location, cuisine, costpref)
    
    restaurantsFound = [str(i+1) + ") " + restaurant["name"] for i, restaurant in enumerate(filter(lambda restaurant: restaurant["location"] == location and (restaurant["cuisines"]) == cuisine and (restaurant["costpref"] == costpref) , restaList))]
    return restaurantsFound


def check_actions(current_intent, attributes, context):
    '''This function performs the action for the intent
    as mentioned in the intent config file'''
    '''Performs actions pertaining to current intent
    for action in current_intent.actions:
        if action.contexts_satisfied(active_contexts):
            return perform_action()
    '''

    context = IntentComplete()
    return 'action: ' + current_intent.action, context

def check_required_params(current_intent, attributes, context):
    '''Collects attributes pertaining to the current intent'''
    
    for para in current_intent.params:
        if para.required:
            if para.name not in attributes:
                #Example of where the context is born, implemented in Contexts.py
                if para.name=='RegNo':
                    context = GetRegNo()
                #returning a random prompt frmo available choices.
                return random.choice(para.prompts), context

    return None, context


def input_processor(user_input, context, attributes, intent):
    '''Spellcheck and entity extraction functions go here'''
    
    #uinput = TextBlob(user_input).correct().string
    
    #update the attributes, abstract over the entities in user input
    attributes, cleaned_input = getattributes(user_input, context, attributes)
    
    return attributes, cleaned_input

def loadIntent(path, intent):
    with open(path) as fil:
        dat = json.load(fil)
        intent = dat[intent]
        return Intent(intent['intentname'],intent['Parameters'], intent['actions'])

def intentIdentifier(clean_input, context,current_intent):
    clean_input = clean_input.lower()
    
    #Scoring Algorithm, can be changed.
    scores = ngrammatch(clean_input)
    print("scores=", scores)
    #choosing here the intent with the highest score
    scores = sorted_by_second = sorted(scores, key=lambda tup: tup[1])
    # print clean_input
    #print 'scores', scores
    

    if(current_intent==None):
        if(clean_input=="search"):
            return loadIntent('params/newparams.cfg', 'SearchStore')
        if(clean_input=='book'):
            return loadIntent('params/newparams.cfg','OrderBook')
        else:
            return loadIntent('params/newparams.cfg',scores[-1][0])
    else:
        #If current intent is not none, stick with the ongoing intent
        return current_intent

def getattributes(uinput,context,attributes):
    '''This function marks the entities in user input, and updates
    the attributes dictionary'''
    #Can use context to context specific attribute fetching
    if context.name.startswith('IntentComplete'):
        return attributes, uinput
    else:
        #Code can be optimised here, loading the same files each time suboptimal 
        files = os.listdir('./entities/')
        entities = {}
        for fil in files:
            lines = open('./entities/'+fil).readlines()
            for i, line in enumerate(lines):
                lines[i] = line[:-1]
            entities[fil[:-4]] = '|'.join(lines)

        #Extract entity and update it in attributes dict
        for entity in entities:
            for i in entities[entity].split('|'):
                if i.lower() in uinput.lower():
                    attributes[entity] = i
        for entity in entities:
                uinput = re.sub(entities[entity],r'$'+entity,uinput,flags=re.IGNORECASE)

        #Example of where the context is being used to do conditional branching.
        if context.name=='GetRegNo' and context.active:
            print(attributes)
            match = re.search('[0-9]+', uinput)
            if match:
                uinput = re.sub('[0-9]+', '$regno', uinput)
                attributes['RegNo'] = match.group()
                context.active = False

        return attributes, uinput


# In[ ]:


class Session:
    def __init__(self, attributes=None, active_contexts=[FirstGreeting(), IntentComplete() ]):
        
        '''Initialise a default session'''
        
        #Active contexts not used yet, can use it to have multiple contexts
        self.active_contexts = active_contexts
        
        #Contexts are flags which control dialogue flow, see Contexts.py        
        self.context = FirstGreeting()
        
        #Intent tracks the current state of dialogue
        #self.current_intent = First_Greeting()
        self.current_intent = None
        
        #attributes hold the information collected over the conversation
        self.attributes = {}
        
    def update_contexts(self):
        '''Not used yet, but is intended to maintain active contexts'''
        for context in self.active_contexts:
            if context.active:
                context.decrease_lifespan()

    def reply(self, user_input):
        '''Generate response to user input'''
        
        self.attributes, clean_input = input_processor(user_input, self.context, self.attributes, self.current_intent)
        
        self.current_intent = intentIdentifier(clean_input, self.context, self.current_intent)
        
        prompt, self.context = check_required_params(self.current_intent, self.attributes, self.context)

        #prompt being None means all parameters satisfied, perform the intent action
        if prompt is None:
            if self.context.name!='IntentComplete':
                prompt, self.context = check_actions(self.current_intent, self.attributes, self.context)
        
        #Resets the state after the Intent is complete
        if self.context.name=='IntentComplete':
            self.attributes = {}
            self.context = FirstGreeting()
            self.current_intent = None
        
        return prompt


# In[ ]:


session = Session()

print ('BOT: Hi! How may I assist you?')

while True:
    
    inp = input('User: ')
    print ('BOT:', session.reply(inp))

