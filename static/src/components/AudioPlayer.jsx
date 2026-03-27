import { useState, useEffect } from 'react'
import { FaPlay, FaPause, FaVolumeUp, FaVolumeMute, FaRandom } from "react-icons/fa";
import { BsRepeat } from "react-icons/bs"
import { BiSkipNext, BiSkipPrevious } from "react-icons/bi"

export default function AudioPlayer(props){
    const [volume, setVolume] = useState(1)
    const [currentTime, setCurrentTime] = useState(0)
    const [random, setRandom] = useState(false)
    const [isRepeating, setIsRepeating] = useState(false)
    
    // Use props.data directly instead of state
    const track = props.data;
    
    // Get current track safely
    const currentTrack = track?.[props.currentTrackIndex] || {};
    
    // Set audio src when track changes
    useEffect(() => {
        console.log('📀 Track array:', track);
        console.log('📀 Track array length:', track?.length);
        console.log('📀 Current index:', props.currentTrackIndex);
        console.log('📀 Full current track object:', currentTrack);
        console.log('📀 Song URL:', currentTrack?.song);
        
        if (props.audioRef.current) {
            // Try both song_url (Deezer) and song (legacy) properties
            const audioUrl = currentTrack?.song_url || currentTrack?.song || currentTrack?.preview_url;
            if (audioUrl) {
                props.audioRef.current.src = audioUrl;
                console.log('✅ Audio src set to:', audioUrl);
            } else {
                console.warn('⚠️ No song URL found for current track');
                console.log('Track properties:', Object.keys(currentTrack));
            }
        }
    }, [props.currentTrackIndex, track]);

    function playRandom(){
        setRandom(true)
    }

    function pauseRandom(){
        setRandom(false)
    }

    function repeatSong(){
        setIsRepeating(prevState => !prevState)
    }

    function handleNext() {
        props.setIsPlaying(true)
        if(props.currentTrackIndex < track.length - 1 && random == false){
            props.setCurrentTrackIndex(props.currentTrackIndex + 1)
        } else if(props.currentTrackIndex < track.length && random == true){
            props.setCurrentTrackIndex(parseInt(Math.random() * track.length))
        } else {
            props.setCurrentTrackIndex(0)
        }
    }

    function handlePrev() {
        props.setCurrentTrackIndex((prevIndex) =>
            prevIndex === 0 ? track.length - 1 : prevIndex - 1
        );
    }

    const handleVolumeChange = (event) => {
        setVolume(event.target.value);
        if (props.audioRef.current) {
            props.audioRef.current.volume = event.target.value;
        }
    };

    const volumeMute = () => {
        setVolume(0)
        if (props.audioRef.current) {
            props.audioRef.current.volume = 0;
        }
    }

    const handleSeek = (event) => {
        const newTime = parseFloat(event.target.value);
        setCurrentTime(newTime)
        if (props.audioRef.current) {
            props.audioRef.current.currentTime = newTime;
        }
    };

    const handleTimeUpdate = () => {
        if (props.audioRef.current) {
            setCurrentTime(props.audioRef.current.currentTime);
        }
    };

    // 🔧 FIX: Safely extract artist name as a STRING
    const getArtistName = () => {
        // Try Deezer format first
        if (currentTrack?.artist?.name) {
            return currentTrack.artist.name;
        }
        // Try Spotify format (artists is an array of objects)
        if (currentTrack?.artists?.[0]?.name) {
            return currentTrack.artists[0].name;
        }
        // Fallback
        return 'Unknown Artist';
    };

    return(
        <div className="fixed flex items-center justify-between space-x-3 md:border-t-2 md:border-solid border-none md:border-t-mid-grey bg-light-black bottom-0 w-full py-3 px-2 sm:px-4 md:py-5 lg:px-11 z-50">
            <audio
                ref={props.audioRef}
                onEnded={handleNext}
                autoPlay={props.isPlaying}
                volume={volume}
                onTimeUpdate={handleTimeUpdate}
                loop={isRepeating}
                onError={(e) => console.error('❌ Audio error:', e)}
                onLoadedData={() => console.log('✅ Audio loaded')}
            />
            <div className='flex items-center space-x-2'>
                <img 
                    src={currentTrack?.album?.cover_medium || currentTrack?.album?.images?.[1]?.url || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect fill="%23333" width="80" height="80"/%3E%3Ctext x="50%25" y="50%25" fill="%23999" font-size="12" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E'} 
                    className='rounded-lg w-14 h-14 xl:w-20 xl:h-20' 
                    alt={currentTrack?.title || 'Album cover'}
                />
                <div className='flex flex-col text-grey font-lato text-dot whitespace-nowrap overflow-hidden w-16 sm:w-28'>
                    <span className='font-extrabold text-sm xl:text-base'>{currentTrack?.title || currentTrack?.name || 'No track'}</span>
                    <span className='text-xs xl:text-sm font-medium'>{getArtistName()}</span>
                </div>
            </div>
            <div className='space-y-5 flex flex-col items-center'>
                <div className="flex items-center space-x-5 md:space-x-16">
                    <div className='cursor-pointer' onClick={!random ? playRandom : pauseRandom}>
                        <FaRandom className='text-grey text-sm sm:text-lg lg:text-2xl' style={random ? {color: '#A22E20'} : {}}/>
                    </div>
                    <div className='cursor-pointer' onClick={handlePrev}>
                        <BiSkipPrevious className='text-grey text-xl lg:text-5xl' />
                    </div>
                    <div className='cursor-pointer bg-grey rounded-full p-1.5 sm:p-3 lg:p-5'>
                        {props.isPlaying ? 
                            <FaPause className='text-red text-xs' onClick={props.handlePause}/>
                            :
                            <FaPlay className='text-red text-xs' onClick={props.handlePlay}/>
                        }
                    </div>
                    <div className='cursor-pointer' onClick={handleNext}>
                        <BiSkipNext className='text-grey text-xl lg:text-5xl' />
                    </div>
                    <div className='cursor-pointer' onClick={repeatSong}>
                        <BsRepeat className='text-grey text-sm sm:text-lg lg:text-2xl' style={isRepeating ? {color: '#A22E20'} : {}} />
                    </div>
                </div>
                <div className='flex items-center text-grey font-poppins space-x-2'>
                    <div className="hidden md:block current-time">
                        {Math.floor(currentTime / 60)}:{String(Math.floor(currentTime % 60)).padStart(2, '0')}
                    </div>
                    <div className='absolute top-0 right-0 w-full md:relative'>
                        <div className='relative bg-grey rounded seek-slider'>
                            <input 
                                type="range" 
                                min={0}
                                max={props.audioRef.current?.duration || 0}
                                value={currentTime}
                                onChange={handleSeek}
                                className='w-full absolute rounded cursor-grab active:cursor-grabbing'
                            />
                            <div className='absolute top-0 left-0 h-full bg-red' 
                                style={{width: `${(currentTime / (props.audioRef.current?.duration || 1)) * 100}%`}}>
                            </div>
                            <div className='w-3 h-3 bg-red absolute top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full hidden md:block' 
                                style={{left: `${(currentTime / (props.audioRef.current?.duration || 1)) * 100}%`}}>
                            </div>
                        </div>
                    </div>
                    <div className="hidden md:block total-duration">
                        {Math.floor((props.audioRef.current?.duration || 0) / 60)}:{String(Math.floor((props.audioRef.current?.duration || 0) % 60)).padStart(2, '0')}
                    </div>
                </div>
            </div>
            <div className='items-center self-start space-x-2 text-grey cursor-pointer hidden md:flex'>
                {volume > 0 ? <FaVolumeUp onClick={volumeMute} /> : <FaVolumeMute />}
                <div className='relative bg-grey rounded volume-slider'>
                    <input 
                        type="range" 
                        min={0} 
                        max={1} 
                        step={0.1}
                        value={volume}
                        onChange={handleVolumeChange} 
                        className='w-full absolute rounded cursor-grab active:cursor-grabbing' 
                    />
                    <div className='absolute top-0 left-0 h-full bg-red' style={{width: `${volume * 100}%`}}></div>
                    <div className='w-3 h-3 bg-red absolute top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full' style={{left: `${volume * 100}%`}}></div>
                </div>
            </div>
        </div>
    )
}