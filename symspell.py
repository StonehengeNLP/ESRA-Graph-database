import pickle
import pandas as pd
from src.graph_database import GraphDatabase
from symspellpy import SymSpell, Verbosity
from collections import Counter

entity_types = ['Task','Method','Metric','OtherScientificTerm',
                'Abbreviation','Material']



def create_corpus():
    """
        create corpus
    """
    graph_database = GraphDatabase()

    nodes = []
    for ent_type in entity_types:
        nodes += graph_database.get_all_entities(ent_type)

    # win's 
    entities_all_name = []
    for node in nodes:
        entities_all_name.append(node.name.replace(" ", "_").strip("_"))

    with open("tmp.txt", "w") as f:
        for ent_name in entities_all_name:
            f.write(ent_name + " ")
    
    symspell = SymSpell(max_dictionary_edit_distance=5)
    symspell.create_dictionary("tmp.txt")
    
    #save dict to corpus
    d = symspell.words
    with open("corpus.txt", "w") as f:
        for k,v in d.items():
            f.write(k + "," + str(v) + "\n")


def spell_correction(input_term):
    """
        create suggestions
    """
    symspell = SymSpell(max_dictionary_edit_distance=5)
    symspell.load_dictionary("corpus.txt",0,1,",","utf-8")
    suggestions = symspell.lookup_compound(input_term, max_edit_distance=5)

    for suggestion in suggestions:
        print(suggestion.term)

if __name__ == "__main__":
    # create corpus 
    # create_corpus()

    # get suggestion
    spell_correction("macpnr leerning")