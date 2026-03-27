import { AiFillPlayCircle } from "react-icons/ai"
import { AiFillHeart, AiOutlineHeart } from "react-icons/ai"
import { BsThreeDots } from "react-icons/bs"

export default function MusicCards(props){
    const musicCards = props.musicData.map(music => {
        // 🔧 FIX: Safely extract artist name as STRING
        const getArtistName = () => {
            // Try Deezer format
            if (music.artist?.name) {
                return music.artist.name;
            }
            // Try Spotify format (artists is array of objects)
            if (music.artists?.[0]?.name) {
                return music.artists[0].name;
            }
            return 'Unknown Artist';
        };

        const artistName = getArtistName();

        return (
            <div 
                key={music.id} 
                className='bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-all duration-200 cursor-pointer group'
            >
                {/* Album Cover with Play Button */}
                <div className='relative mb-4' onClick={() => {props.songClick(music.id)}}>
                    <img 
                        src={music.album?.cover_medium || music.album?.images?.[1]?.url || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300"%3E%3Crect fill="%23374151" width="300" height="300"/%3E%3Ctext x="50%25" y="50%25" fill="%239CA3AF" font-size="24" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E'} 
                        className='w-full aspect-square object-cover rounded-lg' 
                        alt={music.title || music.name || 'Music cover'}
                        onError={(e) => {
                            e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300"%3E%3Crect fill="%23374151" width="300" height="300"/%3E%3Ctext x="50%25" y="50%25" fill="%239CA3AF" font-size="24" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                        }}
                    />
                    {/* Play button overlay */}
                    <div className='absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 rounded-lg'>
                        <AiFillPlayCircle className='text-6xl text-white opacity-0 group-hover:opacity-100 transform scale-75 group-hover:scale-100 transition-all duration-200' />
                    </div>
                </div>

                {/* Track Info */}
                <div className='flex flex-col space-y-1'>
                    <h3 className='font-bold text-white text-base truncate' title={music.title || music.name}>
                        {music.title || music.name || 'Unknown Track'}
                    </h3>
                    <p className='text-sm text-gray-400 truncate' title={artistName}>
                        {artistName}
                    </p>
                </div>

                {/* Action Buttons */}
                <div className='flex items-center justify-between mt-3'>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            props.onFavoriteToggle && props.onFavoriteToggle(music);
                        }}
                        className='text-gray-400 hover:text-red-500 transition-colors'
                    >
                        {music.isFavorite ? (
                            <AiFillHeart className='text-xl text-red-500' />
                        ) : (
                            <AiOutlineHeart className='text-xl' />
                        )}
                    </button>
                    <BsThreeDots className='text-gray-400 hover:text-white cursor-pointer' />
                </div>
            </div>
        )
    })

    return(
        <div className='space-y-6 pb-32'>
            {/* Header */}
            <div className='flex items-center justify-between'>
                <h2 className='font-poppins font-bold text-3xl text-white'>
                    Recommended for You
                </h2>
            </div>

            {/* Music Grid - Responsive */}
            <div className='grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4'>
                {musicCards.length > 0 ? musicCards : (
                    <div className='col-span-full text-center text-gray-400 py-12'>
                        <p>No music found. Try a different mood!</p>
                    </div>
                )}
            </div>
        </div>
    )
}