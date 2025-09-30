# 🏙️ Hong Kong Trip Planner

An AI-powered, web-based trip planning assistant designed specifically for families and seniors visiting Hong Kong. The system generates safe, accessible, and budget-friendly itineraries that address real mobility, dietary, and accessibility needs.

## ✨ Key Features

### 🎯 Accessibility-First Design
- **Comprehensive accessibility information** for every venue
- **Mobility support** for wheelchairs, walking aids, and stair avoidance
- **Senior-friendly options** with rest areas and difficulty ratings
- **Family facilities** including parent rooms and child-friendly venues

### 🍽️ Dietary Accommodation
- **Soft meal options** perfect for seniors
- **Vegetarian and dietary restriction** filtering
- **Allergy-friendly** venue identification
- **Cultural dietary needs** (halal, no seafood options)

### 🤖 AI-Powered Intelligence
- **Weather-responsive planning** adjusting indoor/outdoor activities
- **Budget optimization** with senior and child discounts
- **Route optimization** limiting walking distance and including rest stops
- **Smart venue selection** based on accessibility requirements

### 📱 User-Friendly Interface
- **Streamlit web app** with intuitive forms
- **Real-time validation** and helpful guidance
- **Multiple export formats** (CSV, JSON, printable)
- **Mobile-responsive** design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hk-trip-planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python3 database.py
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** to `http://localhost:8501`

### Test the Components
```bash
python3 test_app.py
```

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with SQLite database
- **AI Integration**: Amazon Q Developer (planned)
- **APIs**: Hong Kong government weather and transport data
- **Deployment**: Streamlit Community Cloud (free hosting)

### Project Structure
```
hk-trip-planner/
├── app.py                 # Main Streamlit application
├── models.py              # Data models and structures
├── database.py            # Database setup and seeding
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml      # API keys and configuration
├── services/
│   ├── venue_service.py   # Venue database operations
│   ├── weather_service.py # Weather API integration
│   └── itinerary_engine.py # AI itinerary generation
└── test_app.py           # Component testing
```

## 🎮 Usage

### 1. Set Your Preferences
- **Family composition**: Adults, children, seniors
- **Accessibility needs**: Wheelchair, elevator requirements, stair avoidance
- **Dietary restrictions**: Soft meals, vegetarian, allergies
- **Budget range**: Per person daily budget in HKD
- **Trip duration**: Number of days
- **Transportation**: MTR, taxi, bus preferences

### 2. Generate Your Itinerary
- Click "Generate Itinerary" to create your personalized plan
- AI considers weather, accessibility, and budget constraints
- Maximum 3 venues per day to avoid fatigue

### 3. Review and Export
- View detailed day-by-day plans with accessibility information
- See cost breakdowns and walking distances
- Export as CSV or JSON for offline use
- Print-friendly format available

## 🏥 Accessibility Features

### Venue Information
- ♿ Wheelchair accessibility
- 🛗 Elevator availability
- 🚻 Accessible toilets
- 🚶 Step-free access
- 👶 Parent facilities
- 🪑 Rest areas
- 📊 Difficulty level (1-5 scale)

### Smart Filtering
- **Automatic filtering** based on mobility needs
- **Alternative suggestions** when requirements can't be met
- **Transparent communication** about accessibility limitations
- **Safety considerations** for children and seniors

## 💰 Budget Features

### Cost Transparency
- **Detailed cost breakdowns** by category
- **Real-time budget validation** against preferences
- **Senior and child discounts** automatically applied
- **Transport cost estimation** included

### Hong Kong Pricing
- **Realistic HKD pricing** for attractions and meals
- **Local transport costs** (MTR, bus, taxi)
- **Discount opportunities** clearly marked

## 🌤️ Weather Integration

### Smart Recommendations
- **Real-time weather data** from Hong Kong Observatory
- **Indoor/outdoor activity balancing** based on conditions
- **Senior-friendly weather assessment** avoiding extremes
- **Rainy day alternatives** automatically suggested

## 🚀 Deployment

### Streamlit Community Cloud (Recommended)

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Deploy SilverJoy Planner HK"
git push origin main
```

#### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `hk-trip-planner`
5. Main file path: `app.py`
6. Click "Deploy!"

#### Step 3: Configure Secrets
In Streamlit Cloud dashboard:
1. Go to your app settings
2. Click "Secrets"
3. Add your secrets:
```toml
[ai]
api_key = "sk-UVKYLhiNf0MKXRqbnDiehA"
base_url = "https://chatapi.akash.network/api/v1"
model = "Meta-Llama-3-1-8B-Instruct-FP8"
```

#### Step 4: Access Your App
Your app will be available at: `https://your-app-name.streamlit.app`

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Environment Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/hk-trip-planner.git
cd hk-trip-planner
pip install -r requirements.txt
python database.py  # Initialize database
streamlit run app.py
```

## 🔧 Configuration

### API Keys (.streamlit/secrets.toml)
```toml
[weather]
api_key = "your_weather_api_key"
base_url = "https://data.weather.gov.hk/weatherAPI/opendata/"

[transport]
data_gov_hk_base = "https://api.data.gov.hk/v1/"

[ai]
amazon_q_key = "your_amazon_q_key"
```

## 📊 Sample Data

The application includes sample Hong Kong venues:

### Attractions
- **Victoria Peak Sky Terrace** - Iconic views with accessibility features
- **Hong Kong Space Museum** - Indoor, family-friendly with full accessibility
- **Hong Kong Park** - Outdoor park with accessible paths

### Restaurants
- **Maxim's Palace Dim Sum** - Traditional dim sum with soft meal options
- **Café de Coral** - Local chain with senior-friendly congee and soups

### Transport
- **Central MTR Station** - Major interchange with full accessibility

## 🧪 Testing

### Component Tests
```bash
python3 test_app.py
```

### Manual Testing Scenarios
1. **Senior with mobility needs** - wheelchair, soft meals, budget-conscious
2. **Family with children** - child-friendly venues, parent facilities
3. **Rainy weather** - indoor activity preferences
4. **Budget constraints** - maximum daily spending limits

## 🔮 Future Enhancements

### Phase 2 Features
- **Real-time crowd density** integration
- **User feedback loop** for venue recommendations
- **Social sharing** and collaborative planning
- **Mobile app** with offline capabilities

### Advanced AI Features
- **Machine learning** from user behavior patterns
- **Predictive modeling** for optimal visit times
- **Natural language processing** for venue reviews
- **Computer vision** for accessibility assessment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the test script: `python3 test_app.py`
2. Review the component logs in the Streamlit interface
3. Verify API keys in `.streamlit/secrets.toml`

## 🏆 Acknowledgments

- **Hong Kong Observatory** for weather data APIs
- **Hong Kong Government** for transport and venue data
- **Streamlit Community** for the excellent web framework
- **Accessibility advocates** who inspired this project's focus

---

**Built with ❤️ for accessible travel in Hong Kong**