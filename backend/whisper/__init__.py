import io
import os
from typing import Optional, Union

import torch

from .audio import load_audio, log_mel_spectrogram, pad_or_trim
from .decoding import DecodingOptions, DecodingResult, decode, detect_language
from .model import Whisper, ModelDimensions
from .transcribe import transcribe



def load_model(name: str, device: Optional[Union[str, torch.device]] = None, in_memory: bool = False) -> Whisper:
    """
    Load a Whisper ASR model

    Parameters
    ----------
    name : str
        one of the official model names listed by `whisper.available_models()`, or
        path to a model checkpoint containing the model dimensions and the model state_dict.
    device : Union[str, torch.device]
        the PyTorch device to put the model into
        path to download the model files; by default, it uses "~/.cache/whisper"
    in_memory: bool
        whether to preload the model weights into host memory

    Returns
    -------
    model : Whisper
        The Whisper ASR model instance
    """

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if os.path.isfile(name):
        checkpoint_file = open(name, "rb").read() if in_memory else name
    else:
        raise RuntimeError(f"Model {name} not found")

    with (io.BytesIO(checkpoint_file) if in_memory else open(checkpoint_file, "rb")) as fp:
        checkpoint = torch.load(fp, map_location=device)
    del checkpoint_file

    dims = ModelDimensions(**checkpoint["dims"])
    model = Whisper(dims)
    model.load_state_dict(checkpoint["model_state_dict"])

    return model.to(device)
