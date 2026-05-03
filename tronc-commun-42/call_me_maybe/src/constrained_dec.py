#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import TYPE_CHECKING, TypedDict

from src.models import FunctionDefinition

if TYPE_CHECKING:  # pragma: no cover - import utilisé uniquement pour le typage
    from llm_sdk import Small_LLM_Model


class TrieNode(TypedDict):
    """
    Représente un noeud unique du FunctionTrie.

    Attributs :
        children : Dictionnaire associant les IDs de tokens
                    à leurs noeuds enfants correspondants.
        is_end : Booléen indiquant si ce noeud marque la fin
                    d'un nom de fonction valide.
        fn_name : Le nom complet de la fonction si is_end vaut True,
                    sinon None.
    """
    children: dict[int, "TrieNode"]
    is_end: bool
    fn_name: str | None


class VocabularyMapper:
    """
    Gère la correspondance entre les tokens et leurs représentations textuelles.

    Fournit des méthodes utilitaires pour convertir des IDs en texte et
    rechercher les tokens partageant un préfixe spécifique, afin d'aider
    à la génération contrainte.
    """
    def __init__(self, model: Small_LLM_Model) -> None:
        """
        Initialise le mapper à partir du fichier de vocabulaire du modèle.

        Arguments :
            model : Une instance de Small_LLM_Model pour récupérer
                    le chemin du vocabulaire.
        """
        self.model = model
        route = model.get_path_to_vocab_file()
        with open(route, "r", encoding="utf-8") as f:
            raw_data: dict[str, int] = json.load(f)
        # token_string -> token_id
        self.vocab: dict[str, int] = raw_data
        # token_id -> token_string
        self.vocab_inverted: dict[int, str] = {
            value: key for key, value in raw_data.items()}
        # Cache pré-calculé : tokens dont la chaîne décodée commence par un
        # chiffre, '.' ou '-'. Utilisé par la contrainte de nombre pour
        # éviter de scanner tout le vocab à chaque appel.
        self._number_start_tokens: list[int] | None = None

    def token_to_str(self, token_id: int) -> str:
        """Convertit un ID de token vers sa représentation textuelle."""
        return self.vocab_inverted[token_id]

    def str_to_token(self, text: str) -> int:
        """Convertit un token (chaîne) vers son ID entier correspondant."""
        return self.vocab[text]

    def find_tokens_with_prefix(self, prefix: str) -> list[int]:
        """Retourne tous les IDs de tokens dont la représentation textuelle
        commence par `prefix`."""
        return [
            token_id for token_id, text in self.vocab_inverted.items()
            if text.startswith(prefix)
        ]

    def number_start_tokens(self) -> list[int]:
        """Retourne le cache des tokens pouvant débuter un nombre JSON."""
        if self._number_start_tokens is None:
            tokens: set[int] = set()
            for digit in range(10):
                tokens.update(self.find_tokens_with_prefix(str(digit)))
            tokens.update(self.find_tokens_with_prefix("-"))
            self._number_start_tokens = list(tokens)
        return self._number_start_tokens


class FunctionTrie:
    """
    Arbre de préfixes (Trie) utilisé pour contraindre la génération du nom
    de fonction.

    Garantit que le LLM ne génère que des noms de fonctions présents dans
    les définitions fournies.
    """
    def __init__(self) -> None:
        """Initialise une racine de Trie vide."""
        self.root: TrieNode = {
            "children": {}, "is_end": False, "fn_name": None}

    def insert(self, tokens: list[int], fn_name: str) -> None:
        """
        Insère une séquence de tokens représentant un nom de fonction
        dans le Trie.
        """
        current_node = self.root

        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                new_node: TrieNode = {
                    "children": {}, "is_end": False, "fn_name": None}
                current_node["children"][token] = new_node
                current_node = new_node

        current_node["is_end"] = True
        current_node["fn_name"] = fn_name

    def get_valid_tokens(self, token_generated: list[int]) -> list[int]:
        """
        Retourne la liste des tokens suivants valides selon le chemin
        de génération courant.
        """
        current_node = self.root

        for token in token_generated:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return []
        return list(current_node["children"].keys())

    def is_function_complete(self, tokens: list[int]) -> bool:
        """
        Vérifie si la séquence de tokens forme un nom de fonction
        complet et valide.

        Retourne True uniquement quand le chemin se termine sur une feuille,
        afin que les noms de fonctions partageant un préfixe avec des noms
        plus longs ne soient pas tronqués prématurément.
        """
        current_node = self.root
        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return False
        return current_node["is_end"] and not current_node["children"]

    def get_fn_name(self, tokens: list[int]) -> str | None:
        """
        Récupère le nom complet de la fonction associée à une séquence
        de tokens.
        """
        current_node = self.root

        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return None
        return current_node["fn_name"]


def build_trie(
    functions: list[FunctionDefinition], model: Small_LLM_Model
) -> FunctionTrie:
    """
    Construit un FunctionTrie à partir d'une liste de définitions de
    fonctions valides.

    Arguments :
        functions : Liste des définitions de fonctions autorisées.
        model : Le modèle LLM utilisé pour encoder les noms en tokens.

    Retourne :
        Un objet FunctionTrie peuplé.
    """
    trie = FunctionTrie()

    for function in functions:
        tokens = model.encode(function.name).tolist()[0]
        trie.insert(tokens, function.name)
    return trie


def _argmax_masked(
        logits: list[float], valid_tokens: list[int]) -> int:
    """
    Retourne l'index du logit maximal restreint à `valid_tokens`.

    Plus efficace que de construire un vecteur masqué complet quand
    l'ensemble valide est petit comparé au vocabulaire.
    """
    best_token = valid_tokens[0]
    best_logit = logits[best_token]
    for token_id in valid_tokens:
        if logits[token_id] > best_logit:
            best_logit = logits[token_id]
            best_token = token_id
    return best_token


def select_function(
        prompt: str,
        model: Small_LLM_Model,
        trie: FunctionTrie) -> str | None:
    """
    Génère un nom de fonction valide token par token via constrained decoding.

    À chaque étape, seuls les tokens enfants du noeud courant du trie sont
    autorisés ; tous les autres sont implicitement masqués via
    _argmax_masked.

    Arguments :
        prompt : La requête en langage naturel.
        model : L'instance du LLM.
        trie : Le Trie contenant les noms de fonctions valides.

    Retourne :
        Le nom de la fonction sélectionnée sous forme de chaîne.
    """
    input_ids: list[int] = model.encode(prompt).tolist()[0]
    tokens_generated: list[int] = []

    while True:
        valid_tokens = trie.get_valid_tokens(tokens_generated)
        if not valid_tokens:
            break
        logits = model.get_logits_from_input_ids(input_ids)
        max_token = _argmax_masked(logits, valid_tokens)
        tokens_generated.append(max_token)
        input_ids.append(max_token)
        if trie.is_function_complete(tokens_generated):
            break
    result = trie.get_fn_name(tokens_generated)
    if result is None:
        raise ValueError("Aucune fonction trouvée")
    return result


def _build_arg_prompt(
        base_prompt: str,
        param_name: str,
        param_type: str) -> str:
    """
    Construit un sous-prompt qui pousse le modèle à émettre la valeur
    d'un seul argument. Le décodeur contraint garantit toujours le format,
    mais un prompt plus clair améliore la qualité de la sélection.
    """
    return (
        f"{base_prompt}\n"
        f"Extrais la valeur de l'argument '{param_name}' "
        f"de type {param_type}. "
        f"Réponds uniquement avec la valeur :\n"
    )


def generate_argument(
        prompt: str,
        param_type: str,
        model: Small_LLM_Model,
        mapper: VocabularyMapper,
        param_name: str = "") -> str | float | bool:
    """
    Génère un argument de fonction contraint par un type de donnée spécifique.

    Arguments :
        prompt : Le prompt de contexte pour l'argument.
        param_type : Le type requis (boolean, number, string).
        model : L'instance du LLM.
        mapper : VocabularyMapper pour valider les tokens autorisés.
        param_name : Nom optionnel du paramètre généré, utilisé pour
                    affiner le prompt envoyé au modèle.

    Retourne :
        La valeur générée pour l'argument dans son type Python correct.

    Lève :
        ValueError : si un type de paramètre non supporté est fourni.
    """
    full_prompt = _build_arg_prompt(prompt, param_name, param_type) \
        if param_name else prompt

    if param_type == "boolean":
        valid_tokens = [
            mapper.str_to_token("true"),
            mapper.str_to_token("false"),
        ]
        input_ids: list[int] = model.encode(full_prompt).tolist()[0]
        logits = model.get_logits_from_input_ids(input_ids)
        max_token = _argmax_masked(logits, valid_tokens)
        return mapper.token_to_str(max_token) == "true"

    if param_type == "number":
        # Tokens pouvant débuter un nombre (chiffres ou signe moins).
        start_tokens = mapper.number_start_tokens()
        input_ids = model.encode(full_prompt).tolist()[0]
        number_tokens: list[int] = []
        # Le premier token doit débuter un nombre.
        logits = model.get_logits_from_input_ids(input_ids)
        first = _argmax_masked(logits, start_tokens)
        number_tokens.append(first)
        input_ids.append(first)
        # Les tokens suivants peuvent prolonger le nombre (chiffres ou '.').
        # On utilise un argmax non contraint et on s'arrête dès que le modèle
        # émet un token dont la chaîne décodée n'est pas faite de chiffres,
        # de '.' ou de '-'.
        while True:
            logits = model.get_logits_from_input_ids(input_ids)
            max_token = max(range(len(logits)), key=lambda i: logits[i])
            text = mapper.vocab_inverted.get(max_token, "")
            if not text or not all(c.isdigit() or c in ".-" for c in text):
                break
            number_tokens.append(max_token)
            input_ids.append(max_token)
        return float(model.decode(number_tokens))

    if param_type == "string":
        # Génération libre jusqu'à ce que le modèle émette un token
        # contenant le caractère terminateur d'une chaîne JSON.
        input_ids = model.encode(full_prompt).tolist()[0]
        string_tokens: list[int] = []
        while True:
            logits = model.get_logits_from_input_ids(input_ids)
            max_token = max(range(len(logits)), key=lambda i: logits[i])
            text = mapper.vocab_inverted.get(max_token, "")
            # Stop sur un guillemet, un retour à la ligne ou un token vide
            # pour garder la chaîne courte et bien formée.
            if not text or '"' in text or "\n" in text:
                break
            string_tokens.append(max_token)
            input_ids.append(max_token)
            # Plafond strict pour éviter une génération qui s'emballe.
            if len(string_tokens) >= 64:
                break
        return model.decode(string_tokens).strip()

    raise ValueError(f"Type de paramètre inconnu : {param_type}")
