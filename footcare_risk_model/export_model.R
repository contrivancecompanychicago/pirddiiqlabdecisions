# Run from the upstream PIRDDIIQ-FootCare-risk-model repository root with R
# packages riskRegression, rms, and jsonlite installed.
# Usage: Rscript /path/to/this/file [output.json]

suppressPackageStartupMessages({
  library(riskRegression)
  library(rms)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
outfile <- if (length(args) >= 1) args[[1]] else "footcare_risk_model.json"
model_path <- "model/final_FGR_clean.rds"
if (!file.exists(model_path)) stop("Run this script from the upstream model repository root.")
model <- readRDS(model_path)
coef <- model$crrFit$coef
if (is.null(names(coef)) || anyDuplicated(names(coef))) {
  stop("The fitted model coefficients must have unique names.")
}

make_row <- function() {
  data <- data.frame(
    age = 67, sex_f = 1, elective_adm = 0, homelessness = 0,
    peripheral_AD = 0, coronary_AD = 0, stroke = 0, CHF = 0,
    hypertension = 0, COPD = 0, CKD = 0, malignancy = 0,
    mental_illness = 0, creatinine = 0, Hb_A1C = 0, albumin = 0,
    Hb_A1C_missing = 1, creatinine_missing = 1, albumin_missing = 1
  )
  age <- rms::rcs(data$age, model$splines$age_knots)
  creatinine <- rms::rcs(data$creatinine, model$splines$creatinine_knots)
  hba1c <- rms::rcs(data$Hb_A1C, model$splines$hba1c_knots)
  albumin <- rms::rcs(data$albumin, model$splines$albumin_knots)
  data$age1 <- age[, 2]; data$age2 <- age[, 3]
  data$creatinine1 <- creatinine[, 2]; data$creatinine2 <- creatinine[, 3]
  data$Hb_A1C1 <- hba1c[, 2]; data$Hb_A1C2 <- hba1c[, 3]
  data$albumin1 <- albumin[, 2]
  data
}

reference <- make_row()
formula <- ~ age + sex_f + elective_adm + homelessness + peripheral_AD +
  coronary_AD + stroke + CHF + hypertension + COPD + CKD + malignancy +
  mental_illness + creatinine + Hb_A1C + albumin + Hb_A1C_missing +
  creatinine_missing + albumin_missing + age1 + age2 + creatinine1 +
  creatinine2 + albumin1 + Hb_A1C1 + Hb_A1C2
x <- model.matrix(formula, data = reference)[, -1, drop = FALSE]
if (!identical(colnames(x), names(coef))) {
  stop(paste0("Model matrix/coefficient names do not match. Matrix: ",
              paste(colnames(x), collapse = ", "), "; coefficients: ",
              paste(names(coef), collapse = ", ")))
}
reference_lp <- as.numeric(x %*% coef)
# Daily horizon through five years; riskRegression supplies the fitted CIF.
times <- seq(0, 5 * 365.25, by = 1)
risk <- as.numeric(riskRegression::predictRisk(model, newdata = reference,
                                                times = times, cause = 1))
if (length(risk) != length(times) || any(!is.finite(risk)) ||
    any(risk < 0) || any(risk >= 1) || any(diff(risk) < -1e-10)) {
  stop("Could not obtain a valid, monotone reference cumulative-incidence curve.")
}
baseline <- -log1p(-risk) / exp(reference_lp)
artifact <- list(
  format_version = 1,
  source = "PIRDDIIQ-FootCare-risk-model",
  feature_names = names(coef),
  coefficients = unname(as.numeric(coef)),
  knots = list(
    age = as.numeric(model$splines$age_knots),
    creatinine = as.numeric(model$splines$creatinine_knots),
    hba1c = as.numeric(model$splines$hba1c_knots),
    albumin = as.numeric(model$splines$albumin_knots)
  ),
  baseline_times_days = as.numeric(times),
  baseline_cumulative_subhazard = as.numeric(baseline),
  reference_linear_predictor = reference_lp
)
jsonlite::write_json(artifact, outfile, auto_unbox = TRUE, digits = 17,
                     pretty = TRUE, na = "null")
message("Wrote Python model artifact to ", outfile)
