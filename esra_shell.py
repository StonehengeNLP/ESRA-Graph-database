import cmd
import time
from os import system
from src import graph_search as gs


INTRO = \
"""
                 _____ ____  ____      _     
                | ____/ ___||  _ \    / \    
                |  _| \___ \| |_) |  / _ \   
                | |___ ___) |  _ <  / ___ \  
                |_____|____/|_| \_\/_/   \_\ 
  ____                 _       ____                      _
 / ___|_ __ __ _ _ __ | |__   / ___|  ___  __ _ _ __ ___| |__
| |  _| '__/ _` | '_ \| '_ \  \___ \ / _ \/ _` | '__/ __| '_ \ 
| |_| | | | (_| | |_) | | | |  ___) |  __/ (_| | | | (__| | | |
 \____|_|  \__,_| .__/|_| |_| |____/ \___|\__,_|_|  \___|_| |_|
                |_|
"""

class EsraShell(cmd.Cmd):
    
    intro = INTRO + "\nWelcome to the ESRA's graph search command line.\n"
    prompt = '(esra) '
    
    def __init__(self):
        super().__init__()
        
    def emptyline(self):
         pass
        
    def do_clear(self, line):
        """Clear screen"""
        system('clear')
    
    def do_exit(self,*args):
        """Quit the program"""
        return True
        
    def do_search(self, line):
        """Search scientific papers by using keyword(s)"""
        keywords = gs.text_preprocessing(line)
        t = time.time()
        r = gs.search(keywords, mode='popularity')
        print('Time:', time.time() - t, 's')
        for i in r:
            print(*i, sep=' \t')
                        
    def complete_search(self, text, line, start_index, end_index):
        if text:
            tokenized_text = line.split()[1:]
            for i in range(len(tokenized_text)):
                temp_text = ' '.join(tokenized_text[i:])
                out = gs.text_autocomplete(temp_text)
                if out:
                    n_skip = temp_text.count(' ')
                    out = [' '.join(word.split()[n_skip:]) for word in out]
                    break
            else:
                corrected = gs.text_correction(text)
                out = [corrected[0]]
            return out
        return []
    

if __name__ == '__main__':
    esra_shell = EsraShell()
    # esra_shell.cmdloop()

    search_text = 'bert natural language processing attention'
    print('Search text:', search_text)
    keywords = gs.text_preprocessing(search_text)
    print(keywords)

    # x = get_related_word(keywords)
    # print(x)
    
    # # PageRank
    # t = time.time()
    # r = gs.search(keywords, mode='pagerank')
    # print('Time:', time.time() - t, 's')
    # for i in r:
    #     print(i)
        
    # # BM25
    # t = time.time()
    # r = gs.search(keywords, mode='bm25')
    # print('Time:', time.time() - t, 's')
    # for i in r:
    #     print(i)
        
    # # Popularity
    # t = time.time()
    # r = gs.search(keywords, mode='popularity')
    # print('Time:', time.time() - t, 's')
    # for i in r:
    #     print(i)
    
    # for i in r[:3]:
    #     print(gs.explain(keywords, i[2], mode='template'))