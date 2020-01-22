def trunc(number, digits=0.0) -> float:
    stepper = 10 ** digits
    return int(stepper * number) / stepper