"""API-equivalent cost (era 98 spec §3). Cost is recorded in API terms whatever the login, so a reader who pays per
token can read the same record. Prices come from measure/prices.json, which cites the official page and its date."""
import json
from pathlib import Path

PRICES = Path(__file__).resolve().parent / "prices.json"


def price(model):
    return json.loads(PRICES.read_text(encoding="utf-8"))["models"].get(model)


def api_equivalent(model, input_tokens, cached_input_tokens=0, output_tokens=0):
    """USD, or None when the model has no price entry. input_tokens counts all input, cached included (Codex's
    usage.input_tokens); reasoning tokens are part of output_tokens."""
    p = price(model)
    if p is None:
        return None
    uncached = max(0, input_tokens - cached_input_tokens)
    return round((uncached * p["input"] + cached_input_tokens * p["cached_input"] + output_tokens * p["output"]) / 1_000_000, 6)
