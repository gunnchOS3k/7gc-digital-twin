from .schema import REQUIRED_SCENE_FIELDS


def validate_site_config(cfg: dict) -> list[str]:
    errs = []
    for k in REQUIRED_SCENE_FIELDS:
        if k not in cfg:
            errs.append(f"missing {k}")
    if len(cfg.get("anchor_use_cases", [])) < 3:
        errs.append("need >=3 anchor use cases")
    if len(cfg.get("resilience_use_cases", [])) < 2:
        errs.append("need >=2 resilience use cases")
    if len(cfg.get("bad_day_scenarios", [])) < 5:
        errs.append("need >=5 bad_day scenarios")
    return errs
