from uuid import UUID, uuid4

from ninja import File, Form, Router, Status
from ninja.files import UploadedFile

from api import wiring
from api.schemas import StartWalkIn, WalkCreatedOut, WalkOut
from microadventures.application.commands.complete_challenge.complete_challenge_command import CompleteChallengeCommand
from microadventures.application.queries.find_walk.find_walk_query import FindWalkQuery
from microadventures.application.commands.start_walk.start_walk_command import StartWalkCommand
from microadventures.application.commands.swap_challenge.swap_challenge_command import SwapChallengeCommand

router = Router()


@router.post("", response={201: WalkCreatedOut})
def start_walk(request, payload: StartWalkIn):
    walk_id = uuid4()
    wiring.start_walk_handler().handle(
        StartWalkCommand(
            walk_id=walk_id,
            user_id=payload.user_id,
            mood=payload.mood,
            minutes=payload.minutes,
            weather=payload.weather,
            challenges_count=payload.challenges_count,
            note=payload.note.strip(),
            language=payload.language,
        )
    )
    return Status(201, {"id": walk_id})


@router.get("/{walk_id}", response=WalkOut)
def get_walk(request, walk_id: UUID):
    return wiring.find_walk_handler().handle(FindWalkQuery(walk_id=walk_id))


@router.post("/{walk_id}/challenges/{challenge_id}/complete", response={204: None})
def complete_challenge(
    request, walk_id: UUID, challenge_id: UUID, photo: UploadedFile = File(None), story: str = Form("")
):
    wiring.complete_challenge_handler().handle(
        CompleteChallengeCommand(
            walk_id=walk_id,
            challenge_id=challenge_id,
            photo=photo.read() if photo else None,
            story=story,
        )
    )
    return Status(204, None)


@router.post("/{walk_id}/challenges/{challenge_id}/swap", response={204: None})
def swap_challenge(request, walk_id: UUID, challenge_id: UUID):
    wiring.swap_challenge_handler().handle(SwapChallengeCommand(walk_id=walk_id, challenge_id=challenge_id))
    return Status(204, None)
