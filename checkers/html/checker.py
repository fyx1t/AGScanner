from bs4 import BeautifulSoup

def check_in_html(endpoint, node) -> bool:
    """
    
    Здесь работают проверочные правила:
    """
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
    executor.execute(node, html_data)
    return executor.check()

def get_in_html(endpoint, node) -> dict:
    """
    
    Здесь работают захватывающие правила
    """
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
    node.print_tree()
    executor.execute(node, html_data)
    print('--')


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

executor = RuleExecutor()

if __name__ == '__main__':
    pass
