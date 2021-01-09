import nltk
from nltk.tokenize import sent_tokenize 

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
  
import re
import torch
import language_tool_python
from transformers import pipeline
from .graph_database import GraphDatabase


gdb = GraphDatabase()

device = 0 if torch.cuda.is_available() else -1
bart_base = pipeline("summarization", model='t5-small', device=device)

tool = language_tool_python.LanguageTool('en-US')


def is_include_word(word, text):
    """ 
    return true if the word is included in the text
    
    I have handled plural cases by adding just 's' and 'es'
    you could make it smarter :D
    """
    return re.search(r'\b{}(s|es){{0,1}}\b'.format(word), text, flags=re.IGNORECASE)

def count_word(text):
    """
    return number of English word exists in the given text 
    """
    return len(re.findall('\w+', text))

def filtered_summarization(keys, title, abstract):
    """
    This explanation method is to filter some sentences that include keyword(s)
    and then throw it into summarization model (we use t5-small in this case)
    so, we will get our explanation that based on entities in the path from keywords to paper
    Although it looks like summarization, it is also explanation of the local graph as well.
    """
    
    nodes = gdb.get_related_nodes(keys, title)
    
    sentences = sent_tokenize(abstract)
    
    selected_sentence = []
    for sentence in sentences:
        for name in nodes + keys:
            if is_include_word(name, sentence):
                selected_sentence += [sentence]
                break
            
    new_sentence = ' '.join(selected_sentence)
    word_count = count_word(new_sentence)

    if word_count > 10:
        min_length = min(50, word_count)
        summ = bart_base(new_sentence, max_length=70, min_length=min_length)[0]['summary_text']
        summ = tool.correct(summ)
    else:
        summ = ''
        
    return summ