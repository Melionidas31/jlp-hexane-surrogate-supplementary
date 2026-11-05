# Supplementary material R1-1 — ANN surrogates of ALOHA for n-hexane hazard-zone radii

Released in response to reviewer comment R1-1, which asked for the ANN
formulation as complete, ready-to-implement expressions. Parameters, training
data and a consistency check for the manuscript

> **A Machine-Learning Surrogate for Rapid Hazard-Zone Prediction of n-Hexane
> Vapor Dispersion from Tank Overfill: Accuracy and Robustness Limits Beyond
> the Training Domain**
>
> M. Zaki Ramdhan, Adhitya Ryan Ramadhani, Waskito Pranowo
> *Journal of Loss Prevention in the Process Industries*, manuscript
> JLP-D-26-01452 (under review)

Two trained ANN surrogates predict the red, orange and yellow hazard-zone radii
of an n-hexane vapour cloud released by tank overfill, from six scenario
inputs, without running the ALOHA dispersion code. This repository holds their
complete parameters, the ALOHA simulation data they were fitted on, and a
script that checks the two against each other.

Everything here is plain text, so a prediction can be reproduced with a
spreadsheet and no machine-learning software.

## Repository layout

```
parameters/
  README.txt                 full specification: file formats, the six
                             prediction steps, worked test values
  model_1215_seed15/         weights W1..W3, biases b1..b3, scaler, .keras
  model_1261_A/              the same, plus .h5
  model_1215_seed15.xlsx     the same parameters as a spreadsheet, with a
  model_1261_A.xlsx          Calculator sheet that has no macros
data/
  aloha_1215_scenarios.csv   the full-factorial design, 1,215 scenarios
  aloha_1261_scenarios.csv   the extended set, 1,261 scenarios
  aloha_46_added_scenarios.csv   the 46 runs added by the two sets' difference
verify.py                    recomputes each scaler from the data
```

## The two models

| | data | training subset | split | used for |
|---|---|---|---|---|
| `model_1215_seed15` | 1,215 scenarios | 972 | 80/20 drawn at random over the whole design | the SHAP attributions of Section 3.2.1 |
| `model_1261_A` | 1,261 scenarios | 1,008 | 80/20 **stratified by stability class** | the targeted retraining of Section 3.4 |

Both use `random_state = 42`.

**The two splits are not the same.** The standardisation parameters of a model
are the mean and standard deviation of its own training subset, so applying the
wrong split to a model moves the mean of the yellow-zone radius by about 5 m
and nothing afterwards will reproduce. `verify.py` pins each model to its split.

## Architecture

Six inputs, two hidden layers of 64 and 32 ReLU units, three linear outputs,
2,627 parameters. Inputs and outputs are both standardised, so a prediction is
inverse-transformed back to metres before it is read.

A prediction takes six steps:

1. `z = (x - mean) / standard_deviation` from the input rows of `scaler.csv`
2. `h1 = max(0, z W1 + b1)` — 64 values
3. `h2 = max(0, h1 W2 + b2)` — 32 values
4. `s = h2 W3 + b3` — 3 values
5. `radius = s * standard_deviation + mean` from the output rows
6. clip any negative radius to zero

Inputs go in the order used by the rows of `W1`: wind speed (m/s), air
temperature (°C), stability class, inflow rate (kL/h), effective duration
(min), pool thickness (mm). Stability is encoded ordinally, A=1 through F=6.
Outputs are the red, orange and yellow radii in metres.

`parameters/README.txt` carries the full specification, including test values
to check an implementation against. Entering wind 3.0, temperature 27,
stability D, inflow 350, duration 15 and thickness 10 returns

| | red | orange | yellow |
|---|---|---|---|
| `model_1215_seed15` | 61.895 | 79.039 | 138.835 m |
| `model_1261_A` | 63.154 | 81.473 | 139.908 m |

## Data

ALOHA output, semicolon-separated, point as decimal mark, UTF-8. Thirteen
columns, of which the models use nine: six inputs and three target radii. `No`,
`Rate in (m3/s)`, `Volume (m3)` and `Area(m2)` are a row number and three
quantities derived from the others, and they are dropped before training.

| column | unit | 1,215 set | 1,261 set |
|---|---|---|---|
| `Wind (m/s)` | m/s | 1.5, 3.0, 5.0 | 19 values, 1.0 to 10.0 |
| `Temp (°C)` | °C | 25, 27, 30 | 21 values, 17 to 37 |
| `Stability` | Pasquill class | B, D, F | B, D, F |
| `Rate In (kL/jam)` | kL/h | 250, 350, 550 | 250, 350, 550, 1000, 1050 |
| `T_eff (menit)` | min | 2, 5, 15, 30, 45 | 2, 5, 15, 30, 45 |
| `Thickness (mm)` | mm | 24 values, 5.0 to 28.0 | 24 values, 5.0 to 28.0 |
| `Zone Red (m)` | m | 11 to 281 | 11 to 281 |
| `Zone orange (m)` | m | 11 to 371 | 11 to 371 |
| `Zone yellow (m)` | m | 12 to 692 | 12 to 692 |

Column names keep the spelling of the original simulation output, including
the Indonesian `jam` for hour and `menit` for minute, so that they match the
`variable` column of `scaler.csv` and the row labels of the weight files.

`aloha_1261_scenarios.csv` is `aloha_1215_scenarios.csv` followed by the 46
runs of `aloha_46_added_scenarios.csv`, in that order. The order matters,
because it is what the split draws over.

## Checking the release

```bash
pip install pandas scikit-learn
python verify.py
```

The script recomputes the nine means and nine standard deviations of each
model's `scaler.csv` from the data in `data/` and prints the largest
disagreement. Expected output:

```
model_1215_seed15   1215 scenarios, 972 in the training subset, split drawn at random
    largest disagreement over 9 means and 9 standard deviations: 5.7e-14

model_1261_A   1261 scenarios, 1008 in the training subset, split stratified by stability class
    largest disagreement over 9 means and 9 standard deviations: 1.4e-14

Consistent. Both models match the data in this repository to within 1e-09.
```

Nothing is fitted and no network is evaluated, so the check needs only pandas
and scikit-learn and takes about a second.

## What cannot be reproduced

Network weights were initialised at random without a fixed seed, so no run of
the training procedure can be reproduced bit for bit, by the authors as much as
by anyone else. The consequence is bounded, not open: on the test subset the
released 1,215-scenario model attains MAE of 1.85, 2.56 and 4.16 m against the
1.82, 2.69 and 4.51 m reported in Table 4 of the paper, with R² of 99.77, 99.71
and 99.75 % against 99.79, 99.70 and 99.75 %. Recomputing the robustness
results from these parameters should give the same qualitative pattern rather
than the same figures. Appendix A of the paper states this in full.

The MLR baseline carries no such caveat, since ordinary least squares is
deterministic.

## Precision

The released values reproduce the predictions of the accompanying model files
to within 1e-4 m on every scenario of the corresponding dataset. The residual
comes from the order in which floating-point products are accumulated, not from
rounding in these files. Weights are written with nine significant digits,
which round-trips 32-bit floating point exactly.

## License

MIT, see [LICENSE](LICENSE). If you use these files, please cite the paper.
