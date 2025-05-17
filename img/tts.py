import warnings
# silence the torch.weight_norm deprecation
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*weight_norm is deprecated.*"
)

import soundfile as sf
from dia.model import Dia

def synthesize(
    text: str,
    out_path: str,
    sr: int = 44100,
    speed: float = 1.0,
    ref_wav: str | None = None,
) -> None:
    """
    Generate waveform for `text` (ref_wav ignored) and write to `out_path`.
    """
    # plain text to avoid SSML/pitch artifacts
    model = Dia.from_pretrained("nari-labs/Dia-1.6B")
    waveform = model.generate(text)

    # adjust playback speed via write‐rate scaling
    write_sr = int(sr * speed)
    sf.write(out_path, waveform, write_sr)
