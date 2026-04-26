import random


# Simulación de probabilidades de un modelo
def fake_model_next_token():
    tokens = [
        "{", "}", ":", ",", '"name"', '"age"', '"Alice"', '"Bob"', "25", "30"]
    return random.choice(tokens)


class JSONStateMachine:
    def __init__(self):
        self.state = "start"

    def allowed_tokens(self):
        if self.state == "start":
            return ["{"]
        if self.state == "open_brace":
            return ['"name"']
        if self.state == "name_key":
            return [":"]
        if self.state == "name_colon":
            return ['"Alice"', '"Bob"']
        if self.state == "name_value":
            return [","]
        if self.state == "comma":
            return ['"age"']
        if self.state == "age_key":
            return [":"]
        if self.state == "age_colon":
            return ["25", "30"]
        if self.state == "age_value":
            return ["}"]
        return []

    def update_state(self, token):
        transitions = {
            "start": "open_brace",
            "open_brace": "name_key",
            "name_key": "name_colon",
            "name_colon": "name_value",
            "name_value": "comma",
            "comma": "age_key",
            "age_key": "age_colon",
            "age_colon": "age_value",
            "age_value": "done",
        }
        self.state = transitions.get(self.state, "done")


def constrained_generate():
    sm = JSONStateMachine()
    output = []

    while sm.state != "done":
        allowed = sm.allowed_tokens()

        # simulamos múltiples intentos hasta que salga uno válido
        while True:
            token = fake_model_next_token()
            if token in allowed:
                break

        output.append(token)
        sm.update_state(token)

    return " ".join(output)


print(constrained_generate())
