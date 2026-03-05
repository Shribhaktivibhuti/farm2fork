import React from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Select from 'react-select'
import QRScanner from './components/QRScanner'
import cropsData from './data/crops.json'
import { t, LANGUAGES as LANGUAGE_OPTIONS } from './translations'
import { API_URL } from './config'

// Debug log to verify file is loaded
console.log('✅ App.tsx loaded successfully')

function ModeSelection() {
  const navigate = useNavigate()

  return (
    <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 lg:py-16">
      <div className="text-center mb-8 sm:mb-12">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 mb-3 sm:mb-4">
          Welcome to FARM2FORK
        </h2>
        <p className="text-base sm:text-lg text-gray-600">
          Choose your mode to get started
        </p>
      </div>

      {/* Mode Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 max-w-4xl mx-auto">
        {/* Farmer Mode Card */}
        <div 
          onClick={() => navigate('/farmer/login')}
          className="bg-white rounded-xl sm:rounded-2xl shadow-lg sm:shadow-xl p-6 sm:p-8 border-2 border-green-200 hover:border-green-500 hover:shadow-2xl transition-all hover:scale-[1.02] sm:hover:scale-105 cursor-pointer active:scale-[0.98]"
        >
          <div className="text-center">
            <div className="text-5xl sm:text-6xl lg:text-7xl mb-4 sm:mb-6">🚜</div>
            <h3 className="text-2xl sm:text-3xl font-bold text-green-700 mb-3 sm:mb-4">
              Farmer Mode
            </h3>
            <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">
              Upload crop data, get AI safety analysis, and generate QR codes for your produce
            </p>
            <div className="space-y-2 text-left">
              <div className="flex items-center text-xs sm:text-sm text-gray-700">
                <span className="mr-2 flex-shrink-0">✓</span>
                <span>Upload seed packets & crop images</span>
              </div>
              <div className="flex items-center text-xs sm:text-sm text-gray-700">
                <span className="mr-2 flex-shrink-0">✓</span>
                <span>AI-powered safety analysis</span>
              </div>
              <div className="flex items-center text-xs sm:text-sm text-gray-700">
                <span className="mr-2 flex-shrink-0">✓</span>
                <span>Generate verification QR codes</span>
              </div>
            </div>
            <button className="mt-4 sm:mt-6 w-full bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-semibold py-3 sm:py-3.5 px-6 rounded-lg transition-colors min-h-[48px]">
              Get Started
            </button>
          </div>
        </div>

        {/* Consumer Mode Card */}
        <div 
          onClick={() => navigate('/consumer/scan')}
          className="bg-white rounded-xl sm:rounded-2xl shadow-lg sm:shadow-xl p-6 sm:p-8 border-2 border-blue-200 hover:border-blue-500 hover:shadow-2xl transition-all hover:scale-[1.02] sm:hover:scale-105 cursor-pointer active:scale-[0.98]"
        >
          <div className="text-center">
            <div className="text-5xl sm:text-6xl lg:text-7xl mb-4 sm:mb-6">🛒</div>
            <h3 className="text-2xl sm:text-3xl font-bold text-blue-700 mb-3 sm:mb-4">
              Consumer Mode
            </h3>
            <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">
              Scan QR codes to verify crop safety and get personalized consumption advice
            </p>
            <div className="space-y-2 text-left">
              <div className="flex items-center text-xs sm:text-sm text-gray-700">
                <span className="mr-2 flex-shrink-0">✓</span>
                <span>Scan QR codes on products</span>
              </div>
              <div className="flex items-center text-xs sm:text-sm text-gray-700">
                <span className="mr-2 flex-shrink-0">✓</span>
                <span>View safety scores & crop journey</span>
              </div>
              <div className="flex items-center text-xs sm:text-sm text-gray-700">
                <span className="mr-2 flex-shrink-0">✓</span>
                <span>Get AI consumption advice</span>
              </div>
            </div>
            <button className="mt-4 sm:mt-6 w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold py-3 sm:py-3.5 px-6 rounded-lg transition-colors min-h-[48px]">
              Scan QR Code
            </button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="mt-20 text-center">
        <h3 className="text-2xl font-bold text-gray-800 mb-8">
          Powered by AI & AWS
        </h3>
        <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">📸</div>
            <p className="text-sm font-semibold text-gray-700">OCR Extraction</p>
            <p className="text-xs text-gray-500">AWS Textract</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">🔍</div>
            <p className="text-sm font-semibold text-gray-700">Image Analysis</p>
            <p className="text-xs text-gray-500">AWS Rekognition</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">🤖</div>
            <p className="text-sm font-semibold text-gray-700">AI Safety Analysis</p>
            <p className="text-xs text-gray-500">AWS Bedrock</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">🌍</div>
            <p className="text-sm font-semibold text-gray-700">10 Languages</p>
            <p className="text-xs text-gray-500">AWS Translate</p>
          </div>
        </div>
      </div>
    </main>
  )
}

function FarmerLogin() {
  const navigate = useNavigate()
  const [phone, setPhone] = React.useState('')
  const [otp, setOtp] = React.useState('')
  const [name, setName] = React.useState('')
  const [location, setLocation] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState('')
  const [isNewUser, setIsNewUser] = React.useState(false)
  const [selectedLanguage, setSelectedLanguage] = React.useState(() => {
    return localStorage.getItem('app_language') || 'en'
  })
  // Cognito OTP flow states
  const [otpSent, setOtpSent] = React.useState(false)
  const [session, setSession] = React.useState('')
  const [resendTimer, setResendTimer] = React.useState(0)
  const [isDemoMode, setIsDemoMode] = React.useState(false)

  // Save language to localStorage when it changes
  React.useEffect(() => {
    localStorage.setItem('app_language', selectedLanguage)
  }, [selectedLanguage])

  // Resend timer countdown
  React.useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => {
        setResendTimer(resendTimer - 1)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [resendTimer])

  const handleRequestOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/auth/request-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone_number: phone }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to send OTP')
      }

      // Check if demo mode based on message
      const isDemo = data.message && data.message.includes('Demo mode')
      setIsDemoMode(isDemo)
      
      setSession(data.session)
      setOtpSent(true)
      setResendTimer(30)
      setError('')
    } catch (err: any) {
      setError(err.message || 'Failed to send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const requestBody: any = { phone_number: phone, otp, session }
      
      // Include name and location if provided
      if (name.trim()) {
        requestBody.name = name.trim()
      }
      if (location.trim()) {
        requestBody.location = location.trim()
      }

      const response = await fetch(`${API_URL}/api/auth/verify-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      const data = await response.json()

      if (!response.ok) {
        // Check if it's a new user error requiring name
        if (data.details && data.details.field === 'name') {
          setIsNewUser(true)
          setError('Please enter your name to create an account')
          setLoading(false)
          return
        }
        throw new Error(data.message || 'OTP verification failed')
      }

      // Store auth data
      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('farmer_id', data.farmer_id)
      localStorage.setItem('farmer_name', data.farmer_name)

      // Navigate to dashboard
      navigate('/farmer/dashboard')
    } catch (err: any) {
      setError(err.message || 'OTP verification failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleResendOTP = async () => {
    if (resendTimer > 0) return
    
    setError('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/auth/request-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone_number: phone }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to resend OTP')
      }

      setSession(data.session)
      setResendTimer(30)
      setError('')
    } catch (err: any) {
      setError(err.message || 'Failed to resend OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePhone = () => {
    setOtpSent(false)
    setOtp('')
    setSession('')
    setError('')
    setResendTimer(0)
  }

  return (
    <main className="container mx-auto px-4 sm:px-6 py-8 sm:py-12 lg:py-16 min-h-screen">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-lg p-6 sm:p-8">
        {/* Language Selector */}
        <div className="mb-4 sm:mb-6 flex justify-end">
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="appearance-none bg-green-50 border border-green-200 text-green-900 px-3 sm:px-4 py-2 pr-8 rounded-lg text-xs sm:text-sm font-medium focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer"
          >
            {LANGUAGE_OPTIONS.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div className="text-center mb-6 sm:mb-8">
          <div className="text-5xl sm:text-6xl mb-3 sm:mb-4">🚜</div>
          <h1 className="text-2xl sm:text-3xl font-bold text-green-700 mb-2">
            {t('farmer_login', selectedLanguage)}
          </h1>
          <p className="text-sm sm:text-base text-gray-600">
            {otpSent ? 'Enter the OTP sent to your phone' : t('enter_details', selectedLanguage)}
          </p>
        </div>
        
        {!otpSent ? (
          // Step 1: Phone Number Input
          <form onSubmit={handleRequestOTP} className="space-y-4 sm:space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('phone_number', selectedLanguage)}
              </label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="10-digit phone number"
                className="w-full px-4 py-3 text-base sm:text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 min-h-[48px]"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-xs sm:text-sm">
                {error}
              </div>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-h-[48px]"
            >
              {loading ? 'Sending OTP...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          // Step 2: OTP Verification
          <form onSubmit={handleVerifyOTP} className="space-y-4 sm:space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <div className="flex items-center justify-between bg-gray-50 px-3 sm:px-4 py-3 rounded-lg min-h-[48px]">
                <span className="text-sm sm:text-base text-gray-700">{phone}</span>
                <button
                  type="button"
                  onClick={handleChangePhone}
                  className="text-green-600 hover:text-green-700 active:text-green-800 text-xs sm:text-sm font-medium"
                >
                  Change
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OTP Code
              </label>
              {isDemoMode && (
                <div className="mb-2 bg-yellow-50 border border-yellow-200 text-yellow-800 px-3 py-2 rounded-lg text-xs sm:text-sm">
                  <strong>Demo Mode:</strong> Use OTP <strong>0000</strong>
                </div>
              )}
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder={isDemoMode ? "Enter: 0000" : "Enter 6-digit OTP"}
                maxLength={6}
                className="w-full px-4 py-3 text-base sm:text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 min-h-[48px]"
                required
              />
            </div>

            {/* Show name field if new user or if user wants to provide it */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('your_name', selectedLanguage)} {isNewUser && <span className="text-red-500">*</span>}
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your full name"
                className="w-full px-4 py-3 text-base sm:text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 min-h-[48px]"
                required={isNewUser}
              />
              {!isNewUser && (
                <p className="text-xs text-gray-500 mt-1">Required for new users only</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('farm_location', selectedLanguage)}
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., Village, District, State"
                className="w-full px-4 py-3 text-base sm:text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 min-h-[48px]"
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-xs sm:text-sm">
                {error}
              </div>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-h-[48px]"
            >
              {loading ? 'Verifying...' : 'Verify & Login'}
            </button>

            <button
              type="button"
              onClick={handleResendOTP}
              disabled={resendTimer > 0 || loading}
              className="w-full text-green-600 hover:text-green-700 active:text-green-800 font-medium py-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base min-h-[44px]"
            >
              {resendTimer > 0 ? `Resend OTP in ${resendTimer}s` : 'Resend OTP'}
            </button>
          </form>
        )}
        
        <p className="text-xs sm:text-sm text-gray-500 mt-4 text-center">
          {otpSent 
            ? (isDemoMode ? 'Demo Mode: Use OTP 0000 to login' : 'Check your phone for the OTP code')
            : 'You will receive an OTP via SMS'}
        </p>
        
        <button
          onClick={() => navigate('/')}
          className="mt-4 sm:mt-6 w-full text-gray-600 hover:text-gray-800 active:text-gray-900 text-xs sm:text-sm min-h-[44px]"
        >
          {t('back_to_home', selectedLanguage)}
        </button>
      </div>
    </main>
  )
}

// ConsumerScan component removed - using QRScanner component instead

interface VerificationData {
  success: boolean
  crop_name: string
  crop_variety: string | null
  farming_method: string
  harvest_date: string
  farmer_name: string
  batch_id: string
  qr_id: string
  farmer_location?: string
  farmer_profile_photo?: string
  field_photo?: string
  safety_analysis?: {
    safety_score: number
    risk_level: string
    explanation: string
  } | null
  cleaning_instructions?: string | null
}

function ConsumerVerify() {
  const navigate = useNavigate()
  const { qrId } = useParams<{ qrId: string }>()
  const [loading, setLoading] = React.useState(true)
  const [data, setData] = React.useState<VerificationData | null>(null)
  const [error, setError] = React.useState('')
  const [selectedLanguage, setSelectedLanguage] = React.useState(() => {
    return localStorage.getItem('app_language') || 'en'
  })

  // Save language to localStorage when it changes
  React.useEffect(() => {
    localStorage.setItem('app_language', selectedLanguage)
  }, [selectedLanguage])

  React.useEffect(() => {
    if (qrId) {
      fetchVerificationData(qrId, selectedLanguage)
    }
  }, [qrId, selectedLanguage])

  const fetchVerificationData = async (id: string, language: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/public/verify/${id}?language=${language}`)
      
      if (!response.ok) {
        throw new Error('QR code not found')
      }
      
      const result = await response.json()
      setData(result)
    } catch (err: any) {
      setError(err.message || 'Failed to verify QR code')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <div className="text-6xl mb-4">⏳</div>
          <p className="text-lg text-gray-600">Verifying product...</p>
        </div>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">❌</div>
            <h1 className="text-2xl font-bold text-red-700 mb-4">Verification Failed</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => navigate('/consumer/scan')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Language Selector */}
          <div className="mb-6 flex justify-end">
            <div className="relative inline-block">
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="appearance-none bg-blue-50 border border-blue-200 text-blue-900 px-4 py-2 pr-8 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {LANGUAGE_OPTIONS.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.flag} {lang.name}
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-blue-900">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                </svg>
              </div>
            </div>
          </div>

          <div className="text-center mb-8">
            <div className="text-6xl mb-4">✅</div>
            <h1 className="text-3xl font-bold text-green-700 mb-2">
              {selectedLanguage === 'en' ? 'Product Verified!' : 
               selectedLanguage === 'hi' ? 'उत्पाद सत्यापित!' :
               selectedLanguage === 'ta' ? 'தயாரிப்பு சரிபார்க்கப்பட்டது!' :
               selectedLanguage === 'te' ? 'ఉత్పత్తి ధృవీకరించబడింది!' :
               selectedLanguage === 'kn' ? 'ಉತ್ಪನ್ನ ಪರಿಶೀಲಿಸಲಾಗಿದೆ!' :
               selectedLanguage === 'ml' ? 'ഉൽപ്പന്നം പരിശോധിച്ചു!' :
               selectedLanguage === 'bn' ? 'পণ্য যাচাই করা হয়েছে!' :
               selectedLanguage === 'mr' ? 'उत्पादन सत्यापित!' :
               selectedLanguage === 'gu' ? 'ઉત્પાદન ચકાસાયું!' :
               selectedLanguage === 'pa' ? 'ਉਤਪਾਦ ਪ੍ਰਮਾਣਿਤ!' :
               'Product Verified!'}
            </h1>
            <p className="text-gray-600">
              {selectedLanguage === 'en' ? 'This product has been authenticated' :
               selectedLanguage === 'hi' ? 'यह उत्पाद प्रमाणित किया गया है' :
               selectedLanguage === 'ta' ? 'இந்த தயாரிப்பு அங்கீகரிக்கப்பட்டுள்ளது' :
               selectedLanguage === 'te' ? 'ఈ ఉత్పత్తి ప్రామాణీకరించబడింది' :
               selectedLanguage === 'kn' ? 'ಈ ಉತ್ಪನ್ನವನ್ನು ದೃಢೀಕರಿಸಲಾಗಿದೆ' :
               selectedLanguage === 'ml' ? 'ഈ ഉൽപ്പന്നം പ്രാമാണീകരിച്ചു' :
               selectedLanguage === 'bn' ? 'এই পণ্যটি প্রমাণীকৃত হয়েছে' :
               selectedLanguage === 'mr' ? 'हे उत्पादन प्रमाणित केले गेले आहे' :
               selectedLanguage === 'gu' ? 'આ ઉત્પાદન પ્રમાણિત કરવામાં આવ્યું છે' :
               selectedLanguage === 'pa' ? 'ਇਹ ਉਤਪਾਦ ਪ੍ਰਮਾਣਿਤ ਕੀਤਾ ਗਿਆ ਹੈ' :
               'This product has been authenticated'}
            </p>
          </div>

          <div className="space-y-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h2 className="text-xl font-bold text-green-900 mb-4">
                {selectedLanguage === 'en' ? 'Crop Information' :
                 selectedLanguage === 'hi' ? 'फसल की जानकारी' :
                 selectedLanguage === 'ta' ? 'பயிர் தகவல்' :
                 selectedLanguage === 'te' ? 'పంట సమాచారం' :
                 selectedLanguage === 'kn' ? 'ಬೆಳೆ ಮಾಹಿತಿ' :
                 selectedLanguage === 'ml' ? 'വിള വിവരങ്ങൾ' :
                 selectedLanguage === 'bn' ? 'ফসলের তথ্য' :
                 selectedLanguage === 'mr' ? 'पीक माहिती' :
                 selectedLanguage === 'gu' ? 'પાક માહિતી' :
                 selectedLanguage === 'pa' ? 'ਫਸਲ ਜਾਣਕਾਰੀ' :
                 'Crop Information'}
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-700 font-medium">
                    {selectedLanguage === 'en' ? 'Crop:' :
                     selectedLanguage === 'hi' ? 'फसल:' :
                     selectedLanguage === 'ta' ? 'பயிர்:' :
                     selectedLanguage === 'te' ? 'పంట:' :
                     selectedLanguage === 'kn' ? 'ಬೆಳೆ:' :
                     selectedLanguage === 'ml' ? 'വിള:' :
                     selectedLanguage === 'bn' ? 'ফসল:' :
                     selectedLanguage === 'mr' ? 'पीक:' :
                     selectedLanguage === 'gu' ? 'પાક:' :
                     selectedLanguage === 'pa' ? 'ਫਸਲ:' :
                     'Crop:'}
                  </span>
                  <span className="text-gray-900 font-semibold">
                    {data.crop_name}
                    {data.crop_variety && ` - ${data.crop_variety}`}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700 font-medium">
                    {selectedLanguage === 'en' ? 'Farming Method:' :
                     selectedLanguage === 'hi' ? 'खेती की विधि:' :
                     selectedLanguage === 'ta' ? 'விவசாய முறை:' :
                     selectedLanguage === 'te' ? 'వ్యవసాయ పద్ధతి:' :
                     selectedLanguage === 'kn' ? 'ಕೃಷಿ ವಿಧಾನ:' :
                     selectedLanguage === 'ml' ? 'കൃഷി രീതി:' :
                     selectedLanguage === 'bn' ? 'চাষ পদ্ধতি:' :
                     selectedLanguage === 'mr' ? 'शेती पद्धत:' :
                     selectedLanguage === 'gu' ? 'ખેતી પદ્ધતિ:' :
                     selectedLanguage === 'pa' ? 'ਖੇਤੀ ਵਿਧੀ:' :
                     'Farming Method:'}
                  </span>
                  <span className="text-gray-900 font-semibold capitalize">{data.farming_method}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700 font-medium">
                    {selectedLanguage === 'en' ? 'Harvest Date:' :
                     selectedLanguage === 'hi' ? 'कटाई की तारीख:' :
                     selectedLanguage === 'ta' ? 'அறுவடை தேதி:' :
                     selectedLanguage === 'te' ? 'పంట తేదీ:' :
                     selectedLanguage === 'kn' ? 'ಕೊಯ್ಲು ದಿನಾಂಕ:' :
                     selectedLanguage === 'ml' ? 'വിളവെടുപ്പ് തീയതി:' :
                     selectedLanguage === 'bn' ? 'ফসল কাটার তারিখ:' :
                     selectedLanguage === 'mr' ? 'कापणी तारीख:' :
                     selectedLanguage === 'gu' ? 'લણણી તારીખ:' :
                     selectedLanguage === 'pa' ? 'ਵਾਢੀ ਦੀ ਤਾਰੀਖ:' :
                     'Harvest Date:'}
                  </span>
                  <span className="text-gray-900 font-semibold">{data.harvest_date}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700 font-medium">
                    {selectedLanguage === 'en' ? 'Farmer:' :
                     selectedLanguage === 'hi' ? 'किसान:' :
                     selectedLanguage === 'ta' ? 'விவசாயி:' :
                     selectedLanguage === 'te' ? 'రైతు:' :
                     selectedLanguage === 'kn' ? 'ರೈತ:' :
                     selectedLanguage === 'ml' ? 'കർഷകൻ:' :
                     selectedLanguage === 'bn' ? 'কৃষক:' :
                     selectedLanguage === 'mr' ? 'शेतकरी:' :
                     selectedLanguage === 'gu' ? 'ખેડૂત:' :
                     selectedLanguage === 'pa' ? 'ਕਿਸਾਨ:' :
                     'Farmer:'}
                  </span>
                  <span className="text-gray-900 font-semibold">{data.farmer_name}</span>
                </div>
              </div>
            </div>

            {/* Farmer Info Card */}
            {(data.farmer_profile_photo || data.farmer_location) && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h2 className="text-xl font-bold text-purple-900 mb-4">👨‍🌾 Farmer Information</h2>
                <div className="flex items-center space-x-4">
                  {data.farmer_profile_photo ? (
                    <img
                      src={data.farmer_profile_photo}
                      alt={data.farmer_name}
                      className="w-20 h-20 rounded-full object-cover border-4 border-purple-200"
                    />
                  ) : (
                    <div className="w-20 h-20 rounded-full bg-purple-100 flex items-center justify-center border-4 border-purple-200">
                      <span className="text-3xl">👤</span>
                    </div>
                  )}
                  <div>
                    <p className="text-lg font-semibold text-gray-900">{data.farmer_name}</p>
                    {data.farmer_location && (
                      <p className="text-gray-700 flex items-center mt-1">
                        <span className="mr-1">📍</span>
                        {data.farmer_location}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Field Photo Section */}
            {data.field_photo && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h2 className="text-xl font-bold text-blue-900 mb-4">🌾 Farm Field</h2>
                <img
                  src={data.field_photo}
                  alt="Farm field"
                  className="w-full rounded-lg object-cover max-h-96"
                />
                <p className="text-sm text-gray-600 mt-2 text-center">Photo of the farm where this crop was grown</p>
              </div>
            )}

            {/* Safety Analysis Section */}
            {data.safety_analysis && (
              <div className={`border rounded-lg p-6 ${
                data.safety_analysis.safety_score >= 71 ? 'bg-green-50 border-green-200' :
                data.safety_analysis.safety_score >= 41 ? 'bg-yellow-50 border-yellow-200' :
                'bg-red-50 border-red-200'
              }`}>
                <h2 className="text-xl font-bold mb-4" style={{
                  color: data.safety_analysis.safety_score >= 71 ? '#065f46' :
                         data.safety_analysis.safety_score >= 41 ? '#92400e' : '#991b1b'
                }}>
                  {selectedLanguage === 'en' ? '🛡️ Safety Analysis' :
                   selectedLanguage === 'hi' ? '🛡️ सुरक्षा विश्लेषण' :
                   selectedLanguage === 'ta' ? '🛡️ பாதுகாப்பு பகுப்பாய்வு' :
                   selectedLanguage === 'te' ? '🛡️ భద్రతా విశ్లేషణ' :
                   selectedLanguage === 'kn' ? '🛡️ ಸುರಕ್ಷತಾ ವಿಶ್ಲೇಷಣೆ' :
                   selectedLanguage === 'ml' ? '🛡️ സുരക്ഷാ വിശകലനം' :
                   selectedLanguage === 'bn' ? '🛡️ নিরাপত্তা বিশ্লেষণ' :
                   selectedLanguage === 'mr' ? '🛡️ सुरक्षा विश्लेषण' :
                   selectedLanguage === 'gu' ? '🛡️ સુરક્ષા વિશ્લેષણ' :
                   selectedLanguage === 'pa' ? '🛡️ ਸੁਰੱਖਿਆ ਵਿਸ਼ਲੇਸ਼ਣ' :
                   '🛡️ Safety Analysis'}
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700 font-medium">
                      {selectedLanguage === 'en' ? 'Safety Score:' :
                       selectedLanguage === 'hi' ? 'सुरक्षा स्कोर:' :
                       selectedLanguage === 'ta' ? 'பாதுகாப்பு மதிப்பெண்:' :
                       selectedLanguage === 'te' ? 'భద్రతా స్కోర్:' :
                       selectedLanguage === 'kn' ? 'ಸುರಕ್ಷತಾ ಸ್ಕೋರ್:' :
                       selectedLanguage === 'ml' ? 'സുരക്ഷാ സ്കോർ:' :
                       selectedLanguage === 'bn' ? 'নিরাপত্তা স্কোর:' :
                       selectedLanguage === 'mr' ? 'सुरक्षा स्कोअर:' :
                       selectedLanguage === 'gu' ? 'સુરક્ષા સ્કોર:' :
                       selectedLanguage === 'pa' ? 'ਸੁਰੱਖਿਆ ਸਕੋਰ:' :
                       'Safety Score:'}
                    </span>
                    <span className={`text-3xl font-bold ${
                      data.safety_analysis.safety_score >= 71 ? 'text-green-600' :
                      data.safety_analysis.safety_score >= 41 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {data.safety_analysis.safety_score}/100
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700 font-medium">
                      {selectedLanguage === 'en' ? 'Risk Level:' :
                       selectedLanguage === 'hi' ? 'जोखिम स्तर:' :
                       selectedLanguage === 'ta' ? 'ஆபத்து நிலை:' :
                       selectedLanguage === 'te' ? 'ప్రమాద స్థాయి:' :
                       selectedLanguage === 'kn' ? 'ಅಪಾಯ ಮಟ್ಟ:' :
                       selectedLanguage === 'ml' ? 'അപകട നില:' :
                       selectedLanguage === 'bn' ? 'ঝুঁকির স্তর:' :
                       selectedLanguage === 'mr' ? 'धोका पातळी:' :
                       selectedLanguage === 'gu' ? 'જોખમ સ્તર:' :
                       selectedLanguage === 'pa' ? 'ਖਤਰੇ ਦਾ ਪੱਧਰ:' :
                       'Risk Level:'}
                    </span>
                    <span className={`text-xl font-bold ${
                      data.safety_analysis.safety_score >= 71 ? 'text-green-600' :
                      data.safety_analysis.safety_score >= 41 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {data.safety_analysis.risk_level}
                    </span>
                  </div>
                  <div className="pt-4 border-t">
                    <p className="text-sm text-gray-700">{data.safety_analysis.explanation}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Cleaning Instructions Section */}
            {data.cleaning_instructions && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h2 className="text-xl font-bold text-purple-900 mb-4">
                  {selectedLanguage === 'en' ? '🧼 How to Clean & Prepare' :
                   selectedLanguage === 'hi' ? '🧼 कैसे साफ करें और तैयार करें' :
                   selectedLanguage === 'ta' ? '🧼 எப்படி சுத்தம் செய்வது மற்றும் தயார் செய்வது' :
                   selectedLanguage === 'te' ? '🧼 ఎలా శుభ్రం చేయాలి మరియు సిద్ధం చేయాలి' :
                   selectedLanguage === 'kn' ? '🧼 ಹೇಗೆ ಸ್ವಚ್ಛಗೊಳಿಸುವುದು ಮತ್ತು ತಯಾರಿಸುವುದು' :
                   selectedLanguage === 'ml' ? '🧼 എങ്ങനെ വൃത്തിയാക്കാം, തയ്യാറാക്കാം' :
                   selectedLanguage === 'bn' ? '🧼 কীভাবে পরিষ্কার এবং প্রস্তুত করবেন' :
                   selectedLanguage === 'mr' ? '🧼 कसे स्वच्छ आणि तयार करावे' :
                   selectedLanguage === 'gu' ? '🧼 કેવી રીતે સાફ અને તૈયાર કરવું' :
                   selectedLanguage === 'pa' ? '🧼 ਕਿਵੇਂ ਸਾਫ਼ ਅਤੇ ਤਿਆਰ ਕਰੀਏ' :
                   '🧼 How to Clean & Prepare'}
                </h2>
                <p className="text-sm text-purple-800 leading-relaxed">
                  {data.cleaning_instructions}
                </p>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h2 className="text-xl font-bold text-blue-900 mb-4">
                {selectedLanguage === 'en' ? 'Verification Details' :
                 selectedLanguage === 'hi' ? 'सत्यापन विवरण' :
                 selectedLanguage === 'ta' ? 'சரிபார்ப்பு விவரங்கள்' :
                 selectedLanguage === 'te' ? 'ధృవీకరణ వివరాలు' :
                 selectedLanguage === 'kn' ? 'ಪರಿಶೀಲನೆ ವಿವರಗಳು' :
                 selectedLanguage === 'ml' ? 'പരിശോധന വിശദാംശങ്ങൾ' :
                 selectedLanguage === 'bn' ? 'যাচাইকরণ বিবরণ' :
                 selectedLanguage === 'mr' ? 'सत्यापन तपशील' :
                 selectedLanguage === 'gu' ? 'ચકાસણી વિગતો' :
                 selectedLanguage === 'pa' ? 'ਪ੍ਰਮਾਣਿਕਤਾ ਵੇਰਵੇ' :
                 'Verification Details'}
              </h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-700">QR Code ID:</span>
                  <span className="text-gray-900 font-mono">{data.qr_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Batch ID:</span>
                  <span className="text-gray-900 font-mono text-xs">{data.batch_id}</span>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <span className="font-semibold">
                  {selectedLanguage === 'en' ? 'Note:' :
                   selectedLanguage === 'hi' ? 'नोट:' :
                   selectedLanguage === 'ta' ? 'குறிப்பு:' :
                   selectedLanguage === 'te' ? 'గమనిక:' :
                   selectedLanguage === 'kn' ? 'ಸೂಚನೆ:' :
                   selectedLanguage === 'ml' ? 'കുറിപ്പ്:' :
                   selectedLanguage === 'bn' ? 'নোট:' :
                   selectedLanguage === 'mr' ? 'टीप:' :
                   selectedLanguage === 'gu' ? 'નોંધ:' :
                   selectedLanguage === 'pa' ? 'ਨੋਟ:' :
                   'Note:'}
                </span>{' '}
                {selectedLanguage === 'en' ? 'This verification confirms the product\'s authenticity and traceability. For detailed safety analysis and consumption advice, AI features will be available in the full version.' :
                 selectedLanguage === 'hi' ? 'यह सत्यापन उत्पाद की प्रामाणिकता और ट्रेसेबिलिटी की पुष्टि करता है। विस्तृत सुरक्षा विश्लेषण और उपभोग सलाह के लिए, एआई सुविधाएं पूर्ण संस्करण में उपलब्ध होंगी।' :
                 selectedLanguage === 'ta' ? 'இந்த சரிபார்ப்பு தயாரிப்பின் நம்பகத்தன்மை மற்றும் கண்காணிப்பை உறுதிப்படுத்துகிறது। விரிவான பாதுகாப்பு பகுப்பாய்வு மற்றும் நுகர்வு ஆலோசனைக்கு, AI அம்சங்கள் முழு பதிப்பில் கிடைக்கும்.' :
                 selectedLanguage === 'te' ? 'ఈ ధృవీకరణ ఉత్పత్తి యొక్క ప్రామాణికత మరియు ట్రేసబిలిటీని నిర్ధారిస్తుంది। వివరణాత్మక భద్రతా విశ్లేషణ మరియు వినియోగ సలహా కోసం, AI ఫీచర్లు పూర్తి వెర్షన్‌లో అందుబాటులో ఉంటాయి।' :
                 selectedLanguage === 'kn' ? 'ಈ ಪರಿಶೀಲನೆಯು ಉತ್ಪನ್ನದ ಅಧಿಕೃತತೆ ಮತ್ತು ಟ್ರೇಸಬಿಲಿಟಿಯನ್ನು ದೃಢೀಕರಿಸುತ್ತದೆ. ವಿವರವಾದ ಸುರಕ್ಷತಾ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ಬಳಕೆ ಸಲಹೆಗಾಗಿ, AI ವೈಶಿಷ್ಟ್ಯಗಳು ಪೂರ್ಣ ಆವೃತ್ತಿಯಲ್ಲಿ ಲಭ್ಯವಿರುತ್ತವೆ।' :
                 selectedLanguage === 'ml' ? 'ഈ പരിശോധന ഉൽപ്പന്നത്തിന്റെ ആധികാരികതയും ട്രേസബിലിറ്റിയും സ്ഥിരീകരിക്കുന്നു. വിശദമായ സുരക്ഷാ വിശകലനത്തിനും ഉപഭോഗ ഉപദേശത്തിനും, AI സവിശേഷതകൾ പൂർണ്ണ പതിപ്പിൽ ലഭ്യമാകും।' :
                 selectedLanguage === 'bn' ? 'এই যাচাইকরণ পণ্যের সত্যতা এবং ট্রেসেবিলিটি নিশ্চিত করে। বিস্তারিত নিরাপত্তা বিশ্লেষণ এবং ভোগ পরামর্শের জন্য, AI বৈশিষ্ট্যগুলি সম্পূর্ণ সংস্করণে উপলব্ধ হবে।' :
                 selectedLanguage === 'mr' ? 'हे सत्यापन उत्पादनाची सत्यता आणि ट्रेसेबिलिटी पुष्टी करते. तपशीलवार सुरक्षा विश्लेषण आणि उपभोग सल्ल्यासाठी, AI वैशिष्ट्ये पूर्ण आवृत्तीमध्ये उपलब्ध असतील।' :
                 selectedLanguage === 'gu' ? 'આ ચકાસણી ઉત્પાદનની અધિકૃતતા અને ટ્રેસેબિલિટીની પુષ્ટિ કરે છે. વિગતવાર સુરક્ષા વિશ્લેષણ અને વપરાશ સલાહ માટે, AI સુવિધાઓ સંપૂર્ણ સંસ્કરણમાં ઉપલબ્ધ હશે।' :
                 selectedLanguage === 'pa' ? 'ਇਹ ਪ੍ਰਮਾਣਿਕਤਾ ਉਤਪਾਦ ਦੀ ਪ੍ਰਮਾਣਿਕਤਾ ਅਤੇ ਟਰੇਸੇਬਿਲਿਟੀ ਦੀ ਪੁਸ਼ਟੀ ਕਰਦੀ ਹੈ। ਵਿਸਤ੍ਰਿਤ ਸੁਰੱਖਿਆ ਵਿਸ਼ਲੇਸ਼ਣ ਅਤੇ ਖਪਤ ਸਲਾਹ ਲਈ, AI ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ ਪੂਰੇ ਸੰਸਕਰਣ ਵਿੱਚ ਉਪਲਬਧ ਹੋਣਗੀਆਂ।' :
                 'This verification confirms the product\'s authenticity and traceability. For detailed safety analysis and consumption advice, AI features will be available in the full version.'}
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => navigate('/consumer/scan')}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                {selectedLanguage === 'en' ? 'Verify Another' :
                 selectedLanguage === 'hi' ? 'दूसरा सत्यापित करें' :
                 selectedLanguage === 'ta' ? 'மற்றொன்றை சரிபார்க்கவும்' :
                 selectedLanguage === 'te' ? 'మరొకటి ధృవీకరించండి' :
                 selectedLanguage === 'kn' ? 'ಇನ್ನೊಂದನ್ನು ಪರಿಶೀಲಿಸಿ' :
                 selectedLanguage === 'ml' ? 'മറ്റൊന്ന് പരിശോധിക്കുക' :
                 selectedLanguage === 'bn' ? 'অন্যটি যাচাই করুন' :
                 selectedLanguage === 'mr' ? 'दुसरे सत्यापित करा' :
                 selectedLanguage === 'gu' ? 'બીજું ચકાસો' :
                 selectedLanguage === 'pa' ? 'ਦੂਜਾ ਪ੍ਰਮਾਣਿਤ ਕਰੋ' :
                 'Verify Another'}
              </button>
              <button
                onClick={() => navigate('/')}
                className="flex-1 border border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {selectedLanguage === 'en' ? 'Back to Home' :
                 selectedLanguage === 'hi' ? 'होम पर वापस जाएं' :
                 selectedLanguage === 'ta' ? 'முகப்புக்குத் திரும்பு' :
                 selectedLanguage === 'te' ? 'హోమ్‌కు తిరిగి వెళ్ళండి' :
                 selectedLanguage === 'kn' ? 'ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ' :
                 selectedLanguage === 'ml' ? 'ഹോമിലേക്ക് മടങ്ങുക' :
                 selectedLanguage === 'bn' ? 'হোমে ফিরে যান' :
                 selectedLanguage === 'mr' ? 'मुख्यपृष्ठावर परत या' :
                 selectedLanguage === 'gu' ? 'હોમ પર પાછા જાઓ' :
                 selectedLanguage === 'pa' ? 'ਘਰ ਵਾਪਸ ਜਾਓ' :
                 'Back to Home'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

interface Batch {
  id: string
  crop_name: string
  crop_variety: string | null
  farming_method: string
  harvest_date: string
  has_qr: boolean
  qr_id: string | null
}

function FarmerDashboard() {
  const navigate = useNavigate()
  const [farmerName, setFarmerName] = React.useState('')
  const [batches, setBatches] = React.useState<Batch[]>([])
  const [loading, setLoading] = React.useState(true)
  const [generatingQR, setGeneratingQR] = React.useState<string | null>(null)
  const [qrImage, setQrImage] = React.useState<{batchId: string, data: string, qrId: string} | null>(null)
  const [selectedLanguage, setSelectedLanguage] = React.useState(() => {
    return localStorage.getItem('app_language') || 'en'
  })
  
  // Profile management states
  const [activeTab, setActiveTab] = React.useState<'batches' | 'profile'>('batches')
  const [profileData, setProfileData] = React.useState<any>(null)
  const [editingProfile, setEditingProfile] = React.useState(false)
  const [uploadingPhoto, setUploadingPhoto] = React.useState(false)
  const [photoPreview, setPhotoPreview] = React.useState<string | null>(null)
  const [profileName, setProfileName] = React.useState('')
  const [profileLocation, setProfileLocation] = React.useState('')

  // Save language to localStorage when it changes
  React.useEffect(() => {
    localStorage.setItem('app_language', selectedLanguage)
  }, [selectedLanguage])

  React.useEffect(() => {
    const token = localStorage.getItem('auth_token')
    const name = localStorage.getItem('farmer_name')
    
    if (!token) {
      navigate('/farmer/login')
      return
    }
    
    setFarmerName(name || 'Farmer')
    fetchBatches()
    fetchProfile()
  }, [navigate])

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`${API_URL}/api/farmer/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to fetch profile')
      
      const data = await response.json()
      console.log('📸 Profile data received:', data)
      console.log('📸 Profile photo URL:', data.profile_photo_url)
      setProfileData(data)
      setProfileName(data.name || '')
      setProfileLocation(data.location || '')
    } catch (error) {
      console.error('Error fetching profile:', error)
    }
  }

  const fetchBatches = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`${API_URL}/api/farmer/batches`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to fetch batches')
      
      const data = await response.json()
      setBatches(data.batches)
    } catch (error) {
      console.error('Error fetching batches:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProfilePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB')
      return
    }
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file')
      return
    }

    setUploadingPhoto(true)
    
    try {
      // Create preview
      const previewUrl = URL.createObjectURL(file)
      setPhotoPreview(previewUrl)

      // Upload to S3
      const token = localStorage.getItem('auth_token')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', 'profile_photo')

      const uploadResponse = await fetch(`${API_URL}/api/upload/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (!uploadResponse.ok) throw new Error('Failed to upload photo')

      const uploadData = await uploadResponse.json()
      const photoUrl = uploadData.s3_url

      // Update profile with new photo URL
      const profileResponse = await fetch(`${API_URL}/api/farmer/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          profile_photo_url: photoUrl,
        }),
      })

      if (!profileResponse.ok) throw new Error('Failed to update profile')

      // Refresh profile data
      await fetchProfile()
      URL.revokeObjectURL(previewUrl)
      setPhotoPreview(null)
      
      // Force a page reload to clear any cached images
      window.location.reload()
    } catch (error) {
      console.error('Error uploading photo:', error)
      alert('Failed to upload photo')
    } finally {
      setUploadingPhoto(false)
    }
  }

  const handleProfileUpdate = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`${API_URL}/api/farmer/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: profileName,
          location: profileLocation,
        }),
      })

      if (!response.ok) throw new Error('Failed to update profile')

      await fetchProfile()
      setEditingProfile(false)
      localStorage.setItem('farmer_name', profileName)
      setFarmerName(profileName)
      alert('Profile updated successfully!')
    } catch (error) {
      console.error('Error updating profile:', error)
      alert('Failed to update profile')
    }
  }

  const handleGenerateQR = async (batchId: string) => {
    setGeneratingQR(batchId)
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`${API_URL}/api/qr/generate?batch_id=${batchId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to generate QR')
      
      const data = await response.json()
      setQrImage({
        batchId,
        data: data.qr_code_data,
        qrId: data.qr_id
      })
      
      // Refresh batches to update QR status
      fetchBatches()
    } catch (error) {
      console.error('Error generating QR:', error)
      alert('Failed to generate QR code')
    } finally {
      setGeneratingQR(null)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('farmer_id')
    localStorage.removeItem('farmer_name')
    navigate('/')
  }

  const totalBatches = batches.length
  const qrCount = batches.filter(b => b.has_qr).length

  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          {/* Language Selector */}
          <div className="mb-4 flex justify-end">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="appearance-none bg-green-50 border border-green-200 text-green-900 px-4 py-2 pr-8 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer"
            >
              {LANGUAGE_OPTIONS.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.flag} {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-green-700 mb-2">
                {selectedLanguage === 'en' ? `Welcome, ${farmerName}!` :
                 selectedLanguage === 'hi' ? `स्वागत है, ${farmerName}!` :
                 selectedLanguage === 'ta' ? `வரவேற்கிறோம், ${farmerName}!` :
                 selectedLanguage === 'te' ? `స్వాగతం, ${farmerName}!` :
                 selectedLanguage === 'kn' ? `ಸ್ವಾಗತ, ${farmerName}!` :
                 selectedLanguage === 'ml' ? `സ്വാഗതം, ${farmerName}!` :
                 selectedLanguage === 'bn' ? `স্বাগতম, ${farmerName}!` :
                 selectedLanguage === 'mr' ? `स्वागत आहे, ${farmerName}!` :
                 selectedLanguage === 'gu' ? `સ્વાગત છે, ${farmerName}!` :
                 selectedLanguage === 'pa' ? `ਸੁਆਗਤ ਹੈ, ${farmerName}!` :
                 `Welcome, ${farmerName}!`}
              </h1>
              <p className="text-gray-600">
                {selectedLanguage === 'en' ? 'Manage your crop batches and QR codes' :
                 selectedLanguage === 'hi' ? 'अपने फसल बैच और QR कोड प्रबंधित करें' :
                 selectedLanguage === 'ta' ? 'உங்கள் பயிர் தொகுதிகள் மற்றும் QR குறியீடுகளை நிர்வகிக்கவும்' :
                 selectedLanguage === 'te' ? 'మీ పంట బ్యాచ్‌లు మరియు QR కోడ్‌లను నిర్వహించండి' :
                 selectedLanguage === 'kn' ? 'ನಿಮ್ಮ ಬೆಳೆ ಬ್ಯಾಚ್‌ಗಳು ಮತ್ತು QR ಕೋಡ್‌ಗಳನ್ನು ನಿರ್ವಹಿಸಿ' :
                 selectedLanguage === 'ml' ? 'നിങ്ങളുടെ വിള ബാച്ചുകളും QR കോഡുകളും നിയന്ത്രിക്കുക' :
                 selectedLanguage === 'bn' ? 'আপনার ফসল ব্যাচ এবং QR কোড পরিচালনা করুন' :
                 selectedLanguage === 'mr' ? 'तुमचे पीक बॅच आणि QR कोड व्यवस्थापित करा' :
                 selectedLanguage === 'gu' ? 'તમારા પાક બેચ અને QR કોડ મેનેજ કરો' :
                 selectedLanguage === 'pa' ? 'ਆਪਣੇ ਫਸਲ ਬੈਚ ਅਤੇ QR ਕੋਡ ਪ੍ਰਬੰਧਿਤ ਕਰੋ' :
                 'Manage your crop batches and QR codes'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-red-600 hover:text-red-700 border border-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              {t('logout', selectedLanguage)}
            </button>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-green-50 rounded-lg p-6 text-center">
              <div className="text-4xl mb-2">📦</div>
              <div className="text-3xl font-bold text-green-700">{totalBatches}</div>
              <div className="text-sm text-gray-600">Total Batches</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-6 text-center">
              <div className="text-4xl mb-2">✅</div>
              <div className="text-3xl font-bold text-blue-700">{totalBatches}</div>
              <div className="text-sm text-gray-600">Analyzed</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-6 text-center">
              <div className="text-4xl mb-2">📱</div>
              <div className="text-3xl font-bold text-purple-700">{qrCount}</div>
              <div className="text-sm text-gray-600">QR Codes</div>
            </div>
          </div>

          <button
            onClick={() => navigate('/farmer/create-batch')}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors text-lg"
          >
            {t('create_new_batch', selectedLanguage)}
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex border-b border-gray-200 mb-6">
            <button
              onClick={() => setActiveTab('batches')}
              className={`px-6 py-3 font-semibold transition-colors ${
                activeTab === 'batches'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              My Batches
            </button>
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-3 font-semibold transition-colors ${
                activeTab === 'profile'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Profile
            </button>
          </div>

          {/* Batches Tab */}
          {activeTab === 'batches' && (
            <>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">{t('my_batches', selectedLanguage)}</h2>
          
          {loading ? (
            <div className="text-center py-12 text-gray-500">
              <p>Loading batches...</p>
            </div>
          ) : batches.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-6xl mb-4">📋</div>
              <p className="text-lg">No batches yet</p>
              <p className="text-sm mt-2">Create your first batch to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {batches.map((batch) => (
                <div key={batch.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-800 mb-2">
                        {batch.crop_name}
                        {batch.crop_variety && <span className="text-gray-600 font-normal"> - {batch.crop_variety}</span>}
                      </h3>
                      <div className="space-y-1 text-sm text-gray-600">
                        <p>Method: <span className="font-medium capitalize">{batch.farming_method}</span></p>
                        <p>Harvest Date: <span className="font-medium">{batch.harvest_date}</span></p>
                        <p>Batch ID: <span className="font-mono text-xs">{batch.id}</span></p>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      {batch.has_qr ? (
                        <div className="text-center">
                          <div className="text-green-600 mb-2">✓ QR Generated</div>
                          <button
                            onClick={() => handleGenerateQR(batch.id)}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                          >
                            View QR
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleGenerateQR(batch.id)}
                          disabled={generatingQR === batch.id}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
                        >
                          {generatingQR === batch.id ? 'Generating...' : 'Generate QR'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
            </>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-6">My Profile</h2>
              
              {profileData ? (
                <div className="space-y-6">
                  {/* Profile Photo Section */}
                  <div className="flex items-center space-x-6">
                    <div className="relative">
                      {photoPreview || profileData.profile_photo_url ? (
                        <img
                          src={photoPreview || `${profileData.profile_photo_url}?t=${Date.now()}`}
                          alt="Profile"
                          className="w-24 h-24 rounded-full object-cover border-4 border-green-200"
                          onError={(e) => {
                            console.error('Failed to load profile photo:', profileData.profile_photo_url)
                            e.currentTarget.style.display = 'none'
                          }}
                        />
                      ) : (
                        <div className="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center border-4 border-green-200">
                          <span className="text-4xl">👤</span>
                          <span className="sr-only">Profile</span>
                        </div>
                      )}
                      {uploadingPhoto && (
                        <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs">Uploading...</span>
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="cursor-pointer">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleProfilePhotoUpload}
                          className="hidden"
                          disabled={uploadingPhoto}
                        />
                        <span className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg inline-block transition-colors">
                          {uploadingPhoto ? 'Uploading...' : 'Upload Photo'}
                        </span>
                      </label>
                      <p className="text-xs text-gray-500 mt-2">Max 5MB, JPG/PNG</p>
                    </div>
                  </div>

                  {/* Profile Info */}
                  {!editingProfile ? (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                        <p className="text-lg text-gray-900">{profileData.name || 'Not set'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                        <p className="text-lg text-gray-900">{profileData.phone}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                        <p className="text-lg text-gray-900">{profileData.location || 'Not set'}</p>
                      </div>
                      <button
                        onClick={() => setEditingProfile(true)}
                        className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                      >
                        Edit Profile
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                        <input
                          type="text"
                          value={profileName}
                          onChange={(e) => setProfileName(e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                        <input
                          type="text"
                          value={profileData.phone}
                          disabled
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                        <input
                          type="text"
                          value={profileLocation}
                          onChange={(e) => setProfileLocation(e.target.value)}
                          placeholder="e.g., Village, District, State"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                      <div className="flex space-x-4">
                        <button
                          onClick={handleProfileUpdate}
                          className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => {
                            setEditingProfile(false)
                            setProfileName(profileData.name || '')
                            setProfileLocation(profileData.location || '')
                          }}
                          className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p>Loading profile...</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* QR Code Modal */}
        {qrImage && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setQrImage(null)}>
            <div className="bg-white rounded-xl p-8 max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
              <h3 className="text-2xl font-bold text-gray-800 mb-4 text-center">QR Code Generated!</h3>
              <div className="bg-gray-50 p-6 rounded-lg mb-4">
                <img 
                  id="qr-code-image"
                  src={`data:image/png;base64,${qrImage.data}`} 
                  alt="QR Code" 
                  className="w-full max-w-xs mx-auto"
                />
              </div>
              <div className="text-center mb-4">
                <p className="text-sm text-gray-600 mb-2">QR ID: <span className="font-mono font-semibold">{qrImage.qrId}</span></p>
                <p className="text-xs text-gray-500">Consumers can scan this to verify your crop</p>
              </div>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    const link = document.createElement('a')
                    link.href = `data:image/png;base64,${qrImage.data}`
                    link.download = `QR-${qrImage.qrId}.png`
                    document.body.appendChild(link)
                    link.click()
                    document.body.removeChild(link)
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <span>📥</span>
                  <span>Download QR Code</span>
                </button>
                <button
                  onClick={() => setQrImage(null)}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

function CreateBatch() {
  const navigate = useNavigate()
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState('')
  const [currentStep, setCurrentStep] = React.useState(1)
  const [aiAnalysis, setAiAnalysis] = React.useState<any>(null)
  const [analyzingAI, setAnalyzingAI] = React.useState(false)
  const [selectedLanguage, setSelectedLanguage] = React.useState(() => {
    return localStorage.getItem('app_language') || 'en'
  })

  // Save language to localStorage when it changes
  React.useEffect(() => {
    localStorage.setItem('app_language', selectedLanguage)
  }, [selectedLanguage])
  
  const [formData, setFormData] = React.useState({
    crop_name: '',
    crop_variety: '',
    farming_method: 'organic',
    harvest_date: '',
  })

  // Support multiple pesticides and fertilizers
  const [pesticides, setPesticides] = React.useState<Array<{
    id: string
    image: File | null
    name: string
    dosage: string
    application_date: string
    extracting: boolean
  }>>([])

  const [fertilizers, setFertilizers] = React.useState<Array<{
    id: string
    image: File | null
    name: string
    quantity: string
    application_date: string
    extracting: boolean
  }>>([])

  // Field photo state
  const [fieldPhotoUrl, setFieldPhotoUrl] = React.useState('')
  const [uploadingFieldPhoto, setUploadingFieldPhoto] = React.useState(false)
  const [fieldPhotoPreview, setFieldPhotoPreview] = React.useState<string | null>(null)

  // Prepare crop options for react-select
  const cropOptions = cropsData.map(crop => ({
    value: crop.name,
    label: crop.name
  }))

  // Get varieties for selected crop
  const selectedCropData = cropsData.find(c => c.name === formData.crop_name)
  const varietyOptions = selectedCropData 
    ? selectedCropData.varieties.map(variety => ({
        value: variety,
        label: variety
      }))
    : []

  // Add new pesticide
  const addPesticide = () => {
    setPesticides([...pesticides, {
      id: Date.now().toString(),
      image: null,
      name: '',
      dosage: '',
      application_date: '',
      extracting: false
    }])
  }

  // Remove pesticide
  const removePesticide = (id: string) => {
    setPesticides(pesticides.filter(p => p.id !== id))
  }

  // Update pesticide
  const updatePesticide = (id: string, updates: Partial<typeof pesticides[0]>) => {
    setPesticides(pesticides.map(p => p.id === id ? { ...p, ...updates } : p))
  }

  // Add new fertilizer
  const addFertilizer = () => {
    setFertilizers([...fertilizers, {
      id: Date.now().toString(),
      image: null,
      name: '',
      quantity: '',
      application_date: '',
      extracting: false
    }])
  }

  // Remove fertilizer
  const removeFertilizer = (id: string) => {
    setFertilizers(fertilizers.filter(f => f.id !== id))
  }

  // Update fertilizer
  const updateFertilizer = (id: string, updates: Partial<typeof fertilizers[0]>) => {
    setFertilizers(fertilizers.map(f => f.id === id ? { ...f, ...updates } : f))
  }

  const handlePesticideImageUpload = async (e: React.ChangeEvent<HTMLInputElement>, pesticideId: string) => {
    const file = e.target.files?.[0]
    if (!file) return

    console.log('🚀 Starting pesticide image upload...')
    updatePesticide(pesticideId, { image: file, extracting: true })

    try {
      const token = localStorage.getItem('auth_token')
      
      // Upload file through backend
      console.log('� Step 1: Uploading to S3 via backend...')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', 'pesticide')
      
      const uploadResponse = await fetch(`${API_URL}/api/upload/image`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload image')
      }
      
      const { s3_url } = await uploadResponse.json()
      console.log('✅ Upload complete, s3_url:', s3_url)

      // Extract text with Textract
      console.log('📸 Step 2: Calling extraction endpoint...')
      const extractResponse = await fetch(`${API_URL}/api/extract/pesticide`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ s3_url })
      })
      console.log('✅ Extraction endpoint called, status:', extractResponse.status)
      
      const extractData = await extractResponse.json()
      console.log('📦 Extraction response:', extractData)

      // Check if extraction was successful and log the result
      if (extractData.success) {
        console.log('✅ OCR extraction successful:', extractData.extracted_data)
        console.log('📄 Raw text:', extractData.raw_text)
        console.log('🎯 Confidence:', extractData.confidence)
      } else {
        console.warn('⚠️ OCR extraction failed:', extractData.error)
        console.log('You can still enter the information manually')
      }

      updatePesticide(pesticideId, {
        image: file,
        name: extractData.extracted_data?.name || '',
        dosage: extractData.extracted_data?.dosage || '',
        extracting: false
      })
    } catch (err) {
      console.error('Pesticide extraction error:', err)
      updatePesticide(pesticideId, { image: file, extracting: false })
      // Don't show error to user - they can enter manually
    }
  }

  const handleFertilizerImageUpload = async (e: React.ChangeEvent<HTMLInputElement>, fertilizerId: string) => {
    const file = e.target.files?.[0]
    if (!file) return

    console.log('🚀 Starting fertilizer image upload...')
    updateFertilizer(fertilizerId, { image: file, extracting: true })

    try {
      const token = localStorage.getItem('auth_token')
      
      // Upload file through backend
      console.log('📡 Step 1: Uploading to S3 via backend...')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', 'fertilizer')
      
      const uploadResponse = await fetch(`${API_URL}/api/upload/image`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload image')
      }
      
      const { s3_url } = await uploadResponse.json()
      console.log('✅ Upload complete, s3_url:', s3_url)

      // Extract text with Textract
      console.log('🔍 Step 2: Calling extraction endpoint...')
      const extractResponse = await fetch(`${API_URL}/api/extract/fertilizer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ s3_url })
      })
      console.log('✅ Extraction endpoint called, status:', extractResponse.status)
      
      const extractData = await extractResponse.json()
      console.log('📦 Extraction response:', extractData)

      // Check if extraction was successful and log the result
      if (extractData.success) {
        console.log('✅ OCR extraction successful:', extractData.extracted_data)
        console.log('📄 Raw text:', extractData.raw_text)
        console.log('🎯 Confidence:', extractData.confidence)
      } else {
        console.warn('⚠️ OCR extraction failed:', extractData.error)
        console.log('You can still enter the information manually')
      }

      updateFertilizer(fertilizerId, {
        image: file,
        name: extractData.extracted_data?.name || '',
        quantity: extractData.extracted_data?.quantity || '',
        extracting: false
      })
    } catch (err) {
      console.error('Fertilizer extraction error:', err)
      updateFertilizer(fertilizerId, { image: file, extracting: false })
      // Don't show error to user - they can enter manually
    }
  }

  const handleFieldPhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB')
      return
    }
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file')
      return
    }

    setUploadingFieldPhoto(true)
    
    try {
      // Create preview
      const previewUrl = URL.createObjectURL(file)
      setFieldPhotoPreview(previewUrl)

      // Upload to S3
      const token = localStorage.getItem('auth_token')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', 'field_photo')

      const response = await fetch(`${API_URL}/api/upload/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to upload field photo')

      const data = await response.json()
      setFieldPhotoUrl(data.s3_url)
    } catch (error) {
      console.error('Error uploading field photo:', error)
      alert('Failed to upload field photo')
      setFieldPhotoPreview(null)
    } finally {
      setUploadingFieldPhoto(false)
    }
  }

  const handleRemoveFieldPhoto = () => {
    if (fieldPhotoPreview) {
      URL.revokeObjectURL(fieldPhotoPreview)
    }
    setFieldPhotoPreview(null)
    setFieldPhotoUrl('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('🚀 Form submitted')
    setError('')
    
    // Validate required fields
    if (!formData.crop_name) {
      console.log('❌ Validation failed: crop_name missing')
      setError('Please select a crop name')
      return
    }
    if (!formData.harvest_date) {
      console.log('❌ Validation failed: harvest_date missing')
      setError('Please select a harvest date')
      return
    }
    
    console.log('✅ Validation passed, form data:', formData)
    setLoading(true)

    try {
      const token = localStorage.getItem('auth_token')
      console.log('🔑 Auth token:', token ? 'Found' : 'Missing')
      
      // Build treatments array from all pesticides and fertilizers
      const treatments = []
      
      // Add all pesticides
      for (const pesticide of pesticides) {
        if (pesticide.name && pesticide.application_date) {
          treatments.push({
            treatment_type: 'pesticide',
            name: pesticide.name,
            dosage_or_quantity: pesticide.dosage || '',
            application_date: pesticide.application_date,
            package_image_url: null,
            extracted_data: null
          })
        }
      }
      
      // Add all fertilizers
      for (const fertilizer of fertilizers) {
        if (fertilizer.name && fertilizer.application_date) {
          treatments.push({
            treatment_type: 'fertilizer',
            name: fertilizer.name,
            dosage_or_quantity: fertilizer.quantity || '',
            application_date: fertilizer.application_date,
            package_image_url: null,
            extracted_data: null
          })
        }
      }

      const requestBody = {
        ...formData,
        harvest_date: formData.harvest_date ? `${formData.harvest_date}-01` : '', // Convert YYYY-MM to YYYY-MM-DD
        treatments,
        crop_image_urls: [],
        field_photo_url: fieldPhotoUrl || null,
      }
      console.log('📤 Sending request to:', `${API_URL}/api/batch/create`)
      console.log('📦 Request body:', requestBody)

      const response = await fetch(`${API_URL}/api/batch/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
      })

      console.log('📥 Response status:', response.status)
      const data = await response.json()
      console.log('📥 Response data:', data)

      if (!response.ok) {
        throw new Error(data.message || 'Failed to create batch')
      }

      console.log('✅ Batch created successfully, batch_id:', data.batch_id)
      setCurrentStep(2)
      
      // Auto-trigger AI analysis
      await performAIAnalysis(data.batch_id)
      
    } catch (err: any) {
      console.error('❌ Error creating batch:', err)
      setError(err.message || 'Failed to create batch')
      setLoading(false)
    }
  }

  const performAIAnalysis = async (batch_id: string) => {
    setAnalyzingAI(true)
    try {
      const token = localStorage.getItem('auth_token')
      const response = await fetch(`${API_URL}/api/batch/analyze?batch_id=${batch_id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!response.ok) throw new Error('AI analysis failed')

      const analysisData = await response.json()
      // Extract safety_analysis from response
      setAiAnalysis(analysisData.safety_analysis || analysisData)
      setCurrentStep(3)
    } catch (err) {
      console.error('AI analysis error:', err)
      setError('AI analysis failed, but batch was created')
    } finally {
      setAnalyzingAI(false)
      setLoading(false)
    }
  }

  const getRiskColor = (score: number) => {
    if (score >= 71) return 'text-green-600'
    if (score >= 41) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getRiskBgColor = (score: number) => {
    if (score >= 71) return 'bg-green-50 border-green-200'
    if (score >= 41) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Language Selector */}
          <div className="mb-4 flex justify-end">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="appearance-none bg-green-50 border border-green-200 text-green-900 px-4 py-2 pr-8 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer"
            >
              {LANGUAGE_OPTIONS.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.flag} {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div className={`flex items-center ${currentStep >= 1 ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${currentStep >= 1 ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>
                  {currentStep > 1 ? '✓' : '1'}
                </div>
                <span className="ml-2 font-medium hidden sm:inline">Batch Details</span>
              </div>
              <div className={`flex-1 h-1 mx-4 ${currentStep >= 2 ? 'bg-green-600' : 'bg-gray-200'}`}></div>
              <div className={`flex items-center ${currentStep >= 2 ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${currentStep >= 2 ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>
                  {currentStep > 2 ? '✓' : '2'}
                </div>
                <span className="ml-2 font-medium hidden sm:inline">AI Analysis</span>
              </div>
              <div className={`flex-1 h-1 mx-4 ${currentStep >= 3 ? 'bg-green-600' : 'bg-gray-200'}`}></div>
              <div className={`flex items-center ${currentStep >= 3 ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${currentStep >= 3 ? 'bg-green-600 text-white' : 'bg-gray-200'}`}>
                  {currentStep > 3 ? '✓' : '3'}
                </div>
                <span className="ml-2 font-medium hidden sm:inline">Complete</span>
              </div>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-green-700 mb-6">
            {selectedLanguage === 'en' ? 'Create New Batch' :
             selectedLanguage === 'hi' ? 'नया बैच बनाएं' :
             selectedLanguage === 'ta' ? 'புதிய தொகுதி உருவாக்கு' :
             selectedLanguage === 'te' ? 'కొత్త బ్యాచ్ సృష్టించండి' :
             selectedLanguage === 'kn' ? 'ಹೊಸ ಬ್ಯಾಚ್ ರಚಿಸಿ' :
             selectedLanguage === 'ml' ? 'പുതിയ ബാച്ച് സൃഷ്ടിക്കുക' :
             selectedLanguage === 'bn' ? 'নতুন ব্যাচ তৈরি করুন' :
             selectedLanguage === 'mr' ? 'नवीन बॅच तयार करा' :
             selectedLanguage === 'gu' ? 'નવો બેચ બનાવો' :
             selectedLanguage === 'pa' ? 'ਨਵਾਂ ਬੈਚ ਬਣਾਓ' :
             'Create New Batch'}
          </h1>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Step 1: Batch Creation Form */}
          {currentStep === 1 && (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('crop_name', selectedLanguage)} *
                </label>
                <Select
                  options={cropOptions}
                  value={cropOptions.find(opt => opt.value === formData.crop_name) || null}
                  onChange={(option) => {
                    setFormData({
                      ...formData, 
                      crop_name: option?.value || '',
                      crop_variety: ''
                    })
                  }}
                  placeholder="Search and select crop..."
                  className="text-base"
                  classNamePrefix="select"
                  isClearable
                  isSearchable
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {selectedLanguage === 'en' ? 'Crop Variety' :
                   selectedLanguage === 'hi' ? 'फसल की किस्म' :
                   selectedLanguage === 'ta' ? 'பயிர் வகை' :
                   selectedLanguage === 'te' ? 'పంట రకం' :
                   selectedLanguage === 'kn' ? 'ಬೆಳೆ ವಿಧ' :
                   selectedLanguage === 'ml' ? 'വിള ഇനം' :
                   selectedLanguage === 'bn' ? 'ফসলের জাত' :
                   selectedLanguage === 'mr' ? 'पीक प्रकार' :
                   selectedLanguage === 'gu' ? 'પાકની જાત' :
                   selectedLanguage === 'pa' ? 'ਫਸਲ ਦੀ ਕਿਸਮ' :
                   'Crop Variety'}
                </label>
                <Select
                  options={varietyOptions}
                  value={varietyOptions.find(opt => opt.value === formData.crop_variety) || null}
                  onChange={(option) => setFormData({...formData, crop_variety: option?.value || ''})}
                  placeholder={formData.crop_name ? "Search and select variety..." : "Select crop first"}
                  className="text-base"
                  classNamePrefix="select"
                  isClearable
                  isSearchable
                  isDisabled={!formData.crop_name}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('farming_method', selectedLanguage)} *
                </label>
                <select
                  value={formData.farming_method}
                  onChange={(e) => setFormData({...formData, farming_method: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                >
                  <option value="organic">{t('organic', selectedLanguage)}</option>
                  <option value="conventional">{t('conventional', selectedLanguage)}</option>
                  <option value="integrated">Integrated</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('harvest_date', selectedLanguage)} *
                </label>
                <input
                  type="month"
                  value={formData.harvest_date}
                  onChange={(e) => setFormData({...formData, harvest_date: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                />
              </div>

              {/* Pesticide Section */}
              <div className="border-t pt-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Pesticide Information (Optional)</h3>
                  <button
                    type="button"
                    onClick={addPesticide}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
                  >
                    + Add Pesticide
                  </button>
                </div>
                
                {pesticides.length === 0 ? (
                  <p className="text-gray-500 text-sm">No pesticides added. Click "Add Pesticide" to add one.</p>
                ) : (
                  <div className="space-y-6">
                    {pesticides.map((pesticide, index) => (
                      <div key={pesticide.id} className="border border-gray-200 rounded-lg p-4 relative">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="font-medium text-gray-700">Pesticide #{index + 1}</h4>
                          <button
                            type="button"
                            onClick={() => removePesticide(pesticide.id)}
                            className="text-red-600 hover:text-red-700 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Upload Pesticide Package Image
                            </label>
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => handlePesticideImageUpload(e, pesticide.id)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                            {pesticide.extracting && (
                              <p className="text-sm text-blue-600 mt-2">🔍 Extracting text with AI...</p>
                            )}
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Pesticide Name
                            </label>
                            <input
                              type="text"
                              value={pesticide.name}
                              onChange={(e) => updatePesticide(pesticide.id, { name: e.target.value })}
                              placeholder="Auto-filled from image or enter manually"
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Dosage
                            </label>
                            <input
                              type="text"
                              value={pesticide.dosage}
                              onChange={(e) => updatePesticide(pesticide.id, { dosage: e.target.value })}
                              placeholder="e.g., 2ml per liter"
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Application Date
                            </label>
                            <input
                              type="month"
                              value={pesticide.application_date}
                              onChange={(e) => updatePesticide(pesticide.id, { application_date: e.target.value })}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Fertilizer Section */}
              <div className="border-t pt-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Fertilizer Information (Optional)</h3>
                  <button
                    type="button"
                    onClick={addFertilizer}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
                  >
                    + Add Fertilizer
                  </button>
                </div>
                
                {fertilizers.length === 0 ? (
                  <p className="text-gray-500 text-sm">No fertilizers added. Click "Add Fertilizer" to add one.</p>
                ) : (
                  <div className="space-y-6">
                    {fertilizers.map((fertilizer, index) => (
                      <div key={fertilizer.id} className="border border-gray-200 rounded-lg p-4 relative">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="font-medium text-gray-700">Fertilizer #{index + 1}</h4>
                          <button
                            type="button"
                            onClick={() => removeFertilizer(fertilizer.id)}
                            className="text-red-600 hover:text-red-700 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Upload Fertilizer Package Image
                            </label>
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => handleFertilizerImageUpload(e, fertilizer.id)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                            {fertilizer.extracting && (
                              <p className="text-sm text-blue-600 mt-2">🔍 Extracting text with AI...</p>
                            )}
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Fertilizer Name
                            </label>
                            <input
                              type="text"
                              value={fertilizer.name}
                              onChange={(e) => updateFertilizer(fertilizer.id, { name: e.target.value })}
                              placeholder="Auto-filled from image or enter manually"
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Quantity
                            </label>
                            <input
                              type="text"
                              value={fertilizer.quantity}
                              onChange={(e) => updateFertilizer(fertilizer.id, { quantity: e.target.value })}
                              placeholder="e.g., 50kg per acre"
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Application Date
                            </label>
                            <input
                              type="month"
                              value={fertilizer.application_date}
                              onChange={(e) => updateFertilizer(fertilizer.id, { application_date: e.target.value })}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Field Photo Section */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">📸 Farm Field Photo (Optional)</h3>
                <p className="text-sm text-gray-600 mb-4">Upload a photo of your farm field where this crop is grown</p>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Field Photo
                  </label>
                  {!fieldPhotoPreview ? (
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFieldPhotoUpload}
                      disabled={uploadingFieldPhoto}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  ) : (
                    <div className="space-y-4">
                      <div className="relative">
                        <img
                          src={fieldPhotoPreview}
                          alt="Field preview"
                          className="w-full max-h-64 object-cover rounded-lg"
                        />
                        {uploadingFieldPhoto && (
                          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                            <span className="text-white">Uploading...</span>
                          </div>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={handleRemoveFieldPhoto}
                        disabled={uploadingFieldPhoto}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50"
                      >
                        Remove Photo
                      </button>
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">Max 5MB, JPG/PNG</p>
                </div>
              </div>

              <div className="flex gap-4 pt-6">
                <button
                  type="button"
                  onClick={() => navigate('/farmer/dashboard')}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {selectedLanguage === 'en' ? 'Cancel' :
                   selectedLanguage === 'hi' ? 'रद्द करें' :
                   selectedLanguage === 'ta' ? 'ரத்து செய்' :
                   selectedLanguage === 'te' ? 'రద్దు చేయండి' :
                   selectedLanguage === 'kn' ? 'ರದ್ದುಮಾಡಿ' :
                   selectedLanguage === 'ml' ? 'റദ്ദാക്കുക' :
                   selectedLanguage === 'bn' ? 'বাতিল করুন' :
                   selectedLanguage === 'mr' ? 'रद्द करा' :
                   selectedLanguage === 'gu' ? 'રદ કરો' :
                   selectedLanguage === 'pa' ? 'ਰੱਦ ਕਰੋ' :
                   'Cancel'}
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 
                    (selectedLanguage === 'en' ? 'Creating & Analyzing...' :
                     selectedLanguage === 'hi' ? 'बना रहे हैं और विश्लेषण कर रहे हैं...' :
                     selectedLanguage === 'ta' ? 'உருவாக்கி பகுப்பாய்வு செய்கிறது...' :
                     selectedLanguage === 'te' ? 'సృష్టిస్తోంది & విశ్లేషిస్తోంది...' :
                     selectedLanguage === 'kn' ? 'ರಚಿಸುತ್ತಿದೆ ಮತ್ತು ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...' :
                     selectedLanguage === 'ml' ? 'സൃഷ്ടിക്കുകയും വിശകലനം ചെയ്യുകയും ചെയ്യുന്നു...' :
                     selectedLanguage === 'bn' ? 'তৈরি এবং বিশ্লেষণ করা হচ্ছে...' :
                     selectedLanguage === 'mr' ? 'तयार आणि विश्लेषण करत आहे...' :
                     selectedLanguage === 'gu' ? 'બનાવી અને વિશ્લેષણ કરી રહ્યા છીએ...' :
                     selectedLanguage === 'pa' ? 'ਬਣਾ ਰਹੇ ਹਾਂ ਅਤੇ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਹੇ ਹਾਂ...' :
                     'Creating & Analyzing...') 
                    : t('create_batch', selectedLanguage)}
                </button>
              </div>
            </form>
          )}

          {/* Step 2: AI Analysis in Progress */}
          {currentStep === 2 && analyzingAI && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4 animate-pulse">🤖</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">AI Analysis in Progress</h2>
              <p className="text-gray-600 mb-4">Analyzing crop safety with AWS Bedrock...</p>
              <div className="flex justify-center">
                <div className="spinner border-green-600"></div>
              </div>
            </div>
          )}

          {/* Step 3: AI Analysis Results */}
          {currentStep === 3 && aiAnalysis && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-6xl mb-4">✅</div>
                <h2 className="text-2xl font-bold text-green-700 mb-2">Batch Created Successfully!</h2>
                <p className="text-gray-600">AI safety analysis complete</p>
              </div>

              {/* Safety Score */}
              <div className={`border rounded-lg p-6 ${getRiskBgColor(aiAnalysis.safety_score)}`}>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Safety Analysis</h3>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-700 font-medium">Safety Score:</span>
                  <span className={`text-4xl font-bold ${getRiskColor(aiAnalysis.safety_score)}`}>
                    {aiAnalysis.safety_score}/100
                  </span>
                </div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-700 font-medium">Risk Level:</span>
                  <span className={`text-xl font-bold ${getRiskColor(aiAnalysis.safety_score)}`}>
                    {aiAnalysis.risk_level}
                  </span>
                </div>
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm text-gray-700">{aiAnalysis.explanation}</p>
                </div>
              </div>

              {/* Consumption Recommendations */}
              {aiAnalysis.consumption_recommendations && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-xl font-bold text-blue-900 mb-4">🍽️ Consumption Recommendations</h3>
                  <div className="space-y-4 text-sm text-blue-800">
                    {aiAnalysis.consumption_recommendations.how_to_clean && (
                      <div>
                        <h4 className="font-semibold mb-2">How to Clean:</h4>
                        <p>{aiAnalysis.consumption_recommendations.how_to_clean}</p>
                      </div>
                    )}
                    {aiAnalysis.consumption_recommendations.safety_tips && (
                      <div>
                        <h4 className="font-semibold mb-2">Safety Tips:</h4>
                        <p>{aiAnalysis.consumption_recommendations.safety_tips}</p>
                      </div>
                    )}
                    {aiAnalysis.consumption_recommendations.recommendations && (
                      <div>
                        <h4 className="font-semibold mb-2">Recommendations:</h4>
                        <p>{aiAnalysis.consumption_recommendations.recommendations}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-4">
                <button
                  onClick={() => navigate('/farmer/dashboard')}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <Toaster position="top-center" />
        
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-6">
            <h1 className="text-3xl font-bold text-center bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              FARM2FORK
            </h1>
            <p className="text-center text-gray-600 text-sm mt-1">
              AI-Powered Farm-to-Consumer Traceability
            </p>
          </div>
        </header>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<ModeSelection />} />
          <Route path="/farmer/login" element={<FarmerLogin />} />
          <Route path="/farmer/dashboard" element={<FarmerDashboard />} />
          <Route path="/farmer/create-batch" element={<CreateBatch />} />
          <Route path="/consumer/scan" element={<QRScanner />} />
          <Route path="/consumer/verify/:qrId" element={<ConsumerVerify />} />
        </Routes>

        {/* Footer */}
        <footer className="bg-white mt-20 py-6 border-t">
          <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
            <p>&copy; 2024 FARM2FORK. AI-Powered Farm-to-Consumer Traceability Platform.</p>
            <p className="mt-2 text-xs text-gray-500">
              Backend: FastAPI + PostgreSQL | Frontend: React + TypeScript | AI: AWS Bedrock, Textract, Rekognition
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App




