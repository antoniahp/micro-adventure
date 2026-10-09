import random
from uuid import uuid4

from microadventures.domain.models.challenge import Challenge
from microadventures.domain.models.challenge_brief import ChallengeBrief
from microadventures.domain.models.challenge_category import ChallengeCategory
from microadventures.domain.models.language import Language
from microadventures.domain.services.challenge_generator import ChallengeGenerator

CHALLENGE_TEXTS_ES = {
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

CHALLENGE_TEXTS_EN = {
    ChallengeCategory.SENSORY: [
        "Touch something soft outdoors: a leaf, moss or a petal.",
        "Find something with a rough texture and feel it slowly.",
        "Compare the temperature of a stone surface and a metal one.",
    ],
    ChallengeCategory.SOUND: [
        "Find a singing bird and listen to it for one minute.",
        "Locate the farthest sound you can hear.",
        "Look for the sound of water: a fountain, a stream or a drain.",
    ],
    ChallengeCategory.CULTURE: [
        "Find a church or a chapel and look closely at its door.",
        "Spot the town hall or a building with a coat of arms.",
        "Find a plaque or a monument and read who it remembers.",
    ],
    ChallengeCategory.NATURE: [
        "Find the oldest tree on your walk.",
        "Look for a wild flower and compare its colour with another.",
        "Find an insect or an animal track.",
    ],
    ChallengeCategory.PEOPLE_WATCHING: [
        "Spot someone wearing something purple, without approaching or taking photos.",
        "Spot someone walking a dog and imagine its name.",
        "Count how many people wear a cap in five minutes.",
    ],
}

CHALLENGE_TEXTS = {Language.ES: CHALLENGE_TEXTS_ES, Language.EN: CHALLENGE_TEXTS_EN}

# After dark or under rain only these are offered: lit streets, busy places, covered spots.
CALM_TEXTS_ES = {
    ChallengeCategory.SENSORY: [
        "Toca algo liso y fresco junto a un portal con luz: un cristal, una barandilla o una puerta.",
        "Abre las manos y nota cómo cambia la temperatura al pasar de una calle a otra.",
    ],
    ChallengeCategory.SOUND: [
        "Escucha un minuto: ¿qué suena más fuerte, el tráfico, las voces o la lluvia?",
        "Localiza el sonido más suave que te llegue desde un lugar con luz.",
    ],
    ChallengeCategory.CULTURE: [
        "Busca una fachada iluminada y fíjate en un detalle que de día pasarías por alto.",
        "Encuentra un escaparate con luz y piensa a quién le gustaría lo que hay dentro.",
    ],
    ChallengeCategory.NATURE: [
        "Busca un árbol de la calle iluminado por una farola y mira cómo cae la luz en sus hojas.",
        "Mira el cielo desde un sitio con luz: ¿ves alguna estrella, la luna o las nubes?",
    ],
    ChallengeCategory.PEOPLE_WATCHING: [
        "Fíjate en una cafetería o tienda con luz y cuenta cuántas personas entran en cinco minutos.",
        "Encuentra una ventana encendida e imagina qué se cocina dentro, sin acercarte.",
    ],
}

CALM_TEXTS_EN = {
    ChallengeCategory.SENSORY: [
        "Touch something smooth and cool by a lit doorway: a glass pane, a railing or a door.",
        "Open your hands and notice how the temperature changes from one street to the next.",
    ],
    ChallengeCategory.SOUND: [
        "Listen for a minute: what is louder, the traffic, the voices or the rain?",
        "Find the softest sound reaching you from a lit place.",
    ],
    ChallengeCategory.CULTURE: [
        "Find a lit-up facade and notice a detail you would miss by day.",
        "Find a lit shop window and think of who would love what is inside.",
    ],
    ChallengeCategory.NATURE: [
        "Find a street tree lit by a lamp and watch how the light falls on its leaves.",
        "Look at the sky from a lit spot: can you see a star, the moon or the clouds?",
    ],
    ChallengeCategory.PEOPLE_WATCHING: [
        "Watch a lit cafe or shop and count how many people go in during five minutes.",
        "Find a lit window and imagine what is cooking inside, without going near.",
    ],
}

CALM_TEXTS = {Language.ES: CALM_TEXTS_ES, Language.EN: CALM_TEXTS_EN}


class TemplateChallengeGenerator(ChallengeGenerator):
    """Offline generator: picks from a fixed bank. Used in tests and as fallback."""

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def generate(self, brief: ChallengeBrief) -> list[Challenge]:
        categories = [brief.category] if brief.category else list(ChallengeCategory)
        self.rng.shuffle(categories)

        texts = CALM_TEXTS if brief.conditions.needs_calm_walk else CHALLENGE_TEXTS
        challenges = []
        for index in range(brief.count):
            category = categories[index % len(categories)]
            challenges.append(Challenge(id=uuid4(), category=category, text=self.rng.choice(texts[brief.language][category])))
        return challenges
