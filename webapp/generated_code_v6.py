import pandas as pd
import json
from typing import Dict, Any
import numpy as np


def categorize_fields(df):
    categories = {
        'demographic': [],
        'behavioral': [],
        'purchase': [],
        'response': []
    }

    for column in df.columns:
        col_lower = column.lower()
        if any(term in col_lower for term in ['age', 'gender', 'region']):
            categories['demographic'].append(column)
        elif any(term in col_lower for term in ['frequency', 'membership', 'preferred']):
            categories['behavioral'].append(column)
        elif any(term in col_lower for term in ['purchase', 'promo', 'value']):
            categories['purchase'].append(column)
        elif any(term in col_lower for term in ['review', 'score', 'rating']):
            categories['response'].append(column)

    return categories


def analyze_demographics(df, demographic_fields):
    results = {}
    for field in demographic_fields:
        results[field] = df[field].value_counts().to_dict()
    return results


def analyze_behavioral(df, behavioral_fields):
    results = {}
    for field in behavioral_fields:
        results[field] = df[field].value_counts().to_dict()
    return results


def analyze_purchases(df, purchase_fields):
    results = {}
    numeric_fields = df[purchase_fields].select_dtypes(include=[np.number]).columns

    for field in numeric_fields:
        results[field] = {
            'mean': float(df[field].mean()),
            'median': float(df[field].median()),
            'std': float(df[field].std())
        }

    categorical_fields = list(set(purchase_fields) - set(numeric_fields))
    for field in categorical_fields:
        results[field] = df[field].value_counts().to_dict()

    return results


def analyze_response(df, response_fields):
    results = {}
    for field in response_fields:
        if df[field].dtype in [np.float64, np.int64]:
            results[field] = {
                'mean': float(df[field].mean()),
                'median': float(df[field].median())
            }
        else:
            results[field] = df[field].value_counts().to_dict()
    return results


def main(csv_file: str) -> Dict[str, Any]:
    try:
        df = pd.read_csv(csv_file)
        categories = categorize_fields(df)

        results = {
            'error': False,
            'results': {
                'demographic_analysis': analyze_demographics(df, categories['demographic']),
                'behavioral_analysis': analyze_behavioral(df, categories['behavioral']),
                'purchase_analysis': analyze_purchases(df, categories['purchase']),
                'response_analysis': analyze_response(df, categories['response'])
            }
        }

        return results

    except Exception as e:
        return {
            'error': True,
            'message': f'Analysis failed: {str(e)}'
        }


results = main('shopping_behavior_test.csv')
print(json.dumps(results, indent=2))