from collections import Counter

def generate_chart_data(votes):
    cnts = Counter(v['option'] for v in votes)
    return {'labels': list(cnts), 'data': list(cnts.values())}