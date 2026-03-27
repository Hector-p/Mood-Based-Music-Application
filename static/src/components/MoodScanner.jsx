import React, { useEffect, useRef, useState } from "react";
import { FaSmile, FaSadTear, FaAngry, FaLeaf } from "react-icons/fa";
import { apiUrl } from "../api/base";

const MoodScanner = ({ isOpen, onClose, onMoodSelect }) => {
  const videoRef = useRef(null);
  const [mood, setMood] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [hasPermission, setHasPermission] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);

  // Define moods with colors and icons
  const moods = [
    { 
      name: "happy", 
      bgColor: "#FCD34D", 
      hoverColor: "#FBBF24", 
      icon: FaSmile, 
      emoji: "😊" 
    },
    { 
      name: "sad", 
      bgColor: "#60A5FA", 
      hoverColor: "#3B82F6", 
      icon: FaSadTear, 
      emoji: "😢" 
    },
    { 
      name: "angry", 
      bgColor: "#F87171", 
      hoverColor: "#EF4444", 
      icon: FaAngry, 
      emoji: "😠" 
    },
    { 
      name: "calm", 
      bgColor: "#34D399", 
      hoverColor: "#10B981", 
      icon: FaLeaf, 
      emoji: "😌" 
    },
  ];

  const requestCamera = async () => {
    try {
      setCameraError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setHasPermission(true);
      }
    } catch (err) {
      console.error("Camera access denied:", err);
      setHasPermission(false);
      
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setCameraError("Camera permission denied. Please allow camera access and try again.");
      } else if (err.name === "NotFoundError") {
        setCameraError("No camera found on this device.");
      } else {
        setCameraError("Unable to access camera. Please check your browser settings.");
      }
    }
  };

  useEffect(() => {
    if (isOpen) {
      requestCamera();
    } else {
      // Clean up camera stream when closing
      if (videoRef.current && videoRef.current.srcObject) {
        let tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
      // Reset states when closing
      setMood(null);
      setScanning(false);
      setCameraError(null);
      setHasPermission(false);
      setDetectionResult(null);
    }
  }, [isOpen]);

  const startScan = async () => {
    setScanning(true);
    
    try {
      const video = videoRef.current;
      
      // Validate video is ready
      if (!video || video.videoWidth === 0 || video.videoHeight === 0) {
        throw new Error('Video stream not ready. Camera may not be initialized.');
      }
      
      // Ensure video is playing
      if (video.paused) {
        console.warn('⚠️ Video is paused, attempting to play...');
        video.play();
        await new Promise(resolve => setTimeout(resolve, 300));
      }
      
      // Capture MULTIPLE FRAMES for better accuracy
      console.log('📸 Capturing 3 frames for better accuracy...');
      const frames = [];
      
      for (let i = 0; i < 3; i++) {
        // Wait between captures to ensure different frames
        await new Promise(resolve => setTimeout(resolve, 150));
        
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        if (canvas.width === 0 || canvas.height === 0) {
          throw new Error('Invalid video dimensions.');
        }
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageData = canvas.toDataURL('image/jpeg', 0.98);
        
        if (!imageData || imageData.length < 500) {
          throw new Error('Captured image is invalid.');
        }
        
        frames.push({
          data: imageData,
          size: imageData.length,
          timestamp: Date.now() + i * 150
        });
        
        console.log(`   Frame ${i + 1}/3: ${(imageData.length / 1024).toFixed(2)}KB captured`);
      }
      
      console.log(`✅ All 3 frames captured, sending to backend for analysis...`);
      
      // Send ALL FRAMES to backend for consensus analysis
      const response = await fetch(apiUrl('/mood/detect'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          images: frames,
          multi_frame: true
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`HTTP ${response.status}: ${errorData.msg || 'Unknown error'}`);
      }
      
      const result = await response.json();
      console.log('🎭 Backend result:', result);
      console.log(`   Analyzed frames: ${result.frames_analyzed}`);
      console.log(`   Consistency: ${result.consistency ? (result.consistency * 100).toFixed(0) + '%' : 'N/A'}`);
      
      if (result.mood && result.mood !== null) {
        setMood(result.mood);
        setDetectionResult(result);
        console.log(`✅ Final mood: ${result.mood} (confidence: ${(result.confidence * 100).toFixed(1)}%)`);
      } else {
        throw new Error('Backend did not return a valid mood. Try again.');
      }
      
    } catch (error) {
      console.error('❌ Mood detection error:', error);
      alert(`Failed to detect mood: ${error.message}\n\nTips:\n- Ensure good lighting\n- Face the camera directly\n- Keep still while capturing`);
    } finally {
      setScanning(false);
    }
  };

  const handleMoodConfirm = () => {
    if (mood && onMoodSelect) {
      console.log('✅ Mood confirmed:', mood);
      
      // Clean up camera before closing
      if (videoRef.current && videoRef.current.srcObject) {
        let tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
      
      // Pass mood to parent component to fetch music
      onMoodSelect(mood);
      
      // Close modal
      onClose();
    }
  };

  const handleManualMoodSelect = (selectedMood) => {
    if (onMoodSelect) {
      console.log('✅ Manual mood selected:', selectedMood);
      
      // Clean up camera before closing
      if (videoRef.current && videoRef.current.srcObject) {
        let tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
      
      // Pass mood to parent component
      onMoodSelect(selectedMood);
      
      // Close modal
      onClose();
    }
  };

  const handleClose = () => {
    // Clean up camera before closing
    if (videoRef.current && videoRef.current.srcObject) {
      let tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    onClose();
  };

  const getMoodData = (moodName) => {
    return moods.find(m => m.name === moodName);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 text-white p-6 rounded-2xl shadow-lg w-full max-w-md flex flex-col items-center">
        <h2 className="text-2xl font-semibold mb-4">How are you feeling?</h2>
        
        {cameraError ? (
          <div className="w-full mb-4">
            <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-4">
              <p className="text-sm">{cameraError}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg mb-4">
              <p className="text-sm text-gray-300 mb-2">To enable camera:</p>
              <ol className="text-xs text-gray-400 list-decimal list-inside space-y-1">
                <li>Click the camera icon in your browser's address bar</li>
                <li>Select "Allow" for camera permission</li>
                <li>Click "Retry Camera Access" below</li>
              </ol>
            </div>
            <button
              onClick={requestCamera}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mb-4"
            >
              Retry Camera Access
            </button>
            
            {/* Manual mood selection as fallback */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-3 text-center">Or select your mood:</p>
              <div className="grid grid-cols-2 gap-3">
                {moods.map((moodOption) => {
                  const Icon = moodOption.icon;
                  return (
                    <button
                      key={moodOption.name}
                      onClick={() => handleManualMoodSelect(moodOption.name)}
                      style={{
                        backgroundColor: moodOption.bgColor,
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = moodOption.hoverColor}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = moodOption.bgColor}
                      className="text-white px-4 py-3 rounded-lg font-semibold capitalize transform hover:scale-105 flex flex-col items-center gap-2"
                    >
                      <Icon className="text-2xl" />
                      <span>{moodOption.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <>
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted
              className="rounded-lg w-full mb-4 border border-gray-700" 
            />
            {mood ? (
              <div className="w-full">
                <div className="bg-gray-800 p-4 rounded-lg mb-4">
                  <p className="text-lg mb-2 text-center">
                    Detected Mood: <span 
                      className="font-bold capitalize inline-block px-3 py-1 rounded-lg text-white"
                      style={{ backgroundColor: getMoodData(mood)?.bgColor }}
                    >
                      {mood}
                    </span>
                  </p>
                  {detectionResult && (
                    <div className="text-sm text-gray-400 text-center mt-2">
                      <p>Emotion: {detectionResult.raw_emotion}</p>
                      <p>Confidence: {(detectionResult.confidence * 100).toFixed(1)}%</p>
                    </div>
                  )}
                </div>
                <button
                  onClick={handleMoodConfirm}
                  className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg mb-2 font-semibold"
                >
                  Get {mood} Music Recommendations
                </button>
                <button
                  onClick={() => {
                    setMood(null);
                    setDetectionResult(null);
                    setScanning(false);
                  }}
                  className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
                >
                  Scan Again
                </button>
              </div>
            ) : (
              <>
                <button
                  onClick={startScan}
                  disabled={scanning || !hasPermission}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:bg-gray-600 disabled:cursor-not-allowed mb-4 font-semibold"
                >
                  {scanning ? "Analyzing your mood..." : "Start Mood Scan"}
                </button>
                
                {/* Manual mood selection option */}
                <div className="w-full">
                  <p className="text-sm text-gray-400 mb-3 text-center">Or select your mood:</p>
                  <div className="grid grid-cols-2 gap-3">
                    {moods.map((moodOption) => {
                      const Icon = moodOption.icon;
                      return (
                        <button
                          key={moodOption.name}
                          onClick={() => handleManualMoodSelect(moodOption.name)}
                          style={{
                            backgroundColor: moodOption.bgColor,
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = moodOption.hoverColor}
                          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = moodOption.bgColor}
                          className="text-white px-4 py-3 rounded-lg font-semibold capitalize transform hover:scale-105 flex flex-col items-center gap-2"
                        >
                          <Icon className="text-2xl" />
                          <span>{moodOption.name}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </>
        )}
        
        <button 
          onClick={handleClose} 
          className="mt-4 text-gray-400 hover:text-white"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default MoodScanner;
