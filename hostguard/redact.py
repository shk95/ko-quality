"""redact(text) for writers of committed summaries (era 98 spec §3): host literals and fixed patterns become placeholders.
The logger's mask() is shipped behaviour (09 §11) and is not changed; this is for records this repository commits."""
from hostguard import local, rules

PLACEHOLDER = {
    "host:home": "~",
    "host:repo-path": "<repository>",
    "host:repo-path-hash": "<project hash>",
    "host:project-slug": "<project slug>",
    "host:user-in-path": "/<user>/",
    "host:hostname": "<host>",
    "host:user-marketplace": "<user-scope marketplace>",
    "host:user-plugin": "<user-scope plugin>",
    "host:model-setting": "<model setting>",
    "fixed:tmp-path": "<tmp>/",
    "fixed:nix-path": "<system>/",
    "fixed:scratch-path": "<scratch>/",
    "fixed:uuid": "<local>",
}


def redact(text, repo=rules.ROOT):
    lits = rules.host_literals(repo) + local.remembered()
    # longest values first, so the repository path wins over the home it sits in
    ordered = sorted(dict.fromkeys(lits), key=lambda rv: -len(rv[1]))
    for rule, value in ordered:
        text = rules.matcher(rule, value).sub(PLACEHOLDER.get(rule, "<host>"), text)
    for rule, rx in rules.FIXED:
        if rule in PLACEHOLDER:
            text = rx.sub(lambda m, r=rule: m.group(0) if rules.placeholder(r, m.group(0)) else PLACEHOLDER[r], text)
    return text
