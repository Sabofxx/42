import json
from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    ruta = "/home/sergio-alejandro/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/vocab.json"

    with open(ruta, "r") as vocab:
        dato = json.load(vocab)
        total = len(dato)

    print(total)
    print(dato["{"])
    print(dato["fn"])
    print(dato["_add"])
    print(dato["_numbers"])

    model = Small_LLM_Model()

    print(model.encode("fn_add_numbers"))


if __name__ == "__main__":
    main()
