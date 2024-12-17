from bs4 import BeautifulSoup

def check_in_html(endpoint, node) -> bool:
    """
    
    Здесь работают проверочные правила:
    """
    html_data = """
    <html>
        <body>
            <form action="/123">
                <input type="text" name="name">
                <textarea name="comment"></textarea>
            </form>
        </body>
    </html>
    """
    executor = RuleExecutor()
    executor.rule_type = 'CHECK'
    executor.execute(node, html_data)
    return executor.check()

def get_in_html(endpoint, node) -> dict:
    """
    
    Здесь работают захватывающие правила
    """
    html_data = """
    <html>
        <body>
            <form action="/123">
                <input type="text" name="name">
                <textarea name="comment"></textarea>
            </form>
        </body>
    </html>
    """
    executor = RuleExecutor()
    executor.rule_type = 'GRUB'
    node.print_tree()
    executor.execute(node, html_data)
    print(executor.return_data)


class RuleExecutor:
    def __init__(self):
        self.collection = []
        self.htmls = []
        self.rule_type = ''
        self.html_spaces = {}
        self.return_data = {}

    def check(self) -> bool:
        """
        
        Checks if all rule conditions are True or False 
        """
        id = 0
        while id < len(self.collection):
            if type(self.collection[id]) is bool:
                id += 1
                if id < len(self.collection):
                    if type(self.collection[id]) is bool:
                        if not self.collection[id - 1]:
                            return False
                    else:
                        id += 1
                        if self.collection[id - 1] == '|':
                            if not self.collection[id - 2] and not self.collection[id]:
                                return False
                        elif self.collection[id - 1] == '&':
                            if not self.collection[id - 2] or not self.collection[id]:
                                return False
                        id += 1
                else:
                    if not self.collection[id - 1]:
                        return False
            else:
                id += 1
                if self.collection[id - 1] == '|':
                    if not self.collection[id - 1] and not self.collection[id]:
                        return False
                elif self.collection[id - 1] == '&':
                    if not self.collection[id - 1] or not self.collection[id]:
                        return False
        return True

    def execute(self, root, html_data=None):
        """
        
        Метод для выполнения всех правил по дереву узлов
        """
        self.html_spaces[0] = html_data
        self.__execute_node(root, 0)

    def __execute_node(self, node, html_space_level, prev_node=None):
        if node.node_type == 'Root':
            self.__execute_node(node.children[0], html_space_level=html_space_level)
        elif node.node_type == 'SearchType':
            for child in node.children:
                self.__execute_node(child, html_space_level=html_space_level)
        elif node.node_type == 'SearchDetail':
            for child in node.children:
                if child.node_type == 'Entity':
                    self.__execute_node(child, prev_node=node, html_space_level=html_space_level)
                elif child.node_type == 'SearchDetail':
                    for child_child in child.children:
                        self.__execute_node(child_child, prev_node=child, html_space_level=html_space_level+1)
                        if child_child.logic_operator:
                            self.collection.append(child_child.logic_operator)
        
        elif node.node_type == 'Entity':
            self._search_entity(node, prev_node, html_space_level)

    def _search_entity(self, node, prev_node, html_space_level):
        # POKA SPECIALNO BERETSYA TOLKO PERVOE VHOZHDENIE, POTOM DOBAVIT OBRABOTKU VSEH VHOZHDENIY
        if prev_node.value == 'TAG':
            soup = BeautifulSoup(str(self.html_spaces[html_space_level]), 'html.parser')
            self.html_spaces[html_space_level+1] = str(soup.find_all(node.value))
            if self.rule_type == 'CHECK':
                # 2 is because of [] symbols:
                if len(self.html_spaces[html_space_level + 1]) > 2:
                    self.collection.append(True)
                else:
                    self.collection.append(False)
        elif prev_node.value == 'ATRIBUTE':
            soup = BeautifulSoup(str(self.html_spaces[html_space_level]), 'html.parser')
            self.html_spaces[html_space_level+1] = str(soup.find(id='action'))
            if self.rule_type == 'CHECK':
                pass
            elif self.rule_type == 'GRUB':
                pass

if __name__ == '__main__':
    pass
