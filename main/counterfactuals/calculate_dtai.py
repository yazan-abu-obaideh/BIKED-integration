import tensorflow as tf


def calculateDTAI(actual_performance,
                  direction,
                  targets,
                  alpha_values,
                  beta_values,
                  smallest_allowed=1e-7) -> float:
    # TODO: make this return an array in case of multiple inputs
    alpha_values, beta_values, actual_performance = convert_to_float_arrays(alpha_values,
                                                                            beta_values,
                                                                            actual_performance)
    actual = ensure_greater_than_smallest(actual_performance, smallest_allowed)

    scores = calculate_scores(alpha_values, beta_values, calculate_ratios(direction, targets, actual))

    sum_of_scores = tf.math.reduce_sum(scores)
    sum_s_max = tf.math.reduce_sum(alpha_values / beta_values)
    sum_s_min = -tf.math.reduce_sum(alpha_values)

    sum_of_scores = (sum_of_scores - sum_s_min) / (sum_s_max - sum_s_min)
    return sum_of_scores.numpy()


def calculate_scores(alpha_values, beta_values, ratios):
    case_less_or_equal_to_one = tf.multiply(alpha_values, ratios) - alpha_values
    alpha_over_beta = tf.divide(alpha_values, beta_values)
    exponential = tf.exp(tf.multiply(beta_values, (1 - ratios)))
    case_greater_or_equal_to_one = tf.multiply(alpha_over_beta, (1 - exponential))
    greater_than_one = tf.greater(ratios, 1)
    greater_than_one = tf.cast(greater_than_one, "float32")
    scores = tf.multiply(case_greater_or_equal_to_one, greater_than_one) \
             + tf.multiply(case_less_or_equal_to_one, (1 - greater_than_one))
    return scores


def ensure_greater_than_smallest(actual_performance, tolerance):
    return tf.math.maximum(actual_performance, tolerance)


def calculate_ratios(direction, targets, y):
    if direction == "maximize":
        x = tf.divide(y, targets)
    elif direction == "minimize":
        x = tf.divide(targets, y)
    else:
        raise Exception("Unknown optimization direction, expected maximize or minimize")
    return x


def convert_to_float_arrays(alpha_values, beta_values, y_eval):
    alpha_values = tf.cast(alpha_values, "float32")
    beta_values = tf.cast(beta_values, "float32")
    y_eval = tf.cast(y_eval, "float32")
    return alpha_values, beta_values, y_eval


if __name__ == "__main__":
    design_index = calculateDTAI([10, 5], "maximize", [10, 5], [1, 1], [4, 4])
    print(design_index)
