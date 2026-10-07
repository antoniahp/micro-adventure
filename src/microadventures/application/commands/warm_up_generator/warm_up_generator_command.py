from dataclasses import dataclass


@dataclass(frozen=True)
class WarmUpGeneratorCommand:
    """Asks the generator to get ready, for example while the person is still filling the form."""
