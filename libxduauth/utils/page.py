def parse_form_hidden_inputs(soup):
    return {
        item.get('name'): item.get('value', '')
        for item in soup.findAll('input', type='hidden')
    }
