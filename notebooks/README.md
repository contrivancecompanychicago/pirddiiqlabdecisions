# Diabetes Foot Risk Prediction Model in Google Colab

Start with [`diabetes_foot_risk_colab.ipynb`](diabetes_foot_risk_colab.ipynb). It is a Python-only Colab walkthrough: clone this repository and the upstream model repo, install the package and the pure-Python `rdata` reader, load the upstream RDS model directly, and predict risk. **No R installation or R code is needed.**

The same Python interface is available locally after installing the project: `from footcare_risk_model.rds_model import load_rds_model`. The notebook includes CSV upload/scoring and a command-line example.

The published model is a research/educational tool, not a diagnosis or substitute for clinical judgment. Never upload identifiable or confidential patient data to hosted Colab; follow your organization's approved data-handling policies.
