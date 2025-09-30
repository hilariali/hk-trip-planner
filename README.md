# HK Travel Planner 🏙️

An AI-powered, conversational travel planner for Hong Kong, specifically designed for families and seniors with accessibility needs. Built with Streamlit and powered by Large Language Models via Akash Network.

## Features ✨

- **Conversational Interface**: Natural language interaction for describing travel preferences
- **Accessibility-First**: Specialized recommendations for mobility, dietary, and safety needs
- **AI-Powered Intelligence**: Uses DeepSeek-R1-Distill-Llama-70B via Akash Network for contextual recommendations
- **Real-time Data**: Integrates Hong Kong government APIs for weather and venue information
- **Personalized Itineraries**: Generates day-by-day plans with detailed explanations
- **Export Options**: Multiple formats for offline use and sharing

## Architecture 🏗️

### LLM-Centric Design
- **LLM Orchestrator**: Central intelligence layer using Akash Network
- **Conversation Context**: Maintains chat history and user preferences
- **Data Integration**: Combines real-time APIs with curated venue database
- **Multi-format Export**: JSON, CSV, and printable formats

### Key Components
- `main.py`: Streamlit chat interface
- `services/llm_orchestrator.py`: AI conversation management
- `config.py`: Configuration for Akash Network integration
- `.kiro/specs/hk-travel-planner/`: Complete project specification

## Quick Start 🚀

### Prerequisites
- Python 3.9+
- Streamlit
- OpenAI Python client

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hilariali/hk-trip-planner.git
cd hk-trip-planner
```

2. Install dependencies:
```bash
pip install streamlit openai
```

3. Run the application:
```bash
streamlit run main.py
```

4. Open your browser to `http://localhost:8501`

## Usage 💬

1. **Start a Conversation**: Describe your Hong Kong travel plans in natural language
2. **Specify Needs**: Mention accessibility requirements, dietary restrictions, budget, and group composition
3. **Get Recommendations**: Receive AI-generated itineraries with detailed explanations
4. **Refine Plans**: Ask questions and request modifications through chat
5. **Export Itinerary**: Download your plan in multiple formats

### Example Conversation
```
User: "I'm planning a 3-day Hong Kong trip for my elderly parents who use wheelchairs and prefer soft meals. Budget is around $200 per day."

AI: "I'd be happy to help create an accessible Hong Kong itinerary for your parents! Let me design a 3-day plan focusing on wheelchair-accessible venues with elevator access and restaurants offering soft meal options..."
```

## Configuration ⚙️

The application uses Akash Network for LLM services. Configuration is handled in `config.py`:

```python
llm_config = LLMConfig(
    api_key="your-akash-api-key",
    base_url="https://chatapi.akash.network/api/v1",
    model="DeepSeek-R1-Distill-Llama-70B"
)
```

## Project Structure 📁

```
hk-trip-planner/
├── main.py                          # Streamlit chat interface
├── config.py                        # Configuration settings
├── services/
│   └── llm_orchestrator.py         # LLM integration
├── .kiro/specs/hk-travel-planner/   # Project specifications
│   ├── requirements.md              # Feature requirements
│   ├── design.md                    # System design
│   └── tasks.md                     # Implementation tasks
├── data/                            # Venue and attraction data
└── README.md                        # This file
```

## Development 🛠️

### Specification-Driven Development
This project follows a spec-driven approach with detailed documentation:

- **Requirements**: User stories and acceptance criteria
- **Design**: Architecture and component specifications  
- **Tasks**: Step-by-step implementation plan

### Key Technologies
- **Frontend**: Streamlit with chat interface
- **AI**: DeepSeek-R1-Distill-Llama-70B via Akash Network
- **Data**: Hong Kong government APIs + curated venue database
- **Architecture**: Service-oriented with conversation context management

## Contributing 🤝

1. Review the specifications in `.kiro/specs/hk-travel-planner/`
2. Check the task list for current development priorities
3. Follow the established patterns for LLM integration
4. Ensure accessibility considerations in all features

## Accessibility Focus ♿

This application prioritizes accessibility for:
- **Mobility**: Wheelchair access, elevator availability, step-free routes
- **Dietary**: Soft meals, vegetarian options, allergy accommodations
- **Safety**: Senior-friendly pacing, rest areas, clear navigation
- **Budget**: Discount identification, transparent cost breakdowns

## License 📄

This project is open source and available under the MIT License.

## Support 💡

For questions about:
- **Usage**: Check the conversation examples and feature documentation
- **Development**: Review the specifications and task list
- **Issues**: Open a GitHub issue with detailed description

---

Built with ❤️ for accessible travel in Hong Kong