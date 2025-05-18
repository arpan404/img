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
    voice: str = "default",
    ref_wav: str | None = None,
) -> None:
    """
    Generate waveform for `text` at a natural pace and write to `out_path`.
    """
    model = Dia.from_pretrained("nari-labs/Dia-1.6B")
    # wrap in SSML prosody: e.g. 80%–120% of normal
    rate_pct = int(speed * 100)
    ssml = f"<speak><prosody rate='{rate_pct}%'>{text}</prosody></speak>"
    waveform = model.generate(ssml)
    # write at fixed sample rate for faithful timing
    sf.write(out_path, waveform, sr)
