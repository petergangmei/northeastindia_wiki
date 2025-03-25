# northeastindia.wiki

northeastindia.wiki is an open-source platform dedicated to showcasing the rich cultural heritage, history, and notable personalities of Northeast India. Inspired by Wikipedia, this platform aims to become a comprehensive resource while encouraging user contributions with a structured review process.

## 🚀 Features

### Core Features
- **Cultural Heritage:** Articles highlighting traditions, festivals, and customs of Northeast India.
- **History:** Detailed historical timelines and significant events.
- **Famous Personalities:** SEO-optimized pages dedicated to influential figures.
- **Content Categories:** Organized by state, tribe, and other categories for easy navigation.

### Contribution & Editing
- **Account-Based Contributions:** Contributors must register an account.
- **Rich Text Editor:** Provides intuitive content formatting.
- **Image Embedding:** Images sourced externally to reduce storage load.
- **Revision History:** Maintains version control for content updates.
- **Admin Review System:** All contributions require admin approval.

### User Engagement & Community
- **Search Functionality:** Advanced search with tagging and related content suggestions.
- **Discussion Forums:** Dedicated spaces for content discussion and feedback.
- **User Profiles:** Contributors can showcase their contributions and earn badges.

### Moderation & Quality Control
- **Automated Moderation Tools:** AI or community-driven content flagging.
- **Reputation System:** Trusted contributors earn points and badges.

### Content Enrichment
- **Interactive Maps:** Displays cultural landmarks and historical sites.
- **Multilingual Support:** Expands accessibility for regional languages.
- **Resource Libraries:** Offers downloadable resources and digital archives.

### Technical & SEO Enhancements
- **Mobile Optimization:** Ensures seamless performance across devices.
- **Performance Analytics:** Tracks content engagement and visitor trends.
- **Public API Access:** Provides developers with integration opportunities.

### Social & Outreach Integration
- **Social Media Sharing:** Enables content sharing to expand reach.
- **Event Calendars:** Lists cultural and historical events in the region.
- **Newsletter Subscriptions:** Offers regular updates on new content and events.

## 🛠️ Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/northeastindia.wiki.git
   cd northeastindia.wiki
   ```
2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Migrations:**
   ```bash
   python manage.py migrate --settings=core.settings.dev
   ```
5. **Create a Superuser:**
   ```bash
   python manage.py createsuperuser --settings=core.settings.dev
   ```
6. **Start the Development Server:**
   ```bash
   python manage.py runserver --settings=core.settings.dev
   ```
   Note: The project uses a split settings structure:
   - `core/settings/common.py` - Base settings shared across all environments
   - `core/settings/dev.py` - Development environment settings
   - `core/settings/prod.py` - Production environment settings
   
   By default, `manage.py` uses the development settings.
   
7. Visit `http://localhost:8000` in your browser.

## 📋 Contribution Guidelines

We welcome contributions from the community! Here's how you can get involved:

1. **Fork the Repository.**
2. **Create a Branch:**
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Make Your Changes.**
4. **Test Your Changes Thoroughly.**
5. **Submit a Pull Request.**

## 📄 Code of Conduct
Please review our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a positive community experience.

## 📧 Contact
For any questions or suggestions, feel free to reach out via email at [contact@northeastindia.wiki](mailto:contact@northeastindia.wiki).

## 🌟 Support
If you find this project valuable, please consider giving it a star on GitHub and sharing it with your network! Together, we can preserve and promote Northeast India's rich heritage. 😊

