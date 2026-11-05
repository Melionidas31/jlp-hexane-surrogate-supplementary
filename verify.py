# -*- coding: utf-8 -*-
"""Check that the released parameters and the released data belong together.

The standardisation parameters in each model's scaler.csv are the mean and the
population standard deviation of that model's own training subset. They are
therefore recomputable from the data in this repository, and this script
recomputes them and reports the largest disagreement.

It is a consistency check on the released files, not a retraining. Nothing is
fitted and no network is evaluated, so the script needs only pandas and
scikit-learn and finishes in about a second.

The two models were split differently, and the split is what decides which
rows enter the training subset:

    model_1215_seed15   80/20 drawn at random over the whole design
    model_1261_A        80/20 stratified by stability class

Both use random_state = 42. Using the wrong split for a model moves the mean
of the yellow-zone radius by about 5 m, so the check below also confirms which
split belongs to which model.

Usage:
    python verify.py
"""
import os
import sys

import pandas as pd
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))

# The raw simulation output carries four columns that the models do not use:
# a row number and three quantities derived from the others.
COLUMNS = ['No', 'Wind (m/s)', 'Temp (°C)', 'Stability',
           'Rate In (kL/jam)', 'Rate in (m3/s)', 'T_eff (menit)',
           'Thickness (mm)', 'Volume (m3)', 'Area(m2)', 'Zone Red (m)',
           'Zone orange (m)', 'Zone yellow (m)']
# order as used by the rows of W1
INPUTS = ['Wind (m/s)', 'Temp (°C)', 'Stability', 'Rate In (kL/jam)',
          'T_eff (menit)', 'Thickness (mm)']
OUTPUTS = ['Zone Red (m)', 'Zone orange (m)', 'Zone yellow (m)']
STABILITY = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}

CASES = [
    ('model_1215_seed15', 'data/aloha_1215_scenarios.csv', 1215, False),
    ('model_1261_A', 'data/aloha_1261_scenarios.csv', 1261, True),
]
TOLERANCE = 1e-9


def training_subset(csv, stratified):
    df = pd.read_csv(os.path.join(HERE, csv), sep=';', encoding='utf-8')
    df.columns = COLUMNS
    X = df[INPUTS].copy()
    # stratification uses the letter class, before the ordinal encoding
    classes = X['Stability'].copy()
    X['Stability'] = X['Stability'].map(STABILITY)
    y = df[OUTPUTS]
    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=classes if stratified else None)
    return len(df), X_train, y_train


failed = []
for model, csv, expected_rows, stratified in CASES:
    rows, X_train, y_train = training_subset(csv, stratified)
    if rows != expected_rows:
        failed.append('%s: data has %d rows, expected %d'
                      % (model, rows, expected_rows))

    recomputed = {c: (X_train[c].mean(), X_train[c].std(ddof=0))
                  for c in INPUTS}
    recomputed.update({c: (y_train[c].mean(), y_train[c].std(ddof=0))
                       for c in OUTPUTS})

    released = pd.read_csv(
        os.path.join(HERE, 'parameters', model, 'scaler.csv'))

    print('%s   %d scenarios, %d in the training subset, split %s'
          % (model, rows, len(X_train),
             'stratified by stability class' if stratified
             else 'drawn at random'))
    worst = 0.0
    for _, row in released.iterrows():
        name = row['variable']
        name = 'Temp (°C)' if name.startswith('Temp') else name
        got_mean, got_sd = recomputed[name]
        d = max(abs(float(row['mean']) - got_mean),
                abs(float(row['standard_deviation']) - got_sd))
        worst = max(worst, d)
        if d >= TOLERANCE:
            failed.append('%s / %s: differs by %.3g' % (model, name, d))
    print('    largest disagreement over 9 means and 9 standard '
          'deviations: %.2g\n' % worst)

if failed:
    print('MISMATCH')
    for f in failed:
        print('  - %s' % f)
    sys.exit(1)
print('Consistent. Both models match the data in this repository to within '
      '%g.' % TOLERANCE)
