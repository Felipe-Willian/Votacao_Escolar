from collections import Counter

def generate_chart_data(votes):
    opts = [v['option'] for v in votes]
    cnts = Counter(opts)
    return {'labels': list(cnts.keys()), 'data': list(cnts.values())}