from deepface import DeepFace

def verify_face(reference_img_path: str, selfie_img_path: str):
    result = DeepFace.verify(
        img1_path=reference_img_path,
        img2_path=selfie_img_path,
        enforce_detection=True,
        detector_backend="opencv",
        model_name="VGG-Face",
        distance_metric="cosine"
    )
    is_match = bool(result.get("verified", False))
    distance = float(result.get("distance", 999.0))
    confidence = max(0.0, 1.0 - distance)
    return is_match, confidence
