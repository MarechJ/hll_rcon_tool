from django.views.decorators.csrf import csrf_exempt

from rcon.discord import send_to_discord_audit
from rcon.map_recorder import VoteMap, VoteMapConfig

from .auth import api_response, login_required
from .utils import _get_data
from .views import audit


def votemap_config():
    config = VoteMapConfig()
    return {
        "vote_enabled": config.get_vote_enabled(),
        "votemap_number_of_options": config.get_votemap_number_of_options(),
        "votemap_ratio_of_offensives_to_offer": config.get_votemap_ratio_of_offensives_to_offer(),
        "votemap_number_of_last_played_map_to_exclude": config.get_votemap_number_of_last_played_map_to_exclude(),
        "votemap_consider_offensive_as_same_map": config.get_votemap_consider_offensive_as_same_map(),
        "votemap_allow_consecutive_offensives": config.get_votemap_allow_consecutive_offensives(),
        "votemap_allow_consecutive_offensives_of_opposite_side": config.get_votemap_allow_consecutive_offensives_of_opposite_side(),
        "votemap_default_method": config.get_votemap_default_method().value,
        "votemap_allow_default_to_offsensive": config.get_votemap_allow_default_to_offsensive(),
        "votemap_instruction_text": config.get_votemap_instruction_text(),
        "votemap_thank_you_text": config.get_votemap_thank_you_text(),
        "votemap_no_vote_text": config.get_votemap_no_vote_text(),
    }


@csrf_exempt
@login_required(True)
def get_votemap_config(request):
    return api_response(
        failed=False,
        command="get_votemap_config",
        result=votemap_config(),
    )


@csrf_exempt
@login_required(True)
def set_votemap_config(request):
    config = VoteMapConfig()
    data = _get_data(request)

    setters = {
        "vote_enabled": config.set_vote_enabled,
        "votemap_number_of_options": config.set_votemap_number_of_options,
        "votemap_ratio_of_offensives_to_offer": config.set_votemap_ratio_of_offensives_to_offer,
        "votemap_number_of_last_played_map_to_exclude": config.set_votemap_number_of_last_played_map_to_exclude,
        "votemap_consider_offensive_as_same_map": config.set_votemap_consider_offensive_as_same_map,
        "votemap_allow_consecutive_offensives": config.set_votemap_allow_consecutive_offensives,
        "votemap_allow_consecutive_offensives_of_opposite_side": config.set_votemap_allow_consecutive_offensives_of_opposite_side,
        "votemap_default_method": config.set_votemap_default_method,
        "votemap_allow_default_to_offsensive": config.set_votemap_allow_default_to_offsensive,
        "votemap_instruction_text": config.set_votemap_instruction_text,
        "votemap_thank_you_text": config.set_votemap_thank_you_text,
        "votemap_no_vote_text": config.set_votemap_no_vote_text,
    }

    for k, v in data.items():
        try:
            setters[k](v)
            audit("set_votemap_config", request, {k: v})
        except KeyError:
            return api_response(
                error="{} invalid key".format(k), command="set_votemap_config"
            )

    return api_response(
        failed=False, result=votemap_config(), command="set_votemap_config"
    )


@csrf_exempt
@login_required(True)
def get_votemap_status(request):
    v = VoteMap()
    return api_response(
        failed=False,
        result={
            "votes": v.get_votes(),
            "selection": v.get_selection(),
            "results": v.get_vote_overview(),
        },
        command="set_votemap_config",
    )


@csrf_exempt
@login_required(True)
def reset_votemap_state(request):
    if request.method != "POST":
        return api_response(
            failed=True,
            result={
                "votes": v.get_votes(),
                "selection": v.get_selection(),
                "results": v.get_vote_overview(),
            },
            command="reset_votemap_state",
        )
    audit("reset_votemap_state", request, {})
    v = VoteMap()
    v.clear_votes()
    v.gen_selection()
    v.apply_results()
    return api_response(
        failed=False,
        result={
            "votes": v.get_votes(),
            "selection": v.get_selection(),
            "results": v.get_vote_overview(),
        },
        command="reset_votemap_state",
    )
