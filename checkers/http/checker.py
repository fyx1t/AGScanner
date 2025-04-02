from helpers import make_request
from json import load

def check_in_http(endpoint, node) -> bool:
    """
    
    Здесь работают проверочные правила:
    """
    with open('configs/main.json', 'r') as configs_file:
        domain = load(configs_file)['domain']
    html_data = make_request('GET', domain + endpoint).content.decode()
    executor = RuleExecutor()
    executor.rule_type = 'CHECK'
    executor.execute(node, html_data)
    node.print_tree()
    print(executor.collection)
    print(executor.check())
    return executor.check()

def get_in_http(endpoint, node) -> dict:
    """
    
    Здесь работают захватывающие правила
    """
    with open('configs/main.json', 'r') as configs_file:
        domain = load(configs_file)['domain']
    html_data = make_request('GET', domain + endpoint).content.decode()
    executor = RuleExecutor()
    executor.rule_type = 'GRUB'
    executor.execute(node, html_data)
    return executor.return_data


class RuleExecutor:
    def __init__(self):
        self.collection = []
        self.htmls = []
        self.rule_type = ''
        self.html_spaces = {}
        self.return_data = []
        self.need_to_check = False

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
                else:
                    self.__execute_node(child, prev_node=node, html_space_level=html_space_level+1)
        elif node.node_type == 'Entity':
            self._search_entity(node, prev_node, html_space_level)
        if node.logic_operator:
            self.collection.append(node.logic_operator)
            self.need_to_check = True

    def _search_entity(self, node, prev_node, html_space_level):
        if prev_node.value == 'TAG':
            soup = BeautifulSoup(str(self.html_spaces[html_space_level]), 'html.parser')
            if '*' in node.value:
                self.html_spaces[html_space_level+1] = ''
                for value in node.value.split('*'):
                    if str(soup.find_all(value)) != '[]':
                        self.html_spaces[html_space_level+1] += str(soup.find_all(value)) + '|#|'
                self.html_spaces[html_space_level+1] = self.html_spaces[html_space_level+1].replace(', ', '|#|')
            else:
                self.html_spaces[html_space_level+1] = str(soup.find_all(node.value))
            if self.rule_type == 'CHECK':
                # 2 is because of [] symbols:
                if len(self.html_spaces[html_space_level + 1]) > 2:
                    self.collection.append(True)
                else:
                    self.collection.append(False)
                if self.need_to_check:
                    arg_1 = self.collection[-3]
                    arg_2 = self.collection[-1]
                    operator = self.collection[-2]
                    self.collection = self.collection[:-3]
                    if operator == '|':
                        self.collection.append(arg_1 or arg_2)
                    elif operator == '&':
                        self.collection.append(arg_1 and arg_2)
                    self.need_to_check = False
        elif prev_node.value == 'ATRIBUTE':
            if '|#|' in str(self.html_spaces[html_space_level]):
                splitted_html_spaces = str(self.html_spaces[html_space_level]).split('|#|')
                del splitted_html_spaces[-1]
                for splitted_html_space in splitted_html_spaces:
                    soup = BeautifulSoup(splitted_html_space, 'html.parser')
                    data = soup.find().attrs
                    if self.rule_type == 'CHECK':
                        pass
                    elif self.rule_type == 'GRUB':
                        if data and node.value in [*data.keys()]:
                            self.return_data.append(data[node.value])
            else:
                soup = BeautifulSoup(str(self.html_spaces[html_space_level]), 'html.parser')
                data = soup.find().attrs
                if self.rule_type == 'CHECK':
                    pass
                elif self.rule_type == 'GRUB':
                    if data and node.value in [*data.keys()]:
                        self.return_data.append(data[node.value])

if __name__ == '__main__':
    pass
