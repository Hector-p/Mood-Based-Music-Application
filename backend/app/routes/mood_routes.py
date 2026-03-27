from flask import Blueprint, request, jsonify
from app.utils.emotion import analyze_image_detailed
from PIL import Image
import io
import base64
import numpy as np

mood_bp = Blueprint('mood', __name__)


@mood_bp.route('/detect', methods=['POST'])
def detect():
    """
    Detect mood from uploaded image(s).
    Accepts either:
    - Single image: { "image": "base64_encoded_image" }
    - Multiple images: { "images": [...], "multi_frame": true }
    """
    images = []
    
    try:
        # Check for multiple frames
        if request.is_json:
            data = request.get_json()
            
            if data.get('multi_frame') and 'images' in data:
                print(f"📦 Processing {len(data['images'])} frames for consensus analysis...")
                
                for idx, img_data in enumerate(data['images']):
                    try:
                        image_str = img_data['data'] if isinstance(img_data, dict) else img_data
                        
                        # Remove data URL prefix
                        if 'base64,' in image_str:
                            image_str = image_str.split('base64,')[1]
                        
                        image_bytes = base64.b64decode(image_str)
                        img = Image.open(io.BytesIO(image_bytes))
                        images.append(img)
                        print(f"   ✓ Frame {idx + 1}: {img.size}, mode={img.mode}")
                    except Exception as e:
                        print(f"   ❌ Frame {idx + 1} failed: {e}")
                        
            elif 'image' in data:
                print(f"📦 Processing single image...")
                image_data = data['image']
                
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                
                image_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(image_bytes))
                images.append(img)
                print(f"   ✓ Image: {img.size}, mode={img.mode}")
            else:
                return jsonify({'msg': 'No image provided'}), 400
    except Exception as e:
        return jsonify({'msg': 'Invalid image data', 'error': str(e)}), 400
    
    if not images:
        return jsonify({'msg': 'No valid images provided'}), 400
    
    print(f"🖼️  Loaded {len(images)} image(s), starting analysis...")
    
    # Analyze the image(s)
    try:
        if len(images) == 1:
            # Single image analysis
            result = analyze_image_detailed(images[0])
        else:
            # Multi-frame consensus analysis
            result = analyze_image_detailed(images[0])  # First pass
            
            # For multi-frame, we'll analyze all frames and compute consensus
            all_emotions_combined = [result.copy()]
            
            for img in images[1:]:
                frame_result = analyze_image_detailed(img)
                all_emotions_combined.append(frame_result)
            
            # Compute consensus
            result = _compute_consensus(all_emotions_combined)
        
        # Check if analysis was successful
        if result['mood'] is None:
            return jsonify({
                'msg': 'Failed to detect mood',
                'emotion': None,
                'mood': None,
                'raw_emotion': result['raw_emotion'],
                'confidence': result['confidence'],
                'all_emotions': result['all_emotions']
            }), 400
        
        print(f"🎉 Analysis complete, returning mood: {result['mood']}")
        
        return jsonify({
            'emotion': result['mood'],
            'mood': result['mood'],
            'raw_emotion': result['raw_emotion'],
            'confidence': result['confidence'],
            'all_emotions': result['all_emotions'],
            'frames_analyzed': result.get('frames_collected', 1),
            'consistency': result.get('consistency', None)
        }), 200
        
    except Exception as e:
        print(f"❌ Error in mood detection: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'msg': 'Mood detection failed', 'error': str(e)}), 500


def _compute_consensus(results):
    """Compute consensus mood from multiple frame analyses"""
    
    if not results or len(results) == 1:
        # No consensus needed for single frame
        return results[0] if results else {'mood': None, 'raw_emotion': 'error', 'confidence': 0.0, 'all_emotions': {}, 'frames_collected': 0}
    
    print(f"\n{'='*80}")
    print(f"📊 COMPUTING CONSENSUS FROM {len(results)} FRAMES")
    print(f"{'='*80}")
    
    # Count emotion occurrences
    emotion_counts = {}
    emotion_confidences = {}
    
    for result in results:
        mood = result.get('mood')
        confidence = result.get('confidence', 0)
        raw_emotion = result.get('raw_emotion', 'unknown')
        
        if mood:
            emotion_counts[mood] = emotion_counts.get(mood, 0) + 1
            if mood not in emotion_confidences:
                emotion_confidences[mood] = []
            emotion_confidences[mood].append(confidence)
        
        print(f"   Frame: {mood.upper() if mood else 'UNKNOWN'} (raw: {raw_emotion}, confidence: {confidence*100:.1f}%)")
    
    # Find consensus mood (most frequent)
    if emotion_counts:
        consensus_mood = max(emotion_counts, key=emotion_counts.get)
        consistency = emotion_counts[consensus_mood] / len(results)
        avg_confidence = np.mean(emotion_confidences[consensus_mood])
    else:
        consensus_mood = 'calm'
        consistency = 0.0
        avg_confidence = 0.0
    
    print(f"\n✅ CONSENSUS: {consensus_mood.upper()}")
    print(f"   Consistency: {consistency*100:.1f}% ({emotion_counts.get(consensus_mood, 0)}/{len(results)} frames agree)")
    print(f"   Avg Confidence: {avg_confidence*100:.1f}%")
    print(f"{'='*80}\n")
    
    # Merge all emotion scores with weighting
    merged_emotions = {}
    for result in results:
        for emotion, score in result.get('all_emotions', {}).items():
            if emotion not in merged_emotions:
                merged_emotions[emotion] = []
            merged_emotions[emotion].append(score)
    
    # Average all emotion scores
    final_emotions = {
        emotion: float(np.mean(scores))
        for emotion, scores in merged_emotions.items()
    }
    
    return {
        'mood': consensus_mood,
        'raw_emotion': consensus_mood,
        'confidence': float(avg_confidence),
        'all_emotions': final_emotions,
        'frames_collected': len(results),
        'consistency': float(consistency)
    }


@mood_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify mood detection service is running"""
    return jsonify({
        'status': 'Mood detection service is running',
        'model': 'Tanneru/Facial-Emotion-Detection-FER-RAFDB-AffectNet-BEIT-Large',
        'supported_moods': ['happy', 'sad', 'angry', 'calm']
    }), 200