#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os 
import openai
import pandas as pd
import numpy as np
import re
from argparse import ArgumentParser

def parseParams():

    arg_parser = ArgumentParser()
    arg_parser.add_argument('-t', '--test', dest='test', type=str)
    arg_parser.add_argument('-k', '--key', dest='key', type=str)

    params = arg_parser.parse_args()
    return params


def getAction(test_mail, key):

    # load train data and extract ID
    train_data = openai.File.create(file=open("train_data_Action.jsonl",encoding="utf-8"), purpose="classifications")
    file_id = train_data['id']
    
    # make for loop and evaulate GPT-3 model for classification
    openai.api_key = key
    completion = openai.Completion()
    action_results = []
    for each_mail in test_mail:
        action_pred = type_classification(each_mail, file_id)
        action_results.append(action_pred)
    
    return action_results


def getPoList(test_mail):

    # regex extract all PO number
    regExp = "(?:BZ)?(?:970|973|977)\\s?[0-9]{1,1}\\s?[0-9]{3,3}\\s?[0-9]{3,3}"

    # make for loop append all PO number in each mail
    test_results = []
    for i in test_mail:
        input_pos = re.findall(regExp, i)
        test_results.append(input_pos)
    return test_results


def getType(test_mail, key):
    
    # filter test data with certain key words.
    regExp = "(\w*liefer\w*)|(\w*endlif\w*)|(\w*schlie\w*)|(\w*schloss\w*)|(\w*öffne\w*)|(\w*sperr\w*)|(\w*lösch\w*)|(\w*areneing\w*)|(\w*haken\w*)|(\s*we-\w*)|(\w*ndrechn\w*)|(\w*rechn\w*)|(erk(?![a-z]))|(elk(?![a-z]))|(\w*berechn\w*)"
    test_key_words = []

    # make for loop and extract key words.
    for i in test_mail:
        input_keywords = re.findall(regExp, input, flags=re.IGNORECASE)
        l = []
        for element in input_keywords:
            l.append(list(filter(None, element))[0])
        input_keywords = ' '.join(l)
        test_key_words.append(str(np.unique(l))[1:-1].replace("'", "").replace(" ",", ").replace("\n", " "))
    
    # load train data and extract ID
    openai.api_key = key
    completion = openai.Completion()
    train_data = openai.File.create(file=open("train_data_Type.jsonl",encoding="utf-8"), purpose="classifications")
    file_id = train_data['id']

    # make for loop and evaulate GPT-3 model for classification
    type_results = []
    for each_mail in test_key_words:
        type_pred = type_classification(each_mail, file_id)
        type_results.append(type_pred)
    
    return type_results


def getPositions(test_mail, key):

    openai.api_key = key
    completion = openai.Completion()

    # make for loop and evaulate GPT-3 model for classification
    position_results = []
    for each_mail in test_mail:
        position_pred = position_unstructure_prediction(each_mail)
        position_results.append(position_pred)
    
    return position_results

# GTP-3 model with classification of action
def action_classification(prompt, file_id):

    res = openai.Classification.create(
        file = file_id,
        query = prompt,
        search_model="ada",
        model="curie",
        max_examples=160
    )
    return res["label"]

# GTP-3 model with classification of type
def type_classification(prompt, file_id):

    respone = openai.Classification.create(
        file = file_id,
        query = prompt,
        model="davinci", 
        max_examples=160,
        temperature = 0
    )

    return respone['label']

# GTP-3 model with prediction of unstructure mail in position 
def position_unstructure_prediction(each_mail):

    # promp for GPT-3
    promp = "text:\nBitte in folgenden Bestellungen das Endrechnungskennzeichen setzen.   9704530974 9704679737   Vielen Dank!\n\nPlease make a table relationship between numbers and positions\n{\"9704530974\":['alle'], \"9704679737\":['alle']}\n\ntext:\nPO's schließen. können Sie bitte folgende PO’s im System schließen? 9704367972 9704608240 9704706320 9704809923\n\nPlease make a table relationship between numbers and positions\n{\"970367972\":['alle'], \"970608240\":['alle'], \"9704706320\":['alle'], \"9704809923\":['alle']}\n\ntext:\n"

    # check input won't out of range of limination of token
    if len(each_mail) > 2000:
        return ""
    else:
        current_prompt = promp + each_mail + \
            "\n\nPlease make a table relationship between numbers and positions\n"
        response = openai.Completion.create(
            engine="davinci",
            prompt=current_prompt,
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"]
        )
        
    results_position = response.choices[0].text

    # predict is not 100% correct with json file, make up some fault
    if results_position[-1] == ".":
        return results_position
    if results_position[-1] != "}" and results_position[-1] != ".":
        if results_position[-2] != "]":
            results_position = results_position+"]}"
        else:
            results_position = results_position+"}"
        results_position = eval(results_position)
    else:
        results_position = eval(results_position)

    return results_position


def main():

    # input data
    params = parseParams()
    input = pd.read_excel(params.test)
    key = params.key

    # create test data with fixed form
    test_mail = []
    for label, i in input.T.iteritems():
        test_mail.append(i['combined_email'].replace("\n", " ").replace('"',""))

    # do function and get output
    poAction = getAction(test_mail, key)
    poList = getPoList(test_mail)
    poType = getType(test_mail, key)
    positions = getPositions(test_mail, key)
    result = {}
    poJsonList = []
    
    # make for loop with json format
    for i in range(len(poList))
        for po in poList[i]:
            poJson = {}
            poJson['PO'] = po
            try:
                poJson['Positions'] = positions[i][po]
            except:
                poJson['Positions'] = ['alle']
            poJson['Action'] = poAction[i]
            poJson['Type'] = poType[i]
            poJsonList.append(poJson)
        result['orders: ' + i] = poJsonList
        
    with open('result.jsonl', 'w') as f:
        f.write(result)
        f.close()

if __name__ == "__main__":
    main()

