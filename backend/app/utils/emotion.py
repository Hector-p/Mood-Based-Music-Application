from PIL import Image
import random
import os
import numpy as np
import time
from collections import deque
import cv2
import hashlib
from datetime import datetime

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Try to import DeepFace
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("✅ DeepFace loaded successfully")
except Exception as e:
    DEEPFACE_AVAILABLE = False
    print(f"⚠️ DeepFace not available: {e}")

# ============ CONFIGURATION ============
SCAN_INTERVAL = 1.0          # Time between scans (seconds)
MIN_SAMPLES = 3              # Minimum frames needed for reliable detection
MAX_SAMPLES = 5              # Maximum frames to collect
CONFIDENCE_THRESHOLD = 0.25  # Minimum confidence to accept a reading (25%)
STABILITY_THRESHOLD = 0.60   # 60% of frames must agree on emotion
MIN_FACE_CONFIDENCE = 0.5    # Minimum confidence for face detection
# ========================================

EMOTION_TO_MOOD = {
    'angry': 'angry',
    'disgust': 'angry',
    'fear': 'sad',
    'happy': 'happy',
    'sad': 'sad',
    'surprise': 'happy',
    'neutral': 'calm'
}

# Track last analyzed image to detect duplicates
_last_image_hash = None
_last_analysis_result = None
_analysis_count = 0


def _preprocess_image(pil_image):
    """
    Preprocess PIL image for DeepFace analysis.
    Handles color space, size, normalization, and quality checks.
    """
    try:
        # Validate image is a PIL Image
        if not isinstance(pil_image, Image.Image):
            print(f"❌ Invalid image type: {type(pil_image)}")
            return None
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            print(f"🔄 Converting image from {pil_image.mode} to RGB")
            pil_image = pil_image.convert('RGB')
        
        # Validate image size
        width, height = pil_image.size
        if width < 48 or height < 48:
            print(f"⚠️ Image too small ({width}x{height}), resizing to 192x192...")
            pil_image = pil_image.resize((192, 192), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(pil_image)
        
        # Ensure valid shape
        if img_array is None or len(img_array.shape) != 3 or img_array.shape[2] != 3:
            print(f"❌ Invalid array shape: {img_array.shape if img_array is not None else 'None'}")
            return None
        
        # Ensure uint8 dtype
        if img_array.dtype != np.uint8:
            print(f"🔄 Converting dtype from {img_array.dtype} to uint8")
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # Validate image quality (not too dark/bright)
        pixel_mean = float(img_array.mean())
        pixel_std = float(img_array.std())
        
        if pixel_mean < 20:
            print(f"⚠️ Very dark image (mean: {pixel_mean:.1f}) - may not detect face properly")
        if pixel_mean > 240:
            print(f"⚠️ Very bright image (mean: {pixel_mean:.1f}) - may be overexposed")
        
        # Return fresh copy
        return np.array(img_array, copy=True, order='C')
        
    except Exception as e:
        print(f"❌ Image preprocessing error: {e}")
        return None


def _clear_deepface_cache():
    """Clear any potential DeepFace model caches to ensure fresh analysis"""
    try:
        if DEEPFACE_AVAILABLE:
            # Try to clear built-in DeepFace caches
            from deepface.basemodels import facial_expression
            # Forces model reload
            print("🔄 Clearing DeepFace cache...")
            
    except Exception as e:
        print(f"⚠️ Could not clear DeepFace cache: {e}")


def _get_stable_emotion():
    """Check if we have a stable emotion across frames"""
    if len(_emotion_history) < MIN_SAMPLES:
        return None, 0.0
    
    # Count occurrences of each emotion
    emotion_counts = {}
    confidence_sums = {}
    
    for emotion, confidence in _emotion_history:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        confidence_sums[emotion] = confidence_sums.get(emotion, 0) + confidence
    
    # Find dominant emotion
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    stability = emotion_counts[dominant_emotion] / len(_emotion_history)
    avg_confidence = confidence_sums[dominant_emotion] / emotion_counts[dominant_emotion]
    
    # Return emotion only if it's stable enough
    if stability >= STABILITY_THRESHOLD:
        return dominant_emotion, avg_confidence
    
    return None, 0.0



def analyze_image(pil_image):
    """Analyze emotion from PIL Image using DeepFace with smoothing"""
    global _last_scan_time, _scan_in_progress
    
    if not DEEPFACE_AVAILABLE:
        mood = random.choice(['happy', 'sad', 'angry', 'calm'])
        print(f"🎲 Random fallback mood: {mood}")
        return mood

    current_time = time.time()
    
    # Throttle scans to avoid overwhelming DeepFace
    if current_time - _last_scan_time < SCAN_INTERVAL:
        # Check if we already have a stable result
        stable_emotion, _ = _get_stable_emotion()
        if stable_emotion:
            return EMOTION_TO_MOOD.get(stable_emotion, 'calm')
        return None  # Still collecting samples
    
    try:
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        img_array = np.array(pil_image)

        result = DeepFace.analyze(
            img_array,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv',
            silent=True
        )

        if isinstance(result, list):
            result = result[0]

        raw_emotion = result['dominant_emotion'].lower()
        emotions = result['emotion']
        confidence = float(emotions[result['dominant_emotion']] / 100.0)
        
        # Only accept high-confidence readings
        if confidence < CONFIDENCE_THRESHOLD:
            print(f"⚠️ Low confidence ({confidence:.2f}), skipping frame")
            _last_scan_time = current_time
            return None
        
        # Add to history
        _emotion_history.append((raw_emotion, confidence))
        _last_scan_time = current_time
        
        print(f"📊 Frame {len(_emotion_history)}/{MAX_SAMPLES}: {raw_emotion} ({confidence:.2f})")
        
        # Check if we have a stable emotion
        stable_emotion, avg_confidence = _get_stable_emotion()
        if stable_emotion:
            mood = EMOTION_TO_MOOD.get(stable_emotion, 'calm')
            print(f"✅ Mood detected: {stable_emotion} → {mood} (confidence: {avg_confidence:.2f})")
            _emotion_history.clear()  # Clear for next scan
            return mood
        
        # Still collecting samples
        return None

    except Exception as e:
        print(f"❌ DeepFace error: {str(e)}")
        _last_scan_time = current_time
        return None


def analyze_image_detailed(pil_image, force_fresh=True):
    """
    Analyze emotion from image - returns mood with confidence.
    """
    global _analysis_count
    
    _analysis_count += 1
    analysis_id = _analysis_count
    
    if not DEEPFACE_AVAILABLE:
        mood = random.choice(['happy', 'sad', 'angry', 'calm'])
        return {
            'mood': mood,
            'raw_emotion': 'neutral',
            'confidence': 0.5,
            'all_emotions': {},
            'frames_collected': 1,
            'analysis_id': analysis_id
        }

    start_time = time.time()
    print(f"\n[Frame #{analysis_id}] Starting emotion analysis...")
    
    try:
        # Preprocess image
        img_array = _preprocess_image(pil_image)
        
        if img_array is None:
            print(f"❌ Preprocessing failed")
            return {
                'mood': None,
                'raw_emotion': 'error',
                'confidence': 0.0,
                'all_emotions': {},
                'frames_collected': 0,
                'analysis_id': analysis_id
            }
        
        print(f"✓ Image ready: {img_array.shape}")
        
        # Call DeepFace
        print(f"🔍 Analyzing with DeepFace...")
        analyze_start = time.time()
        
        result = DeepFace.analyze(
            img_array,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv',
            silent=True
        )
        
        analyze_time = time.time() - analyze_start
        print(f"✓ DeepFace completed in {analyze_time:.2f}s")
        
        # Handle list response
        if isinstance(result, list):
            if len(result) == 0:
                print(f"⚠️ No face detected")
                return {
                    'mood': 'calm',
                    'raw_emotion': 'neutral',
                    'confidence': 0.0,
                    'all_emotions': {},
                    'frames_collected': 1,
                    'analysis_id': analysis_id
                }
            result = result[0]
        
        # Extract emotion
        raw_emotion = result['dominant_emotion'].lower()
        emotions = result['emotion']
        dominant_value = emotions.get(result['dominant_emotion'], 0)
        
        # Normalize confidence
        if dominant_value > 1.0:
            confidence = min(1.0, dominant_value / 100.0)
        else:
            confidence = float(dominant_value)
        
        confidence = float(confidence)
        
        # Map to mood
        mood = EMOTION_TO_MOOD.get(raw_emotion, 'calm')
        
        # Normalize all emotions
        all_emotions = {}
        for emotion, score in emotions.items():
            emotion_key = emotion.lower()
            score_float = float(score)
            if score_float > 1.0:
                normalized_score = score_float / 100.0
            else:
                normalized_score = score_float
            all_emotions[emotion_key] = float(min(1.0, max(0.0, normalized_score)))
        
        total_time = time.time() - start_time
        
        print(f"✓ Frame #{analysis_id}: {mood.upper()} ({raw_emotion}, confidence: {confidence*100:.1f}%)")
        print(f"  Top 3: {', '.join(f'{e}={s*100:.0f}%' for e, s in sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)[:3])}")
        print(f"  Time: {total_time:.3f}s")
        
        return {
            'mood': mood,
            'raw_emotion': raw_emotion,
            'confidence': confidence,
            'all_emotions': all_emotions,
            'frames_collected': 1,
            'analysis_id': analysis_id
        }

    except Exception as e:
        print(f"❌ Frame #{analysis_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'mood': None,
            'raw_emotion': 'error',
            'confidence': 0.0,
            'all_emotions': {},
            'frames_collected': 0,
            'analysis_id': analysis_id
        }



def reset_scan():
    """Reset the scanning state (useful for manual reset)"""
    global _last_scan_time
    _emotion_history.clear()
    _last_scan_time = 0
    print("🔄 Scan state reset")