"""Answer generation using Qwen/Qwen3-0.6B via transformers."""

from __future__ import annotations

from typing import List, Optional

from .chunking import Chunk

DEFAULT_MODEL = "Qwen/Qwen3-0.6B"

SYSTEM_PROMPT = (
    "You are a precise technical assistant. Answer the user's question using "
    "ONLY the provided context snippets. Be concise, source-grounded, and "
    "self-contained. If the answer is not present in the context, say so."
)


class AnswerGenerator:
    """Lightweight wrapper around Qwen3-0.6B for grounded answer generation."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        max_new_tokens: int = 256,
        max_context_length: int = 2000,
    ) -> None:
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.max_context_length = max_context_length
        self._tokenizer = None
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        if not torch.cuda.is_available():
            assert self._model is not None
            self._model.to("cpu")

    def _format_context(self, chunks: List[Chunk]) -> str:
        parts: List[str] = []
        for i, c in enumerate(chunks, 1):
            text = c.text
            if len(text) > self.max_context_length:
                text = text[: self.max_context_length]
            parts.append(
                f"[Source {i}] {c.file_path}"
                f" ({c.first_character_index}-{c.last_character_index}):\n{text}"
            )
        return "\n\n".join(parts)

    def generate(self, question: str, chunks: List[Chunk]) -> str:
        """Generate an answer grounded in ``chunks``."""
        self._load()
        assert self._tokenizer is not None and self._model is not None

        context = self._format_context(chunks) if chunks else "(no context)"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"Question: {question}\n\n"
                    "Answer the question using only the context above."
                ),
            },
        ]
        prompt = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        import torch

        with torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                temperature=0.0,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        generated = output[0][inputs["input_ids"].shape[-1]:]
        text = self._tokenizer.decode(generated, skip_special_tokens=True).strip()
        return text


_singleton: Optional[AnswerGenerator] = None


def get_generator(
    model_name: str = DEFAULT_MODEL,
    max_context_length: int = 2000,
) -> AnswerGenerator:
    """Return a process-wide singleton generator (avoids reloading the model)."""
    global _singleton
    if _singleton is None or _singleton.model_name != model_name:
        _singleton = AnswerGenerator(
            model_name=model_name,
            max_context_length=max_context_length,
        )
    return _singleton
