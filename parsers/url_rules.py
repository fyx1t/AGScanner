def get_url(rule: str, html: str):
    # ПЕРЕДЕЛАТЬ:
    if rule.startswith('IN{'):
        if rule == 'IN{TAG=[form]~IN{ATRIBUTE=[action]}}':
            return '/'

if __name__ == '__main__':
    pass
