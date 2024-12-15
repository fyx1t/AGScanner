from json import load
import re
from bs4 import BeautifulSoup

def check_rules(endpoint: str, tokens: list) -> list:
    # Пример использования:
    accepted_rules = []
    html_data = ["""
    <html>
        <body>
            <form action="/123">
                <input type="text" name="name">
                <textarea name="comment"></textarea>
            </form>
        </body>
    </html>
    """]
    for node in tokens:
        executor = RuleExecutor()
        executor.execute(node['tokens'], html_data)
        if executor.check():
            accepted_rules.append([node['rule_name'], str(executor.htmls).replace('[', '').replace(']', '')])
    return accepted_rules

def get_tokens() -> list:
    tokens: list = []
    # Пример использования:
    with open('configs/rules.json', 'r') as rules_file:
        rules: list = load(rules_file)
    for rule in rules:
        parser = RuleParser()
        node = parser.parse(rule['checkrule'])
        tokens.append({'rule_name': rule['name'], 'tokens': node})
    return tokens

class Node:
    def __init__(self, node_type, value=None):
        self.node_type = node_type  # Тип узла (HTML, TAG, KEYWORD, etc.)
        self.value = value          # Значение (например, 'form', 'input')
        self.children = []          # Дочерние узлы
        self.logic_operator = None  # Логический оператор: AND (&) или OR (|)

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"Node({self.node_type}, {self.value})"
    
    def print_tree(self, level=0):
        print(" " * (level * 2) + f"{self.node_type}: {self.value}")
        for child in self.children:
            child.print_tree(level + 1)
            if child.logic_operator:
                print(" " * (level * 2) + child.logic_operator)


class RuleParser:
    def __init__(self):
        self.token_patterns = {
            '$': r'\$',  # $ - начало поля поиска
            '?': r'\?',  # ? - уточнение поиска
            '/': r'/',    # / - разделитель для сущности
            '|': r'\|',   # | - логическое ИЛИ
            '&': r'\&',   # & - логическое И
            '+': r'\+',   # + - вхождение вглубь дерева
            '[A-Za-z]+': r'[A-Za-z]+'  # идентификаторы: HTML, TAG, form, input и т.д.
        }
        self.tokenizer = re.compile('|'.join(self.token_patterns.values()))

    def tokenize(self, rule):
        return [match.group(0) for match in self.tokenizer.finditer(rule)]

    def parse(self, rule):
        tokens = self.tokenize(rule)
        root = Node('Root')  # Корень дерева

        current_node = None
        stack = [root]  # Стек должен всегда содержать хотя бы корневой узел
        
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]

            if token == '$':
                # Следующий токен - тип поиска (HTML, HTTP, API)
                idx += 1
                if idx < len(tokens):
                    search_type = tokens[idx]
                    current_node = Node('SearchType', search_type)
                    stack[-1].add_child(current_node)
                    stack.append(current_node)
                else:
                    raise ValueError("Expected search type after $ symbol.")
            
            elif token == '?':
                # Следующий токен - тип уточнения (TAG, KEYWORD, и т.д.)
                idx += 1
                if idx < len(tokens):
                    search_detail = tokens[idx]
                    current_node = Node('SearchDetail', search_detail)
                    stack[-1].add_child(current_node)
                    stack.append(current_node)
                else:
                    raise ValueError("Expected search detail after ? symbol.")

            elif token == '/':
                # Следующий токен - сущность поиска (например, form, input, textarea)
                idx += 1
                if idx < len(tokens):
                    entity = tokens[idx]
                    current_node = Node('Entity', entity)
                    stack[-1].add_child(current_node)
                    if idx + 1 < len(tokens):
                        if tokens[idx + 1] == '+':
                            stack.append(current_node)
                        elif tokens[idx + 1] == '|':
                            current_node.logic_operator = '|'
                        elif  tokens[idx + 1] == '&':
                            current_node.logic_operator = '&'
                        else:
                            raise ValueError('Expected +, | or & after SearchDetail value')
                else:
                    raise ValueError("Expected entity after / symbol.")
            
            elif token == '+':
                # Следующий токен - вхождение вглубь дерева, то есть должен быть токен ?
                idx += 1
                if idx < len(tokens):
                    if tokens[idx] == '?':
                        idx -= 1
                    else:
                        raise ValueError("Expected ? symbol after + symbol.")
                else:
                    raise ValueError("Expected ? symbol after + symbol.")

            elif token == '|':
                # Следующий токен - еще одно условие для предыдущей ноды с правилом ИЛИ
                idx += 1
                if idx < len(tokens):
                    if tokens[idx] == '?':
                        idx -= 1
                    else:
                        raise ValueError("Expected ? symbol after + symbol.")
                else:
                    raise ValueError("Expected ? symbol after + symbol.")
            
            elif token == '&':
                # Следующий токен - еще одно условие для предыдущей ноды с правилом И
                idx += 1
                if idx < len(tokens):
                    if tokens[idx] == '?':
                        idx -= 1
                    else:
                        raise ValueError("Expected ? symbol after + symbol.")
                else:
                    raise ValueError("Expected ? symbol after + symbol.")
            
            else:
                # Неопознанные токены — идентификаторы
                pass
            
            # Завершаем текущий узел, если можно
            if idx + 1 < len(tokens):
                # Только если следующий токен не является частью текущего узла
                if tokens[idx + 1] not in ['$','?','/']:
                    # Если следующего токена нет, значит нужно вернуть родителя
                    if len(stack) > 1:  # Не удаляем корневой узел
                        stack.pop()
            idx += 1

        return root


class RuleExecutor:
    def __init__(self):
        self.collection = []
        self.htmls = []

    def check(self):
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
        self._execute_node(root, html_data)

    def _execute_node(self, node, html_data=None):
        # Обработка узлов дерева
        if node.node_type == 'Root':
            # Это корень, просто начинаем обработку всех дочерних элементов
            self._execute_node(node.children[0], html_data)
            # results = [self._execute_node(child, html_data) for child in node.children]
            # return results
        
        elif node.node_type == 'SearchType':
            if node.value == 'HTML':
                # Загружаем HTML-страницу для обработки
                if html_data:
                    for child in node.children:
                        self._execute_node(child, html_data)
                    # return data
            elif node.value == 'HTTP':
                # Логика для обработки HTTP-данных
                pass  # Здесь будет логика для HTTP
            elif node.value == 'API':
                # Логика для обработки API-ответов
                pass  # Здесь будет логика для API

        elif node.node_type == 'SearchDetail':
            # Ищем в HTML-тегах или других деталях
            if node.value == 'TAG':
                for child in node.children:
                    if child.node_type == 'Entity':
                        html_data, state = self._execute_node(child, html_data)
                        self.collection.append(state)
                        self.htmls.append(html_data)
                    elif child.node_type == 'SearchDetail':
                        for child_child in child.children:
                            self.collection.append(self._execute_node(child_child, html_data)[1])
                            if child_child.logic_operator:
                                self.collection.append(child_child.logic_operator)

        elif node.node_type == 'Entity':
            found = self._search_entity(node, html_data)
            if found[0]:
                return found, True
            return found, False
            # return self._search_entity(node, html_data)
        
        elif node.logic_operator:
            # Логические операторы (И/ИЛИ)
            return self.logic_operators[node.logic_operator](html_data)
        return None

    def _search_html(self, html_data, node):
        # Если тип поиска - HTML, выполняем поиск в HTML
        for html_found in html_data:
            soup = BeautifulSoup(html_found, 'html.parser')
            results = []
            for child in node.children:
                if child.node_type == 'SearchDetail' and child.value == 'TAG':
                    for child_child in child.children:
                        for tag in soup.find_all(child_child.value):
                            results.append(tag)
        return results

    def _search_entity(self, node, html_data):
        found = []
        for html_found in html_data:
            soup = BeautifulSoup(str(html_found), 'html.parser')
            found.append(soup.find_all(node.value))
        return found


if __name__ == '__main__':
    pass
