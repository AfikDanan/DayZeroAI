# Project Structure

```
preboarding_service/
├── 📁 app/                         # Main application code
│   ├── 📁 api/                     # FastAPI routes and endpoints
│   │   ├── __init__.py
│   │   ├── jobs.py                 # Job status endpoints
│   │   └── webhooks.py             # Webhook endpoints
│   ├── 📁 models/                  # Pydantic data models
│   │   ├── __init__.py
│   │   └── webhook.py              # Webhook and employee models
│   ├── 📁 services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── audio_generator.py      # Google Cloud TTS
│   │   ├── notification_service.py # SendGrid emails
│   │   ├── script_generator.py     # OpenAI script generation
│   │   ├── video_generator.py      # Video composition
│   │   └── webhook_processor.py    # Webhook processing
│   ├── 📁 utils/             # Utilities and helpers
│   │   └── 📁 static/        # Static assets (templates, logos)
│   │       └── template.png  # Video slide template
│   ├── 📁 workers/           # Background job workers
│   │   └── video_worker.py   # RQ video generation worker
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   └── main.py              # FastAPI application
├── 📁 docs/                  # Documentation
│   ├── API.md               # API reference
│   ├── ARCHITECTURE.md      # System architecture
│   └── SETUP.md             # Setup and installation guide
├── 📁 examples/              # Example files and templates
│   ├── .env.example         # Environment variables template
│   ├── google_credencial.json.example  # GCP credentials template
│   └── webhook_payload.json # Example webhook payload
├── 📁 scripts/               # Startup and utility scripts
│   ├── production_startup.py    # Production setup guide
│   ├── start_api_server.bat     # Windows API server startup
│   ├── start_worker.bat         # Windows worker startup
│   └── test_production.ps1      # PowerShell test script
├── 📁 tests/                 # Organized test suite
│   ├── 📁 unit/             # Unit tests (fast, isolated)
│   │   ├── test_welcome_slide.py   # Slide generation tests
│   │   ├── test_script_only.py     # Script generation tests
│   │   └── test_audio_from_script.py # Audio generation tests
│   ├── 📁 integration/      # Integration tests (require services)
│   │   ├── test_basic_api.py       # API endpoint tests
│   │   ├── test_webhook.py         # Webhook processing tests
│   │   └── test_integration.py     # Service integration tests
│   ├── 📁 e2e/              # End-to-end tests (full workflow)
│   │   ├── test_full_pipeline.py   # Complete pipeline tests
│   │   ├── test_video_generation.py # Video generation tests
│   │   └── test_with_dev_output.py # Development output tests
│   ├── 📁 utils/            # Test utilities and debugging
│   │   ├── check_setup.py          # Setup validation
│   │   ├── check_queue.py          # Redis queue inspection
│   │   ├── debug_config.py         # Configuration debugging
│   │   └── start_services.py       # Service startup helper
│   ├── 📁 fixtures/         # Test fixtures and mocks
│   │   ├── test_video_mock.py      # Mock implementations
│   │   └── test_dev_output.py      # Development helpers
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── run_tests.py         # Test runner script
│   └── README.md            # Test documentation
├── 📁 tools/                 # Development and debugging tools
│   ├── debug_google_cloud.py   # GCP TTS debugging
│   ├── debug_template.py       # Template loading debug
│   ├── test_app_demo.py         # Application demo
│   └── test_production_api.py   # Production API test
├── 📁 data/                  # Sample and mock data
│   └── mock_data.json       # Example employee data
├── 📁 dev_output/            # Development output files
│   └── [job_id]/            # Generated files for review
│       ├── script.txt       # Generated script
│       ├── final_audio.mp3  # Generated audio
│       ├── 📁 slides/       # Individual slide images
│       ├── final_video.mp4  # Complete video
│       └── summary.md       # Generation summary
├── 📁 videos/                # Final video output
│   └── [job_id].mp4         # Generated videos
├── 📁 test_output/           # Test file outputs
│   └── 📁 samples/          # Test slide samples
├── .env                     # Environment variables (not in git)
├── .gitignore              # Git ignore rules
├── google_credencial.json  # GCP credentials (not in git)
├── README.md               # Main project documentation
├── PROJECT_STRUCTURE.md    # This file
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Directory Purposes

### 📁 Core Application (`app/`)
Contains the main application code organized by responsibility:
- **api/**: HTTP endpoints and routing
- **models/**: Data validation and serialization
- **services/**: Business logic and external integrations
- **workers/**: Background job processing
- **utils/**: Shared utilities and static assets

### 📁 Documentation (`docs/`)
Comprehensive project documentation:
- **API.md**: Complete API reference with examples
- **ARCHITECTURE.md**: System design and component overview
- **SETUP.md**: Detailed installation and configuration guide

### 📁 Examples (`examples/`)
Template files and examples for easy setup:
- Configuration templates
- Sample webhook payloads
- Credential file templates

### 📁 Scripts (`scripts/`)
Startup and utility scripts for different environments:
- Production startup helpers
- Platform-specific startup scripts
- Test automation scripts

### 📁 Tests (`tests/`)
Comprehensive test suite:
- Unit tests for individual components
- Integration tests for full workflows
- Setup validation and debugging tools
- Service startup helpers

### 📁 Tools (`tools/`)
Development and debugging utilities:
- Debugging tools for specific components
- Demo and testing applications
- Development workflow helpers

### 📁 Output Directories
- **dev_output/**: Development files for review and debugging
- **videos/**: Final generated video files
- **test_output/**: Test artifacts and samples

## File Naming Conventions

### Python Files
- `snake_case.py` for all Python files
- `test_*.py` for test files
- `debug_*.py` for debugging tools
- `check_*.py` for validation scripts

### Configuration Files
- `.env` for environment variables
- `*.example` for template files
- `*.json` for data and configuration
- `*.md` for documentation

### Scripts
- `*.bat` for Windows batch files
- `*.ps1` for PowerShell scripts
- `*.py` for Python scripts

## Import Structure

### Relative Imports
```python
# Within app/ directory
from app.config import settings
from app.models.webhook import EmployeeData
from app.services.video_generator import VideoGenerator
```

### Test Imports
```python
# In tests/ directory
import sys
sys.path.append('.')
from app.services.video_generator import VideoGenerator
```

## Development Workflow

1. **Setup**: Use `examples/` templates to configure environment
2. **Development**: Work in `app/` directory with proper imports
3. **Testing**: Use `tests/` for validation and debugging
4. **Tools**: Use `tools/` for development utilities
5. **Documentation**: Update `docs/` for any changes
6. **Scripts**: Use `scripts/` for deployment and startup

This structure promotes:
- **Separation of concerns**: Clear boundaries between components
- **Easy navigation**: Logical grouping of related files
- **Development efficiency**: Quick access to tools and examples
- **Maintainability**: Clear documentation and testing structure
- **Scalability**: Organized structure supports growth