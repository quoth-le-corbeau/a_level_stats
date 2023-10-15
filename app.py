from flask import Flask, render_template, request
from typing import Tuple, List, Optional, Union
from result import Result, Ok, Err
import data_processor
import models

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", title="Home")


@app.route("/mean")
def mean():
    return render_template("mean.html", title="Central Tendency")


@app.route("/mean-form", methods=["POST"])
def mean_form():
    data_list, dp, error = _discreet_data_from_form()
    if error is not None:
        return render_template("mean-error.html", data=error[0], error=error[1])
    measures = data_processor.get_central_tendency(data_list=data_list, dp=dp)
    return render_template(
        "mean-form.html",
        measures=measures,
        data=data_list,
        sorted_data=sorted(data_list),
        dp=dp,
    )


def _discreet_data_from_form() -> Tuple[List[float], int, Optional[Tuple[str, str]]]:
    error = None
    data_list = []
    dp = _get_or_set_dp()
    data = request.form.get("data", "")
    if data == "":
        error = (data, "Make sure to enter data separated by commas e.g 1.1, 2.2, 3")
    try:
        data_list = list(map(lambda x: float(x), data.split(",")))
    except ValueError:
        error = (
            data,
            "Please only enter numbers using '.' for decimal point. "
            "It could be an unwanted character or maybe you used ',' "
            "as a decimal marker?",
        )
    return data_list, dp, error


@app.route("/spread")
def spread():
    return render_template("spread.html", title="Spread")


@app.route("/spread-form", methods=["POST"])
def spread_form():
    data_list, dp, error = _discreet_data_from_form()
    if error is not None:
        return render_template("spread-error.html", data=error[0], error=error[1])
    measures = data_processor.get_spread(data_list=data_list, dp=dp)
    return render_template(
        "spread-form.html",
        measures=measures,
        data=data_list,
        dp=dp,
    )


@app.route("/binomial")
def binomial():
    return render_template("binomial.html", title="Binomial")


@app.route("/binomial-form", methods=["POST"])
def binomial_form():
    (
        accuracy,
        distribution,
        probability,
        successes,
        trials,
        error,
    ) = _validate_binomial_form_data()
    if error is not None:
        return render_template("binomial-error.html", error=error)
    try:
        if "bcd" in distribution:
            rows, p_x = data_processor.get_bcd(
                n=trials, p=probability, x=successes, dp=accuracy
            )
        elif "bpd" in distribution:
            rows, p_x = data_processor.get_bpd(
                n=trials, p=probability, x=successes, dp=accuracy
            )
        else:
            return render_template("binomial-error.html", error="Unexpected Error!!")
        return render_template(
            "binomial-form.html",
            accuracy=accuracy,
            distribution=distribution,
            trials=str(trials),
            probability=str(probability),
            successes=str(successes),
            rows=rows,
            p_x_is_x=p_x,
            dp=accuracy,
        )
    except ValueError:
        error = (
            f"Invalid values for n, p or x. "
            f"You entered n = {trials}, p = {probability}, x = {successes}"
        )
        return render_template("binomial-error.html", error=error)


def _get_binomial_form_submission() -> Tuple[int, str, str, str, str]:
    dp = _get_or_set_dp()
    distribution = request.form.get("distribution", "")
    if distribution not in ["bpd", "bcd"]:
        distribution = "bpd"
    trials = request.form.get("trials", "")
    probability = request.form.get("probability", "")
    successes = request.form.get("successes", "")
    return dp, distribution, probability, successes, trials


def _get_or_set_dp() -> int:
    accuracy = request.form.get("accuracy", "4dp")
    try:
        dp = int(accuracy[0])
    except ValueError:
        dp = 4
    return dp


def _validate_binomial_form_data() -> (
    Union[
        Tuple[int, str, float, int, int, Optional[str]],
        Tuple[None, None, None, None, None, str],
    ]
):
    (
        accuracy,
        distribution,
        probability,
        successes,
        trials,
    ) = _get_binomial_form_submission()
    error = None
    if any(x == "" for x in [trials, probability, successes]):
        if trials == "":
            trials = "(empty)"
        if probability == "":
            probability = "(empty)"
        if successes == "":
            successes = "(empty)"
        error = (
            f"Invalid values for n, p or x. "
            f"You entered n = {trials}, p = {probability}, x = {successes}"
        )
        return None, None, None, None, None, error
    try:
        if float(probability) < 0 or float(probability) > 1:
            error = (
                f"You entered p = {float(probability)}!! "
                f"Probability must be between 0 and 1 :-)"
            )
        return (
            accuracy,
            distribution,
            float(probability),
            int(successes),
            int(trials),
            error,
        )
    except ValueError:
        error = (
            f"Invalid values for n, p or x. "
            f"You entered n = {trials}, p = {probability}, x = {successes}"
        )
        return None, None, None, None, None, error


@app.route("/normal")
def normal():
    return render_template("normal.html", title="Normal")


@app.route("/normal-form", methods=["POST"])
def normal_form():
    dp = _get_or_set_dp()
    param_result = _get_normal_parameters()
    if isinstance(param_result, Err):
        return render_template("normal-error.html", error=param_result.err_value)
    else:
        assert isinstance(param_result, Ok)
        normal_params = param_result.ok_value
        func = data_processor.NORMAL_FUNCTIONS[normal_params.operation]
        normal_result = func(normal_params)
        if isinstance(normal_result, Err):
            return render_template(
                "unexpected-error.html", error=normal_result.err_value
            )
        else:
            assert isinstance(normal_result, Ok)
            return render_template(
                "normal-form.html",
                title="Normal",
                dp=dp,
                mu=normal_params.mu,
                sigma=normal_params.sigma,
                x1=normal_params.x1,
                x2=normal_params.x2,
                p=normal_params.p,
                operation=normal_params.operation,
                answer=round(normal_result.ok_value, dp),
            )


def _get_normal_parameters() -> Result[models.NormalParams, models.NormalError]:
    operation = request.form.get("operation", "")
    if operation == "":
        # this should not be possible
        return Err(
            models.NormalError(
                operation=operation,
                mean=None,
                standard_deviation=None,
                x1=None,
                x2=None,
                p=None,
                message="No operation selected!",
            )
        )
    mean = request.form.get("mean", "")
    if mean == "":
        return Err(
            models.NormalError(
                operation=operation,
                mean="empty",
                standard_deviation=None,
                x1=None,
                x2=None,
                p=None,
                message="Please provide a numeric value for the mean, μ.",
            )
        )
    standard_deviation = request.form.get("sd", "")
    if standard_deviation == "":
        return Err(
            models.NormalError(
                operation=None,
                mean=None,
                standard_deviation="empty",
                x1=None,
                x2=None,
                p=None,
                message="Please provide a numeric value "
                "for the standard deviation, σ.",
            )
        )
    try:
        mu = float(mean)
        sd = float(standard_deviation)
    except ValueError:
        return Err(
            models.NormalError(
                operation=operation,
                mean=mean,
                standard_deviation=standard_deviation,
                x1=None,
                x2=None,
                p=None,
                message="Please provide numeric values only for the mean, μ "
                "and standard deviation, σ.",
            )
        )
    x_upper = request.form.get("x_upper", "")
    x_lower = request.form.get("x_lower", "")
    prob = request.form.get("prob", "")
    if operation not in ["ppf_left", "ppf_right"] and x_upper == "":
        return Err(
            models.NormalError(
                operation=operation,
                mean=mean,
                standard_deviation=standard_deviation,
                x1="empty",
                x2=None,
                p=None,
                message="Please provide a numeric value for x1.",
            )
        )
    if operation == "cdf_middle" and (x_upper == "" or x_lower) == "":
        return Err(
            models.NormalError(
                operation=operation,
                mean=mean,
                standard_deviation=standard_deviation,
                x1=x_upper,
                x2=x_lower,
                p=None,
                message="Please provide numeric values for x1 and x2.",
            )
        )
    if operation in ["ppf_left", "ppf_right"] and prob == "":
        return Err(
            models.NormalError(
                operation=operation,
                mean=mean,
                standard_deviation=standard_deviation,
                x1=None,
                x2=None,
                p="empty",
                message="Please provide a value for p. 0 <= p <= 1",
            )
        )
    if x_upper != "":
        try:
            x1 = float(x_upper)
        except ValueError:
            return Err(
                models.NormalError(
                    operation=operation,
                    mean=mean,
                    standard_deviation=standard_deviation,
                    x1=x_upper,
                    x2=None,
                    p=None,
                    message="Please enter a numeric value for x1 "
                    "with no other characters.",
                )
            )
    else:
        x1 = None
    if x_lower != "":
        try:
            x2 = float(x_lower)
        except ValueError:
            return Err(
                models.NormalError(
                    operation=None,
                    mean=mean,
                    standard_deviation=standard_deviation,
                    x1=None,
                    x2=None,
                    p=None,
                    message="Please enter a numeric value for x2 "
                    "with no other characters.",
                )
            )
    else:
        x2 = None
    if x1 is not None and x2 is not None and not x2 < x1:
        return Err(
            models.NormalError(
                operation=None,
                mean=mean,
                standard_deviation=standard_deviation,
                x1=x_upper,
                x2=x_lower,
                p=None,
                message="Please make sure x2 < x1.",
            )
        )
    if prob != "":
        try:
            p = float(prob)
        except ValueError:
            return Err(
                models.NormalError(
                    operation=None,
                    mean=mean,
                    standard_deviation=standard_deviation,
                    x1=None,
                    x2=None,
                    p=p,
                    message="Please enter a numeric value for p "
                    "with no other characters.",
                )
            )
        if p < 0 or p > 1:
            return Err(
                models.NormalError(
                    operation=None,
                    mean=mean,
                    standard_deviation=standard_deviation,
                    x1=None,
                    x2=None,
                    p=p,
                    message="Probabilities must be: 0 <= p <= 1!",
                )
            )
    else:
        p = None
    return Ok(
        models.NormalParams(
            operation=operation,
            mu=mu,
            sigma=sd,
            x1=x1,
            x2=x2,
            p=p,
        )
    )


if __name__ == "__main__":
    app.run(debug=True)
