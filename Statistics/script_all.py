import importlib
prep = importlib.import_module('script-0-prep')
analysis = importlib.import_module('script-1-analysis')
precision = importlib.import_module('script-2-precision')
intersection = importlib.import_module('script-3-intersection')
comparison = importlib.import_module('script-4-comparison')

if __name__ == '__main__':
    print('Preparing...')
    prep.prepare()
    print('Analyzing...')
    analysis.analyze()
    print('Graphing Precision...')
    precision.calculate_precision()
    print('Graphing Intersection...')
    intersection.calculate_intersection()
    print('Graphing Comparison...')
    comparison.calculate_comparison()
    print('Done!')