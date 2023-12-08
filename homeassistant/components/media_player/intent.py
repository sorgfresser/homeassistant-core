"""Intents for the media_player integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent

from . import DOMAIN, MediaPlayerEntity, MediaPlayerState

INTENT_MP_TURN_ON = "HassMediaPlayerTurnOn"
INTENT_MP_TURN_OFF = "HassMediaPlayerTurnOff"


async def async_setup_intents(hass: HomeAssistant) -> None:
    """Set up the media_player intents."""
    intent.async_register(hass, MediaPlayerTurnOnIntent())
    intent.async_register(hass, MediaPlayerTurnOffIntent())


class MediaPlayerTurnOnIntent(intent.IntentHandler):
    """Handle MediaPlayerTurnOn intents."""

    intent_type = INTENT_MP_TURN_ON
    slot_schema = {"name": cv.string}

    async def async_handle(self, intent_obj: intent.Intent):
        """Handle the intent."""
        hass = intent_obj.hass

        # Parse media player name
        slots = self.async_validate_slots(intent_obj.slots)
        name = slots["name"]["value"]

        component: EntityComponent[MediaPlayerEntity] = hass.data[DOMAIN]

        # Find first matching media player
        media_player: MediaPlayerEntity | None = None
        for media_state in intent.async_match_states(hass, name=name, domains=[DOMAIN]):
            media_player = component.get_entity(media_state.entity_id)
            if media_player is not None:
                break
        if media_player is None:
            raise intent.IntentHandleError(f"No media player named {name} found")

        assert media_player is not None

        # Turn on media player
        await media_player.async_turn_on()

        response = intent_obj.create_response()
        response.response_type = intent.IntentResponseType.ACTION_DONE
        return response


class MediaPlayerTurnOffIntent(intent.IntentHandler):
    """Handle MediaPlayerTurnOff intents."""

    intent_type = INTENT_MP_TURN_OFF

    async def async_handle(self, intent_obj: intent.Intent):
        """Handle the intent."""
        hass = intent_obj.hass

        component: EntityComponent[MediaPlayerEntity] = hass.data[DOMAIN]

        # Find first playing media player
        media_player: MediaPlayerEntity | None = None
        for media_state in intent.async_match_states(hass, domains=[DOMAIN]):
            media_player_to_check = component.get_entity(media_state.entity_id)
            if (
                media_player_to_check is not None
                and media_player_to_check.state == MediaPlayerState.PLAYING
            ):
                media_player = media_player_to_check
                break

        if media_player is None:
            raise intent.IntentHandleError("No media player currently playing found")

        assert media_player is not None

        # Turn off media player
        await media_player.async_turn_off()

        response = intent_obj.create_response()
        response.response_type = intent.IntentResponseType.ACTION_DONE
        return response
