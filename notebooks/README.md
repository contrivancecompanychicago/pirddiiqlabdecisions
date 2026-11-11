# Diabetes Foot Risk Prediction Model in Google Colab

The step-by-step notebook is [`diabetes_foot_risk_colab.ipynb`](diabetes_foot_risk_colab.ipynb). Open it directly in [Google Colab](https://colab.research.google.com/github/contrivancecompanychicago/pirddiiqlabdecisions/blob/main/notebooks/diabetes_foot_risk_colab.ipynb), or open the notebook in this repository and choose **Open in Colab**.

The walkthrough clones this repository and the upstream model repository, installs R only for the one-time conversion of the official `.rds` model to JSON, then installs and uses the Python package to predict risk. CSV scoring is optional. No R knowledge is needed to follow the notebook cells.

The JSON model artifact is generated within the temporary Colab runtime and is not included in Git. For local Python prediction, follow [`../footcare_risk_model/README.md`](../footcare_risk_model/README.md) to create the artifact and install the package.

**Clinical/privacy caution:** This research/educational model is not a medical device and does not provide a diagnosis. Never upload identifiable or confidential patient information to hosted Colab; use only approved, de-identified data in accordance with your organization's policies.
