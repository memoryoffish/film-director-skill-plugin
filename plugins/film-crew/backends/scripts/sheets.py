"""Reading a job sheet: video or image, which feed, which backend.

The format is formats/job-sheet.md, beside this backends folder."""
from __future__ import annotations

import ark_video
import bailian
import minimax_video
import openai_image

MEDIA = ("reference_images", "reference_video", "first_frame", "last_frame")  # video media fields
IMAGE_FIELDS = ("images", "size", "n", "quality")                             # only image sheets have these


def kind(sheet: dict) -> str:
    """"video" or "image": an explicit "kind" wins; else a gpt-image model or any image-only field makes it an image."""
    if sheet.get("kind"):
        return sheet["kind"]
    if str(sheet.get("model") or "").startswith("gpt-image") or any(k in sheet for k in IMAGE_FIELDS):
        return "image"
    return "video"


def feed(sheet: dict) -> str:
    """Told from the media fields: t2v, first_frame, first_last, refs, ref_video (videos); t2i, edit (images)."""
    if kind(sheet) == "image":
        return "edit" if sheet.get("images") else "t2i"
    frames = sheet.get("first_frame"), sheet.get("last_frame")
    if frames[1] and not frames[0]:
        raise ValueError(f"{sheet.get('name')}: last_frame needs a first_frame")
    if any(frames) and (sheet.get("reference_images") or sheet.get("reference_video")):
        raise ValueError(f"{sheet.get('name')}: first/last frame do not go with reference images or a reference video")
    if sheet.get("reference_video"):
        return "ref_video"
    if sheet.get("reference_images"):
        return "refs"
    return "first_last" if frames[1] else "first_frame" if frames[0] else "t2v"


def backend(sheet: dict):
    """The adapter module for the sheet's model."""
    model = str(sheet.get("model") or "")
    if kind(sheet) == "image":
        if not model or model.startswith("gpt-image"):
            return openai_image
    elif not model or model.startswith(("wan", "happyhorse")):
        return bailian
    elif model in ark_video.MODELS:
        return ark_video
    elif model in minimax_video.MODELS:
        return minimax_video
    raise ValueError(f"{sheet.get('name')}: no backend for {kind(sheet)} model {model!r}")
