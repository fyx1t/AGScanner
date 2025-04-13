from parsers import rules_parser
from json import load
# Import all local checkers:
from checkers.html.checker import check_in_html, get_in_html
from checkers.http.checker import check_in_http, get_in_http

def run(endpoint: str) -> dict:
    output = {}
    """
    
    Main module for loading rules in configs/rules.json, parsing them with parser and checking
    """
    # Loading all rules:
    with open('configs/rules.json', 'r') as rules_file:
        rules_instances = load(rules_file)
    # For every rule parse it and get tokens:
    for rule_instance in rules_instances:
        check_node: rules_parser.Node = rules_parser.get_node(rule_instance['checkrule'])
        url_node: rules_parser.Node = rules_parser.get_node(rule_instance['data']['url'])
        data_node: rules_parser.Node = rules_parser.get_node(rule_instance['data']['data'])
        placeholder_node: rules_parser.Node = rules_parser.get_node(rule_instance['data']['placeholder'])
        # headers_node: rules_parser.Node = rules_parser.get_node(rule_instance['data']['headers'])
        method_node: rules_parser.Node = rules_parser.get_node(rule_instance['data']['method'])

        # Check checktype (HTML, HTTP, API etc...) and start checking:
        if check_node.children[0].value == 'HTML':
            if check_in_html(endpoint, check_node):
                # Add check for every rule (HTML, HTTP, API):
                method = get_in_html(endpoint, method_node)

                # Учитывая. что в HTML мы ищем метод в атрибуте тега, то если его нет, предполагаем, что подразумевается get
                method = method[0] if method else 'GET'

                output[rule_instance['name']] = {
                    "url": get_in_html(endpoint, url_node)[0] if url_node.children else rule_instance['data']['url'],
                    "data": get_in_html(endpoint, data_node) if data_node.children else rule_instance['data']['data'],
                    "placeholder": get_in_html(endpoint, placeholder_node) if placeholder_node.children else rule_instance['data']['placeholder'],
                    "headers": rule_instance['data']['headers'],# "headers": get_in_html(endpoint, headers_node) if headers_node.children else rule_instance['data']['headers'],
                    "method": method if method_node.children else rule_instance['data']['method']
                }
        elif check_node.children[0].value == 'HTTP':
            if check_in_http(endpoint, check_node):
                # Add check for every rule (HTML, HTTP, API):
                output[rule_instance['name']] = {
                    "url": get_in_http(endpoint, url_node) if url_node.children else rule_instance['data']['url'] if rule_instance['data']['url'] != 'SELF' else endpoint,
                    "data": get_in_http(endpoint, data_node) if data_node.children else rule_instance['data']['data'],
                    "placeholder": get_in_http(endpoint, placeholder_node) if placeholder_node.children else rule_instance['data']['placeholder'],
                    "headers": rule_instance['data']['headers'],# "headers": get_in_html(endpoint, headers_node) if headers_node.children else rule_instance['data']['headers'],
                    "method": get_in_http(endpoint, method_node) if method_node.children else rule_instance['data']['method']
                }
        elif check_node.children[0].value == 'API':
            pass
        else:
            raise ValueError('Wrong checktype in rule')
    return output

if __name__ == '__main__':
    pass
