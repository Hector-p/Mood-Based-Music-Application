import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import '../index.css'
import { CiMenuFries } from 'react-icons/ci'
import Loader from '../components/Loader'
import MusicCards from '../components/MusicCards'
import MusicSearch from '../components/MusicSearch'
import Menu from '../components/Menu'
import SideBar from '../components/SideBar'
import AudioPlayer from '../components/AudioPlayer'
import MoodScanner from '../components/MoodScanner'
import { getCurrentUser } from '../api/auth'
import { searchMusic, getRecommendations, addFavorite, removeFavorite, addToHistory } from '../api/music'
import bellIcon from '../assets/icons/bell-icon.png'
import profileImg from '../assets/icons/profile-img.png'
import arrowDown from '../assets/icons/arrow-down-icon.png'
import searchIcon from '../assets/icons/search-icon.png'

function Home() {
  const audioRef = useRef();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [musicData, setMusicData] = useState([])
  const [initialPage, setInitialPage] = useState(false)
  const [formData, setFormData] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0)
  const [musicSearchData, setMusicSearchData] = useState([])
  const [musicSearched, setMusicSearched] = useState(false)
  const [menu, setMenu] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showMoodScanner, setShowMoodScanner] = useState(false)

  // Check authentication and get user data
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      console.log('Token from localStorage:', token); // Debug log
      
      if (!token) {
        // No token, redirect to login
        navigate('/login');
        return;
      }

      try {
        // Get current user data
        const response = await getCurrentUser(token);
        console.log('getCurrentUser response:', response); // Debug log
        
        if (response.error) {
          // Invalid token, clear and redirect
          console.error('Auth error:', response.message);
          localStorage.removeItem('token');
          navigate('/login');
        } else {
          // Valid token, set user data
          setUser(response);
        }
      } catch (error) {
        console.error('Auth check error:', error);
        localStorage.removeItem('token');
        navigate('/login');
      }
    };

    checkAuth();
  }, [navigate]);

  // Auto-show mood scanner after loader finishes
  useEffect(() => {
    if (initialPage) {
      setShowMoodScanner(true);
    }
  }, [initialPage]);

  // Fetch default music recommendations on load
  useEffect(() => {
    const fetchDefaultMusic = async () => {
      if (!user) return;
      
      setIsLoading(true);
      try {
        // Get recommendations for "happy" mood by default
        const response = await getRecommendations('happy', 25);
        console.log('Backend Music Response:', response);
        
        // FIXED: Handle both response formats {music: [...]} and {tracks: [...]}
        const tracks = response.music || response.tracks || [];
        
        const musicArray = tracks.map(track => ({
          id: track.id,
          album: {
            ...track.album,
            cover_medium: track.album?.images?.[1]?.url || track.album?.images?.[0]?.url || null,
            images: track.album?.images || []
          },
          artist: track.artists?.[0]?.name || track.artists?.[0] || 'Unknown Artist',
          artists: track.artists || ['Unknown Artist'],
          song_url: track.preview_url,
          title: track.name,
          external_url: track.external_url,
          isPlayed: false,
          isDownloaded: false,
          isFavorite: track.is_favorite || false
        }));
        
        console.log('Processed Music Array:', musicArray);
        setMusicData(musicArray);
      } catch (error) {
        console.error('Error fetching music:', error);
        setError(error);
      }
      setIsLoading(false);
    };

    fetchDefaultMusic();
  }, [user]);

  if (isLoading && !user) {
    return <div className='bg-mid-black h-screen w-full flex items-center justify-center'>
      <div className='lds-ellipsis'><div></div><div></div><div></div><div></div></div>
    </div>;
  }

  if (error) {
    return <div className='flex flex-col space-y-2 items-center justify-center bg-mid-black w-full h-screen text-white font-poppins'>
      <span>Something went wrong loading music. Please try again.</span>
      <button className='bg-red text-white py-2 px-5 rounded' onClick={reload}>Reload</button>
    </div>;
  }

  // Search for music using backend
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!formData.trim()) return;
    
    setMusicSearched(true);
    setIsLoading(true);
    
    try {
      const response = await searchMusic(formData, 25);
      console.log('Search Response:', response);
      
      // FIXED: Handle both response formats {music: [...]} and {tracks: [...]}
      const tracks = response.tracks || response.music || [];
      
      const musicArray = tracks.map(track => ({
        id: track.id,
        album: {
          ...track.album,
          cover_medium: track.album?.images?.[1]?.url || track.album?.images?.[0]?.url || null,
          images: track.album?.images || []
        },
        artist: track.artists?.[0]?.name || track.artists?.[0] || 'Unknown Artist',
        artists: track.artists || ['Unknown Artist'],
        song_url: track.preview_url,
        title: track.name,
        external_url: track.external_url,
        isPlayed: false,
        isDownloaded: false,
        isFavorite: track.is_favorite || false
      }));
      
      console.log('Search Results:', musicArray);
      setMusicSearchData(musicArray);
    } catch (error) {
      console.error('Search Error:', error);
      setError(error);
    }
    setIsLoading(false);
  }

  // Handle mood-based recommendations
  const handleMoodSelection = async (mood) => {
    setIsLoading(true);
    setShowMoodScanner(false);
    
    try {
      const response = await getRecommendations(mood, 25);
      console.log('Mood Recommendations:', response);
      
      // FIXED: Handle both response formats {music: [...]} and {tracks: [...]}
      const tracks = response.music || response.tracks || [];
      
      const musicArray = tracks.map(track => ({
        id: track.id,
        album: {
          ...track.album,
          cover_medium: track.album?.images?.[1]?.url || track.album?.images?.[0]?.url || null,
          images: track.album?.images || []
        },
        artist: track.artists?.[0]?.name || track.artists?.[0] || 'Unknown Artist',
        artists: track.artists || ['Unknown Artist'],
        song_url: track.preview_url,
        title: track.name,
        external_url: track.external_url,
        isPlayed: false,
        isDownloaded: false,
        isFavorite: track.is_favorite || false
      }));
      
      setMusicData(musicArray);
      setMusicSearched(false); // Show main view
    } catch (error) {
      console.error('Mood Recommendation Error:', error);
      setError(error);
    }
    setIsLoading(false);
  }

  function handlePlay() {
    audioRef.current.play();
    setIsPlaying(true);
    
    // Add to listening history
    const currentTrack = musicSearched ? musicSearchData[currentTrackIndex] : musicData[currentTrackIndex];
    if (currentTrack) {
      addToHistory(currentTrack).catch(err => console.error('Failed to add to history:', err));
    }
  }

  function handlePause() {
    audioRef.current.pause();
    setIsPlaying(false);
  }

  function songClick(id) {
    let index = musicData.findIndex(music => music.id == id);
    setCurrentTrackIndex(index);
    handlePlay();
  }

  function searchedSongClick(id) {
    let index = musicSearchData.findIndex(music => music.id == id);
    setCurrentTrackIndex(index);
    handlePlay();
  }

  function reload() {
    window.location.reload();
  }

  const handleDownloadClick = (id, src, title) => {
    if (!src) {
      alert('No preview available for this track');
      return;
    }
    
    const link = document.createElement("a");
    link.href = src;
    link.download = title;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Update downloaded state
    if (musicSearched) {
      setMusicSearchData(prevData => prevData.map(data => {
        if (data.id == id) {
          return { ...data, isDownloaded: true }
        } else {
          return { ...data }
        }
      }));
    } else {
      setMusicData(prevData => prevData.map(data => {
        if (data.id == id) {
          return { ...data, isDownloaded: true }
        } else {
          return { ...data }
        }
      }));
    }
  };

  // Handle favorite toggle
  const handleFavoriteToggle = async (track) => {
    try {
      if (track.isFavorite) {
        // Remove from favorites
        await removeFavorite(track.id);
        
        // Update state
        const updateTrack = (data) => data.map(t => 
          t.id === track.id ? { ...t, isFavorite: false } : t
        );
        
        if (musicSearched) {
          setMusicSearchData(updateTrack);
        } else {
          setMusicData(updateTrack);
        }
        
        console.log('Removed from favorites');
      } else {
        // Add to favorites
        await addFavorite(track);
        
        // Update state
        const updateTrack = (data) => data.map(t => 
          t.id === track.id ? { ...t, isFavorite: true } : t
        );
        
        if (musicSearched) {
          setMusicSearchData(updateTrack);
        } else {
          setMusicData(updateTrack);
        }
        
        console.log('Added to favorites');
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      alert('Failed to update favorites');
    }
  };

  function handleMenu() {
    setMenu(prevMenu => !prevMenu);
  }

  function handleLogout() {
    localStorage.removeItem('token');
    navigate('/login');
  }

  // Don't render home content until user is authenticated
  if (!user) {
    return <div className='bg-mid-black h-screen w-full flex items-center justify-center'>
      <div className='lds-ellipsis'><div></div><div></div><div></div><div></div></div>
    </div>;
  }

  return (
    <div className="App bg-mid-black min-h-screen">
      {/* MoodScanner - only shows on home page */}
      <MoodScanner
        isOpen={showMoodScanner}
        onClose={() => setShowMoodScanner(false)}
        onMoodSelect={handleMoodSelection}
      />
      
      {!initialPage ?
        <Loader setInitial={setInitialPage} />
        :
        <div className='flex w-full'>
          <Menu menu={menu} handleLogout={handleLogout} />
          
          {!musicSearched && <div className='px-5 lg:px-2.5 overflow-y-scroll h-screen full sixty-five'>
            <nav className='py-9 flex items-center justify-between'>
              <form className="bg-dark-grey py-3 px-5 flex items-center rounded-md space-x-5 w-3/4 lg:w-2/5" onSubmit={handleSubmit}>
                <img src={searchIcon} alt="" />
                <input
                  type="text"
                  name="name"
                  value={formData}
                  placeholder="Search artists, songs, podcasts..."
                  onChange={(event) => setFormData(event.target.value)}
                  className='border-none bg-dark-grey outline-none w-full text-grey font-poppins placeholder:font-poppins placeholder:text-mid-grey'
                />
              </form>
              <div className='items-center space-x-3 text-grey hidden lg:flex'>
                <img src={bellIcon} alt="" />
                <span>{user.name || 'User'}</span>
                <img src={profileImg} className='w-12 h-12' alt="" />
                <img src={arrowDown} alt="" />
              </div>
              <CiMenuFries className='text-white text-2xl z-20 lg:hidden' onClick={handleMenu} />
            </nav>
            
            {isLoading ? (
              <div className='flex items-center justify-center h-64'>
                <div className='lds-ellipsis'><div></div><div></div><div></div><div></div></div>
              </div>
            ) : (
              <MusicCards
                musicData={musicData}
                songClick={songClick}
                onFavoriteToggle={handleFavoriteToggle}
              />
            )}
          </div>}
          
          {!musicSearched && musicData && musicData.length > 0 && (
            <SideBar 
              musicData={musicData} 
              handleDownloadClick={handleDownloadClick}
              onFavoriteToggle={handleFavoriteToggle}
            />
          )}
          
          {musicSearched &&
            <MusicSearch 
              musicData={musicSearchData} 
              songClick={searchedSongClick} 
              name={formData} 
              handleDownloadClick={handleDownloadClick}
              onFavoriteToggle={handleFavoriteToggle}
              reload={reload}
              isLoading={isLoading}
            />
          }
          
          {!musicSearched && musicData && musicData.length > 0 && (
            <AudioPlayer
              data={musicData}
              isPlaying={isPlaying}
              setIsPlaying={setIsPlaying}
              currentTrackIndex={currentTrackIndex}
              setCurrentTrackIndex={setCurrentTrackIndex}
              handlePlay={handlePlay}
              handlePause={handlePause}
              audioRef={audioRef}
            />
          )}
          
          {musicSearched && musicSearchData && musicSearchData.length > 0 && (
            <AudioPlayer
              data={musicSearchData}
              isPlaying={isPlaying}
              setIsPlaying={setIsPlaying}
              currentTrackIndex={currentTrackIndex}
              setCurrentTrackIndex={setCurrentTrackIndex}
              handlePlay={handlePlay}
              handlePause={handlePause}
              audioRef={audioRef}
            />
          )}
        </div>
      }
    </div>
  )
}

export default Home