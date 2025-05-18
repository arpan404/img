import warnings

# silence the torch.weight_norm deprecation
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*weight_norm is deprecated.*"
)

import librosa.effects  # for true time‐stretch
import soundfile as sf
from dia.model import Dia


def synthesize(
    text: str,
    out_path: str,
    sr: int = 44100,
    speed: float = 0.8,    # default slower
    ref_wav: str | None = None,
) -> None:
    """
    Generate waveform for `text` (ref_wav ignored), slow by `speed`, and write to `out_path`.

    :param text: Text to synthesize

    :return: None
    """
    model = Dia.from_pretrained("nari-labs/Dia-1.6B")
    # plain text, no SSML
    waveform = model.generate(text)
    # true slow down
    if speed != 1.0:
        waveform = librosa.effects.time_stretch(waveform, rate=speed)
    # write at fixed sample rate to preserve timing
    sf.write(out_path, waveform, sr)
