import React, {useState, useEffect} from 'react'

function LoadingText() {
  const [dotCount, setDotCount] = useState(1);

  // TODO: we should cancel the timeout on unmount...
  useEffect(() => {
    let t = setTimeout(() => {
      setDotCount((dotCount+1)%5)
    }, 250)

    return () => {
      clearTimeout(t)
    }
  }, [dotCount])

  return (
    <span className="dbn-loading-text">
      Loading.{".".repeat(dotCount)}
    </span>
  )
}

export default LoadingText
