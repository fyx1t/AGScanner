def get_data(rule: str, html: str, placeholder: str):
    # ПЕРЕДЕЛАТЬ:
    if rule.startswith('IN{'):
        if rule == 'IN{TAG=[input]~IN{TAG=[*]~IN{DATA}}}':
            return 'text=%&number=%&database=%'

if __name__ == '__main__':
    pass
