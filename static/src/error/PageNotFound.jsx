import React from 'react'
import { useNavigate } from 'react-router-dom'

const PageNotFound = () => {
  const navigate = useNavigate()

  const handleGoHome = () => {
    navigate('/')
  }
  
  return (
    <div className="flex flex-col space-y-2 items-center justify-center bg-mid-black w-full h-screen text-white font-poppins">
      <span>Error 404!! The page you're looking for might have been moved or deleted.</span>
      <button className="bg-red text-white py-2 px-5 rounded" onClick={handleGoHome}>
        Home
      </button>
    </div>
  )
}

export default PageNotFound