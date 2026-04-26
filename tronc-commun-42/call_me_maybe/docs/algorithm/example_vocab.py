from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    model = Small_LLM_Model()
    print(model.get_path_to_vocab_file())


if __name__ == "__main__":
    main()
