import { useState } from 'react'
import Eyes from "./eyes.jsx"
import TrashTracker from "./TrashTracker.jsx"
import ThankYou from "./ThankYou.jsx"

function App() {
  const [currentPage, setCurrentPage] = useState('eyes')

  const handleNavigation = (page) => {
    setCurrentPage(page)
  }

  if (currentPage === 'eyes') {
    return <Eyes onNavigate={() => handleNavigation('tracker')} />
  } else if (currentPage === 'tracker') {
    return <TrashTracker onNavigate={handleNavigation} />
  } else if (currentPage === 'thankyou') {
    return <ThankYou onNavigate={handleNavigation} />
  }
}

export default App