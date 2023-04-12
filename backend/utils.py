def replace_empty_epreuve(d):
    """
    Replace empty 'epreuve' fields with the same value from other subdicts with the same 'date'
    """
    # Create a dict where the keys are the 'date' values and the values are a list of subdictionaries with that 'date'
    date_to_subdicts = {}
    for subdict in d['list']:
        for journee in subdict['journees']:
            date = journee['date']
            if date not in date_to_subdicts:
                date_to_subdicts[date] = []
            date_to_subdicts[date].append(journee)

    # For each 'date' with multiple subdictionaries, iterate through them and find the first non-empty 'epreuve' field
    for subdicts in date_to_subdicts.values():
        epreuve = None
        for subdict in subdicts:
            if subdict['epreuve'] != '':
                epreuve = subdict['epreuve']
                break

        # Replace any empty 'epreuve' fields with the value of the first non-empty 'epreuve' field
        for subdict in subdicts:
            if subdict['epreuve'] == '':
                subdict['epreuve'] = epreuve

    # Create a dictionary to store the matches by epreuve and date
    matches_by_epreuve_and_date = {}

    for block in d['list']:
        for journee in block['journees']:
            for match in journee['matchs']:
                epreuve = journee['epreuve']
                date = journee['date']
                if epreuve and date:
                    if (epreuve, date) not in matches_by_epreuve_and_date:
                        matches_by_epreuve_and_date[(epreuve, date)] = {
                            'processed': block['processed'],
                            'epreuve': epreuve,
                            'date': date,
                            'matchs': [match]
                        }
                    else:
                        matches_by_epreuve_and_date[(epreuve, date)]['matchs'].append(match)

    # Create a list of dictionaries from the dictionary of matches by epreuve and date
    grouped_matches = {'list': [
        {'processed': 0, 'journees': []},  # processed: 0
        {'processed': 1, 'journees': []},  # processed: 1
    ]}
    for match_dict in matches_by_epreuve_and_date.values():
        grouped_matches['list'][match_dict['processed']]['journees'].append({
            'epreuve': match_dict.get('epreuve'),
            'date': match_dict.get('date'),
            'matchs': match_dict.get('matchs')
        })
    return grouped_matches
