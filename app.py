from flask import Flask, render_template, request
from typing import Tuple, List, Optional, Union

import processor

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
    measures = processor.get_central_tendency(data_list=data_list, dp=dp)
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
    accuracy = request.form.get("accuracy", "2dp")
    if "dp" in accuracy:
        dp = int(accuracy[0])
    else:
        # TODO: handle sig figs
        dp = 6
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
    measures = processor.get_spread(data_list=data_list, dp=dp)
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
            rows, p_x = processor.get_bcd(
                n=trials, p=probability, x=successes, dp=accuracy
            )
        elif "bpd" in distribution:
            rows, p_x = processor.get_bpd(
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
    accuracy = request.form.get("accuracy", "4dp")
    try:
        accuracy = int(accuracy[0])
    except ValueError:
        accuracy = 4
    distribution = request.form.get("distribution", "")
    if distribution not in ["bpd", "bcd"]:
        distribution = "bpd"
    trials = request.form.get("trials", "")
    probability = request.form.get("probability", "")
    successes = request.form.get("successes", "")
    return accuracy, distribution, probability, successes, trials


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


if __name__ == "__main__":
    app.run(debug=True)
