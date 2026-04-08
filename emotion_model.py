"""
Emotion-recognition model wrapper.

Currently wraps **emotion2vec** via the FunASR toolkit.  The rest of the
pipeline only depends on the public interface defined below, so swapping
to a different backbone (HuBERT, wav2vec 2.0, Whisper features + head,
your own model, …) only requires changing *this* file.

=======================================================================
MODEL SWAP GUIDE
=======================================================================
To replace emotion2vec with a custom model:

1.  Create a new class that exposes:

        class YourModel:
            def __init__(self, model_name: str, device: str = "cpu"): ...

            @property
            def dimensions(self) -> list[str]:
                \"\"\"Ordered list of output dimension / label names.\"\"\"
                ...

            def predict(self, audio: np.ndarray, sr: int = 16000) -> dict:
                \"\"\"
                Returns:
                    {
                        "label":      str,              # top-scoring dimension
                        "confidence": float,             # its score in [0, 1]
                        "scores":     dict[str, float],  # {dim_name: score}
                    }
                \"\"\"
                ...

2.  In main.py, change the import:

        from emotion_model import YourModel as EmotionModel

    and update CONFIG["model_name"] if needed.

EXAMPLE — HuBERT with a HuggingFace classification head:

    class HuBERTEmotionModel:
        def __init__(self, model_name="superb/hubert-large-superb-er", device="cpu"):
            from transformers import (
                AutoModelForAudioClassification,
                AutoFeatureExtractor,
            )
            self.extractor = AutoFeatureExtractor.from_pretrained(model_name)
            self.model = AutoModelForAudioClassification.from_pretrained(model_name)
            self.model.to(device).eval()
            self._device = device
            self._dims = list(self.model.config.id2label.values())

        @property
        def dimensions(self):
            return self._dims

        def predict(self, audio, sr=16000):
            import torch
            inputs = self.extractor(audio, sampling_rate=sr, return_tensors="pt")
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()
            scores = {d: float(p) for d, p in zip(self._dims, probs)}
            label = max(scores, key=scores.get)
            return {"label": label, "confidence": scores[label], "scores": scores}

=======================================================================
"""

from __future__ import annotations

import numpy as np


class Emotion2VecModel:
    """Wraps emotion2vec (FunASR) for utterance-level emotion recognition."""

    # --- DIMENSION DEFINITIONS ------------------------------------------------
    # emotion2vec_plus outputs 9 categories.  If you fine-tune or relabel,
    # update this list *and* make sure the model's output order matches.
    DIMENSIONS = [
        "angry",
        "disgusted",
        "fearful",
        "happy",
        "neutral",
        "other",
        "sad",
        "surprised",
        "unknown",
    ]

    def __init__(
        self,
        model_name: str = "iic/emotion2vec_plus_large",
        device: str = "cpu",
    ):
        from funasr import AutoModel  # lazy import keeps startup fast if unused

        self._model = AutoModel(model=model_name, device=device)
        self._dimensions = list(self.DIMENSIONS)

    # ---- public interface ----------------------------------------------------

    @property
    def dimensions(self) -> list[str]:
        return self._dimensions

    def predict(self, audio: np.ndarray, sr: int = 16000) -> dict:
        """
        Run utterance-level emotion inference on a mono audio chunk.

        Args:
            audio: 1-D float32 numpy array, mono, sampled at *sr* Hz.
            sr:    Sample rate (emotion2vec expects 16 000).

        Returns:
            {
                "label":      str,
                "confidence": float,
                "scores":     {dimension_name: float, …},
            }
        """
        result = self._model.generate(
            audio,
            granularity="utterance",
            extract_embedding=False,
        )

        # funasr returns a list[dict]; take the first entry
        entry = result[0] if result else {}

        labels = entry.get("labels", self._dimensions)
        scores_list = entry.get("scores", [0.0] * len(self._dimensions))

        scores: dict[str, float] = {}
        for lbl, sc in zip(labels, scores_list):
            scores[lbl] = float(sc)

        top_label = entry.get("text", max(scores, key=scores.get))
        top_score = scores.get(top_label, 0.0)

        return {
            "label": top_label,
            "confidence": top_score,
            "scores": scores,
        }
