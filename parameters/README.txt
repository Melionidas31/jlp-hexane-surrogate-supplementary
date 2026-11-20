Supplementary material for

  M. Z. Ramdhan, A. R. Ramadhani and W. Pranowo, "A machine-learning surrogate
  for rapid hazard-zone prediction of n-hexane vapor dispersion from tank
  overfill: Accuracy and robustness limits beyond the training domain",
  Journal of Loss Prevention in the Process Industries, vol. 105, p. 106245,
  Jan. 2027. doi: 10.1016/j.jlp.2026.106245

Released in response to reviewer comment 1, which asked for the surrogate's
parameters so that the ANN formulation is reproducible with complete,
ready-to-implement mathematical expressions.

IF YOU USE THIS DATA OR THESE PARAMETERS IN WORK YOU PUBLISH, PLEASE CITE THE
PAPER ABOVE. The files are free to use under the MIT licence, and a citation
is the only thing asked in return. The repository at
https://github.com/Melionidas31/jlp-hexane-surrogate-supplementary carries the
reference as BibTeX and as CITATION.cff.


CONTENTS

  model_1215_seed15/        ANN for the 1,215-scenario setting
  model_1261_A/             ANN for the 1,261-scenario setting
  model_1215_seed15.xlsx    the same parameters as a spreadsheet, with a
  model_1261_A.xlsx         working calculator sheet

Each model folder contains

  W1.csv   weights, 6 inputs x 64 units of hidden layer 1
  b1.csv   bias of hidden layer 1, 64 values
  W2.csv   weights, 64 x 32 units of hidden layer 2
  b2.csv   bias of hidden layer 2, 32 values
  W3.csv   weights, 32 units x 3 outputs
  b3.csv   bias of the output layer, 3 values
  scaler.csv            standardisation parameters for 6 inputs and 3 outputs
  ann_*.keras / *.h5    the model file itself, for direct use

Every CSV carries row and column labels, uses the comma as field separator
and the point as decimal mark. The weights are written with nine significant
digits, which round-trips 32-bit floating point exactly.


HOW TO COMPUTE A PREDICTION

  1. Standardise each input:  z = (x - mean) / standard_deviation
     taking mean and standard_deviation from the input rows of scaler.csv.
  2. Hidden layer 1:  h1 = max(0, z W1 + b1)      64 values
  3. Hidden layer 2:  h2 = max(0, h1 W2 + b2)     32 values
  4. Output layer:    s  = h2 W3 + b3             3 values
  5. Rescale:  radius = s * standard_deviation + mean
     taking the values from the output rows of scaler.csv.
  6. Clip any negative radius to zero.

Inputs are given in the order used by W1: wind speed (m/s), air temperature
(C), stability class, inflow rate (kL/h), effective duration (min) and pool
thickness (mm). Stability class is encoded ordinally, A=1 through F=6. The
three outputs are the red, orange and yellow hazard-zone radii in metres.

The Calculator sheet of each workbook implements steps 1 to 6 with ordinary
spreadsheet formulas, with no macros, so a prediction can be reproduced
without any machine-learning software. Entering wind 3.0, temperature 27,
stability 4 (class D), inflow 350, duration 15 and thickness 10 returns

  model_1215_seed15     61.895 / 79.039 / 138.835 m
  model_1261_A          63.154 / 81.473 / 139.908 m

These values are also stored on the sheet, so the calculator can be checked
against them.


WHICH MODEL CORRESPONDS TO WHICH RESULT

  model_1215_seed15   the 1,215-scenario setting. Trained on an 80/20 split
                      drawn at random over the whole design, random_state = 42.
                      This model produced the SHAP attributions of Section
                      3.2.1.
  model_1261_A        the 1,261-scenario setting obtained after the targeted
                      retraining of Section 3.4. Trained on an 80/20 split
                      stratified by stability class, random_state = 42.

The two splits differ, so the standardisation parameters of a given model are
reproduced only by the split named above for that model.

Network weights were initialised randomly without a fixed seed, so no run of
the training procedure can be reproduced bit for bit, including by the
authors. Appendix A of the paper bounds the consequence, comparing the
test-set metrics of the released models against those of Table 4. The released
models are runs of the identical procedure on the identical data.


PRECISION

The released values reproduce the predictions of the accompanying model files
to within 1e-4 m across every scenario in the corresponding dataset. The
residual arises from the order of floating-point accumulation, not from
rounding in these files.
