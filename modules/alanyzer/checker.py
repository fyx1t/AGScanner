from bs4 import BeautifulSoup
from helpers import make_request, check_csrf_presense
from json import load
from modules.alanyzer import parser


class __BaseCheck:
    def __init__(self):
        self.collection = []
        self.htmls = []
        self.rule_type = ''
        self.return_data = []
        self.need_to_check = False

    def work(self, endpoint: str, rule_type: str):
        # Обновляем данные:
        self.update()

        with open('configs/main.json', 'r') as configs_file:
            domain = load(configs_file)['domain']
        self.rule_type = rule_type

        return make_request('GET', domain + endpoint)
    
    def update(self) -> None:
        # Обновление стандартных данных:
        self.collection = []
        self.htmls = []
        self.rule_type = ''
        self.return_data = []
        self.need_to_check = False

        # Обновление данных, если они есть:
        if hasattr(self, 'response'):
            self.response = None

        if hasattr(self, 'header_name'):
            self.header_name = ''

        if hasattr(self, 'html_spaces'):
            self.html_spaces = {}

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


class HTMLCheck(__BaseCheck):
    def __init__(self):
        super().__init__()
        self.html_spaces = {}
    
    def work(self, endpoint, node, rule_type):
        response = super().work(endpoint, rule_type)
        self.execute(node, response.content.decode())

        return self.return_data if rule_type == 'GRUB' else self.check()

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
        global CSRF
        if prev_node.value == 'TAG':
            soup = BeautifulSoup(str(self.html_spaces[html_space_level]), 'html.parser')
            if '*' in node.value:
                self.html_spaces[html_space_level+1] = ''
                for value in node.value.split('*'):
                    if str(soup.find_all(value)) != '[]':

                        # Проверяем, есть ли среди названий тегов что-то связанное с csrf (чтобы сохранить значение csrf токена):
                        csrf = check_csrf_presense(soup.find_all(value))
                        if csrf:
                            CSRF = csrf

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
        elif prev_node.value == 'ATTRIBUTE':
            if '|#|' in str(self.html_spaces[html_space_level]):
                splitted_html_spaces = str(self.html_spaces[html_space_level]).split('|#|')
                del splitted_html_spaces[-1]
                for splitted_html_space in splitted_html_spaces:
                    soup = BeautifulSoup(splitted_html_space, 'html.parser')
                    data = soup.find().attrs
                    if self.rule_type == 'CHECK':
                        pass
                    elif self.rule_type == 'GRUB':
                        pass
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
        elif prev_node.value == 'CONTAINS':
            # Чтобы если до этого были найдены данные, они нам не нужны, а нужны данные только в новой области поиска:
            self.return_data = []
            # Здесь используем html_space_level-1, так как вы не создаем новую область поиска, а всего лишь ищем текст в предыдущей:
            soup = BeautifulSoup(str(self.html_spaces[html_space_level-1]), 'html.parser')

            if self.rule_type == 'CHECK':
                found = False
                # Все значения пока статические, но обязательно нужно смотреть области поиска:
                for tag in soup.find_all('a'):
                    if node.value.replace("'", '') in tag.attrs['href']:
                        self.collection.append(True)
                        found = True
                        break
                
                if not found:
                    self.collection.append(False)
            else:
                self.html_spaces[html_space_level] = ''
                for tag in soup.find_all('a'):
                    if node.value.replace("'", '') in tag.attrs['href']:
                        self.return_data.append(tag.attrs['href'])
                        self.html_spaces[html_space_level] += str(tag) + '|#|'
                self.html_spaces[html_space_level] = self.html_spaces[html_space_level].replace(', ', '|#|')

        elif prev_node.value == 'PARAMETER':
            # Чтобы если до этого были найдены данные, они нам не нужны, а нужны данные только в новой области поиска:
            self.return_data = []
            soup = BeautifulSoup(str(self.html_spaces[html_space_level-1]), 'html.parser')
            for tag in soup.find_all('a'):
                data = tag.attrs['href']
                for parameter in data.split('?')[1].split('&'):
                    self.return_data.append(parameter.split('=')[0])
                # Временный return, потому что пока фаззер не умеет фаззить несколько одинаковых конструкций:
                return


class HTTPCheck(__BaseCheck):
    def __init__(self):
        super().__init__()
        self.header_name = ''
        self.response = None
    
    def work(self, endpoint, node, rule_type):
        response = super().work(endpoint, rule_type)
        self.execute(node, response)

        return self.return_data if rule_type == 'GRUB' else self.check()

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


class Checker:
    """
    Класс, ответственный за анализ полученного ресурса тестируемой системы на предмет наличия в нем
    определенных конструкций, описанных в правилах (предварительно преобразованных в ноды). 
    Каждая конструкция ищется в ресурсе и, если находится, сохраняется. В итоге это все отдается на выходе.
    Каждое правило реализуется в ноды за счет взаимодействия с интерфейсом RuleParser через вызовы функции
    get_node модуля parser
    """
    def __init__(self):
        pass

    def html_check():
        pass

    def http_check():
        pass

    def run(self, endpoint: str) -> dict:
        html_checker = HTMLCheck()
        http_checker = HTTPCheck()

        output = {}
        """
        
        Main module for loading rules in configs/rules.json, parsing them with parser and checking
        """
        # Loading all rules:
        with open('configs/rules.json', 'r') as rules_file:
            rules_instances = load(rules_file)
        # For every rule parse it and get tokens:
        for rule_instance in rules_instances:
            check_node: parser.Node = parser.get_node(rule_instance['checkrule'])
            url_node: parser.Node = parser.get_node(rule_instance['data']['url'])
            data_node: parser.Node = parser.get_node(rule_instance['data']['data'])
            placeholder_node: parser.Node = parser.get_node(rule_instance['data']['placeholder'])
            # headers_node: parser.Node = parser.get_node(rule_instance['data']['headers'])
            method_node: parser.Node = parser.get_node(rule_instance['data']['method'])

            # Check checktype (HTML, HTTP, API etc...) and start checking:
            if check_node.children[0].value == 'HTML':
                if html_checker.work(endpoint, check_node, 'CHECK'):
                    # Add check for every rule (HTML, HTTP, API):
                    if not method_node.children:
                        method = rule_instance['data']['method']
                    else:
                        method = html_checker.work(endpoint, method_node, 'GRUB')[0]

                    url = html_checker.work(endpoint, url_node, 'GRUB')
                    if len(url) > 0:
                        url = url[0]

                    print(html_checker.work(endpoint, method_node, 'GRUB'))

                    output[rule_instance['name']] = {
                        "url": url if url_node.children else rule_instance['data']['url'] if rule_instance['data']['url'] != 'SELF' else endpoint,
                        "data": html_checker.work(endpoint, data_node, 'GRUB') if data_node.children else rule_instance['data']['data'],
                        "placeholder": html_checker.work(endpoint, placeholder_node, 'GRUB') if placeholder_node.children else rule_instance['data']['placeholder'],
                        "headers": rule_instance['data']['headers'],# "headers": get_in_html(endpoint, headers_node) if headers_node.children else rule_instance['data']['headers'],
                        "method": method if method_node.children else rule_instance['data']['method']
                    }

            elif check_node.children[0].value == 'HTTP':
                if http_checker.work(endpoint, check_node, 'CHECK'):
                    # Add check for every rule (HTML, HTTP, API):
                    output[rule_instance['name']] = {
                        "url": http_checker.work(endpoint, url_node, 'GRUB') if url_node.children else rule_instance['data']['url'] if rule_instance['data']['url'] != 'SELF' else endpoint,
                        "data": http_checker.work(endpoint, data_node, 'GRUB') if data_node.children else rule_instance['data']['data'],
                        "placeholder": http_checker.work(endpoint, placeholder_node, 'GRUB') if placeholder_node.children else rule_instance['data']['placeholder'],
                        "headers": rule_instance['data']['headers'],# "headers": get_in_html(endpoint, headers_node) if headers_node.children else rule_instance['data']['headers'],
                        "method": http_checker.work(endpoint, method_node, 'GRUB') if method_node.children else rule_instance['data']['method']
                    }
            elif check_node.children[0].value == 'API':
                pass
            else:
                raise ValueError('Wrong checktype in rule')
        return output


if __name__ == '__main__':
    pass
