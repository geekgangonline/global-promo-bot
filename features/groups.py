# All group chat IDs managed by the bot

GROUPS = {
    "engagement": -5168467207,
    "lounge": -5171489499,
    "collective": -5213568788,
    "stream": -5112538513,
    "thread": -4940260799,
    "runway": -5165924184,
    "cypher": -5259611243,
    "soundwave": -5168034856,
    "affiliates": -5191183874,
    "hive": -5204817164,
    "dailygrind": -4950889720,
}

TIERS = {
    "tier1": ["engagement", "lounge", "collective"],
    "tier2": ["cypher", "stream", "thread", "runway", "dailygrind"],
    "tier3": ["soundwave", "affiliates", "hive"],
}

def group_ids():
    return {k: v for k, v in GROUPS.items() if v}

def all_chat_ids():
    return [v for v in GROUPS.values() if v]

def get_group_tier(group_id):
    for tier, keys in TIERS.items():
        for key in keys:
            if GROUPS.get(key) == group_id:
                return tier
    return None

def tier_chat_ids(tier):
    return [GROUPS[k] for k in TIERS.get(tier, []) if GROUPS.get(k)]

def tier_group_keys(tier):
    return list(TIERS.get(tier, []))

# All engagement groups (Tier 1 + Tier 2) for daily reminders
ENGAGEMENT_GROUPS = TIERS["tier1"] + TIERS["tier2"]
