import React, {useState, useEffect} from 'react'

function LoadingText() {
  const [dotCount, setDotCount] = useState(1);

  // TODO: we should cancel the timeout on unmount...
  useEffect(() => {
    setTimeout(() => {
      setDotCount((dotCount+1)%5)
    }, 250)
  }, [dotCount])

  return (
    <span class="dbn-loading-text">
      Loading.{".".repeat(dotCount)}
    </span>
  )
}

export default LoadingText
