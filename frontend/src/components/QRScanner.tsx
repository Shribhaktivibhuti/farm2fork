import { useEffect, useState } from 'react'
import { Html5QrcodeScanner } from 'html5-qrcode'
import { useNavigate } from 'react-router-dom'

export default function QRScanner() {
  const navigate = useNavigate()
  const [, ] = useState('')

  useEffect(() => {
    const scanner = new Html5QrcodeScanner(
      "qr-reader",
      { 
        fps: 10, 
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      },
      false
    )

    scanner.render(
      (decodedText) => {
        console.log('QR Code scanned:', decodedText)
        scanner.clear()
        navigate(`/consumer/verify/${decodedText}`)
      },
      (errorMessage) => {
        // Ignore continuous scanning errors
        if (!errorMessage.includes('NotFoundException')) {
          console.warn('QR scan error:', errorMessage)
        }
      }
    )

    return () => {
      scanner.clear().catch(err => console.error('Scanner cleanup error:', err))
    }
  }, [navigate])

  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">📱</div>
          <h1 className="text-3xl font-bold text-blue-700 mb-2">
            Scan QR Code
          </h1>
          <p className="text-gray-600">Point your camera at the QR code on the product</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div id="qr-reader" className="w-full"></div>
          
          <div className="mt-6 space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">How to scan:</h3>
              <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                <li>Allow camera access when prompted</li>
                <li>Point camera at the QR code</li>
                <li>Hold steady until it scans automatically</li>
                <li>View crop verification details</li>
              </ol>
            </div>
            
            <button
              onClick={() => navigate('/')}
              className="w-full text-gray-600 hover:text-gray-800 py-2"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
