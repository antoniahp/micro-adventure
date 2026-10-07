import random
from uuid import uuid4

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.services.challenge_generator import ChallengeGenerator

CHALLENGE_TEXTS = {
    ChallengeCategory.SENSORY: [
        "Toca algo suave al aire libre: una hoja, musgo o un pétalo.",
        "Encuentra algo de textura rugosa y tócalo con calma.",
        "Compara la temperatura de una superficie de piedra y una de metal.",
    ],
    ChallengeCategory.SOUND: [
        "Encuentra un pájaro que cante y escúchalo durante un minuto.",
        "Localiza el sonido más lejano que seas capaz de oír.",
        "Busca el sonido del agua: una fuente, un arroyo o un desagüe.",
    ],
    ChallengeCategory.CULTURE: [
        "Encuentra una iglesia o una ermita y fíjate en su puerta.",
        "Localiza el ayuntamiento o un edificio con escudo.",
        "Busca una placa o un monumento y lee a quién recuerda.",
    ],
    ChallengeCategory.NATURE: [
        "Encuentra el árbol más viejo de tu paseo.",
        "Busca una flor silvestre y compara su color con otra.",
        "Encuentra un insecto o la huella de un animal.",
    ],
    ChallengeCategory.PEOPLE_WATCHING: [
        "Encuentra a alguien con algo de color lila, sin acercarte ni hacer fotos.",
        "Encuentra a alguien paseando a su perro e imagina cómo se llama.",
        "Cuenta cuántas personas llevan gorra en cinco minutos.",
    ],
}


class TemplateChallengeGenerator(ChallengeGenerator):
    """Offline generator: picks from a fixed bank. Used in tests and as fallback."""

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def generate(self, brief: ChallengeBrief) -> list[Challenge]:
        categories = [brief.category] if brief.category else list(ChallengeCategory)
        self.rng.shuffle(categories)

        challenges = []
        for index in range(brief.count):
            category = categories[index % len(categories)]
            challenges.append(Challenge(id=uuid4(), category=category, text=self.rng.choice(CHALLENGE_TEXTS[category])))
        return challenges
