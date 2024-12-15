def get_method(rule: str, html: str):
    # ПЕРЕДЕЛАТЬ:
    if rule.startswith('IN{'):
        if rule == 'IN{TAG=[form]~IN{ATRIBUTE=[method]}}':
            return 'POST'

if __name__ == '__main__':
    pass
