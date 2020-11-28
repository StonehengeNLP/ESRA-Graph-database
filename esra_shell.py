import cmd
from os import system
from src.graph_database import GraphDatabase


INTRO = """
 _____ ____  ____      _      ____  _          _ _           _
| ____/ ___||  _ \    / \    / ___|| |__   ___| | | __   __ / |
|  _| \___ \| |_) |  / _ \   \___ \| '_ \ / _ \ | | \ \ / / | |
| |___ ___) |  _ <  / ___ \   ___) | | | |  __/ | |  \ V /  | |
|_____|____/|_| \_\/_/   \_\ |____/|_| |_|\___|_|_|   \_/   |_|
"""

class EsraShell(cmd.Cmd):
    
    intro = INTRO + "\nWelcome to the graph_search command line.\n"
    prompt = '(esra) '
    
    def __init__(self):
        super().__init__()
        self.graph_database = GraphDatabase()
        
    def emptyline(self):
         pass
        
    def do_clear(self, line):
        'Clear screen'
        system('clear')
    
    def do_exit(self,*args):
        return True
        
    def do_search(self, line):
        'Search scientific papers by using keyword(s)'
        line = line.replace('_', ' ')
        results = self.graph_database.search(line)
        for i in results[:10]:
            print(*i)
            
    def complete_search(self, text, line, start_index, end_index):
        if text:
            text = text.replace('_', ' ')
            out = self.graph_database.text_autocomplete(text)
            if len(out) == 0:
                out = self.graph_database.text_correction(text)
            out = [i.replace(' ', '_') for i in out]
            return out
        return []     

if __name__ == '__main__':
    esra_shell = EsraShell()
    esra_shell.cmdloop()