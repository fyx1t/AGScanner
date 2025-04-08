from helpers import make_request
from json import load

def check_in_http(endpoint, node) -> bool:
    """
    
    Здесь работают проверочные правила:
    """
    with open('configs/main.json', 'r') as configs_file:
        domain = load(configs_file)['domain']
    response = make_request('GET', domain + endpoint)
    response.headers = {k.lower(): v.lower() if isinstance(v, str) else v for k, v in response.headers.items()}
    executor = RuleExecutor()
    executor.rule_type = 'CHECK'
    executor.execute(node, response)
    return executor.check()

def get_in_http(endpoint, node) -> dict:
    """
    
    Здесь работают захватывающие правила
    """
    with open('configs/main.json', 'r') as configs_file:
        domain = load(configs_file)['domain']
    response = make_request('GET', domain + endpoint)
    executor = RuleExecutor()
    executor.rule_type = 'GRUB'
    executor.execute(node, response)
    return executor.return_data


class RuleExecutor:
    def __init__(self):
        self.collection = []
        self.htmls = []
        self.rule_type = ''
        self.return_data = []
        self.need_to_check = False
        self.response = None
        self.header_name = ''

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

    def execute(self, root, response=None):
        """
        
        Метод для выполнения всех правил по дереву узлов
        """
        self.response = response
        self.__execute_node(root)

    def __execute_node(self, node, prev_node=None):
        if node.node_type == 'Root':
            self.__execute_node(node.children[0])
        elif node.node_type == 'SearchType':
            for child in node.children:
                self.__execute_node(child)
        elif node.node_type == 'SearchDetail':
            for child in node.children:
                if child.node_type == 'Entity':
                    self.__execute_node(child, prev_node=node)
                else:
                    self.__execute_node(child, prev_node=node)
        elif node.node_type == 'Entity':
            self._search_entity(node, prev_node)
        if node.logic_operator:
            self.collection.append(node.logic_operator)
            self.need_to_check = True

    def _search_entity(self, node, prev_node):
        if prev_node.value == 'HEADER':
            if self.rule_type == 'CHECK':
                if node.value.lower() in self.response.headers.keys():
                    self.collection.append(True)
                    self.header_name = node.value.lower()
                else:
                    self.collection.append(False)
        elif prev_node.value == 'DATA':
            pass
        elif prev_node.value == 'VALUE':
            if self.rule_type == 'CHECK':
                if self.header_name in [key for key in self.response.headers.keys()]:
                    if node.value.lower() in self.response.headers[self.header_name]:
                        self.collection.append(True)
                    else:
                        self.collection.append(False)


if __name__ == '__main__':
    pass
