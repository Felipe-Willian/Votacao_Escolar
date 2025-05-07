from collections import Counter


def generate_chart_data(votes):
    options = [v['option'] for v in votes]
    count = Counter(options)
    return {
        'labels': list(count.keys()),
        'data': list(count.values())
    }