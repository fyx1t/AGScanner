import re

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
            '?': r'\?',                # ? - начало конструкции выбора
            '!': r'\!',                # ! - начало конструкции захвата
            '%': r'\%',                # % - уточнение для поля поиска
            '/': r'/',                 # / - сущность поиска
            '|': r'\|',                # | - логическое ИЛИ
            '&': r'\&',                # + - логическое И
            '+': r'\+',                # + - вхождение вглубь дерева
            '[A-Za-z*-]+': r'[A-Za-z*-]+'  # идентификаторы: HTML, TAG, form, input и т.д.
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

        # По дефолту ставим, что правило является поисковым:
        rule_type = 'FIND'

        while idx < len(tokens):
            token = tokens[idx]

            if token == '?' or token == '!':
                # Если токен !, то меняем тип правила на захват:
                if token == '!':
                    rule_type = 'GRIP'
                # Следующий токен - тип поиска (HTML, HTTP, API)
                idx += 1
                if idx < len(tokens):
                    search_type = tokens[idx]
                    current_node = Node('SearchType', search_type)
                    stack[-1].add_child(current_node)
                    stack.append(current_node)
                else:
                    raise ValueError("Expected search type after ? symbol.")
            
            elif token == '%':
                # Следующий токен - тип уточнения (TAG, KEYWORD, ATRIBUTE и т.д.)
                idx += 1
                if idx < len(tokens) or rule_type == 'GRIP':
                    search_detail = tokens[idx]
                    current_node = Node('SearchDetail', search_detail)
                    stack[-1].add_child(current_node)
                    stack.append(current_node)
                else:
                    raise ValueError("Expected search detail after '%' symbol.")

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
                    if tokens[idx] == '%':
                        idx -= 1
                    else:
                        raise ValueError("Expected '%' symbol after + symbol.")
                else:
                    raise ValueError("Expected '%' symbol after + symbol.")

            elif token == '|':
                # Следующий токен - еще одно условие для предыдущей ноды с правилом ИЛИ
                idx += 1
                if idx < len(tokens):
                    if tokens[idx] == '%':
                        idx -= 1
                    else:
                        raise ValueError("Expected '%' symbol after + symbol.")
                else:
                    raise ValueError("Expected '%' symbol after + symbol.")
            
            elif token == '&':
                # Следующий токен - еще одно условие для предыдущей ноды с правилом И
                idx += 1
                if idx < len(tokens):
                    if tokens[idx] == '%':
                        idx -= 1
                    else:
                        raise ValueError("Expected '%' symbol after + symbol.")
                else:
                    raise ValueError("Expected '%' symbol after + symbol.")
            
            else:
                # Неопознанные токены — идентификаторы
                pass
            
            # Завершаем текущий узел, если можно
            if idx + 1 < len(tokens):
                # Только если следующий токен не является частью текущего узла
                if tokens[idx + 1] not in ['?','%','/']:
                    # Если следующего токена нет, значит нужно вернуть родителя
                    if len(stack) > 1:  # Не удаляем корневой узел
                        stack.pop()
            idx += 1

        return root


def get_node(rule: str) -> Node:
    return RuleParser().parse(rule)

if __name__ == '__main__':
    pass
