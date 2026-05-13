[← Zurück zur CLAUDE.md](../CLAUDE.md)

# Tutorial & Wizard Systems

## Tutorial Service (`services/tutorial_service.py`)
Manages guided user introduction and contextual help:
- **Welcome Tutorial**: Multi-step introduction with spotlight highlighting
- **Tab-specific Hints**: Contextual help for each UI section
- **Tutorial State**: Tracks which tutorials have been shown
- **Configuration**: Loads from `config/tutorial_config.json`

Key features:
- `show_welcome_tutorial()` - displays initial guided tour
- `show_tab_hint(tab_id)` - shows contextual help for specific tabs
- `mark_tutorial_completed()` - tracks tutorial completion state
- `is_tutorial_shown()` - checks if specific tutorial was already shown

## Tutorial Overlay (`views/tutorial_overlay.py`)
Interactive tutorial overlay with spotlight functionality:
- **SpotlightOverlay**: Semi-transparent overlay with cutout highlighting
- **Tutorial Cards**: Context-aware help cards with navigation
- **Interactive Elements**: Next/Previous/Skip functionality
- **Responsive Layout**: Adapts to desktop/mobile layouts

## Character Creation Wizard (`services/wizard_service.py`)
Step-by-step guided character creation:
- **WizardSchritt**: Individual wizard step with validation
- **WizardService**: Event-driven wizard state management
- **Step Validation**: Each step can validate character state
- **Progress Tracking**: Visual progress indication via `wizard_bar.py`

Wizard steps include:
1. Setting selection
2. Race selection
3. Profile setup
4. Attribute distribution
5. Skill allocation
6. Handicap selection
7. Talent selection
8. Equipment purchase

## Setting Assistant (`views/setting_assistent_view.py`)
Multi-step wizard for creating and editing game settings:
- **4-Step Process**: Basic info → Element configuration → Conflict resolution → Preview
- **Merge Functionality**: Combine multiple existing settings
- **Conflict Resolution**: Handle overlapping elements when merging
- **Draft Management**: Save/restore work in progress via `models/setting_draft.py`

## Template Wizard (`views/template_wizard.py`)
Guided creation of character templates:
- **Multi-step Dialog**: Captures template metadata and configuration
- **Character Analysis**: Analyzes current character for template creation
- **Validation**: Ensures template completeness and validity
- **JSON Export**: Saves templates in standardized format

## Integration Points
- **ServiceContainer**: All tutorial/wizard services are dependency-injected
- **Event System**: Wizard progress triggers UI updates via event service
- **Configuration**: Tutorial content and wizard steps are configurable via JSON
- **Mobile Optimization**: All wizards adapt to mobile layouts automatically
