# XML Sitemaps for Northeast India Wiki

This document describes the comprehensive XML sitemap system implemented for the Northeast India Wiki to help search engines efficiently discover and index all cultural content.

## Overview

The sitemap system provides structured XML files that help search engines understand the site's content hierarchy and update frequency. This is crucial for getting Northeast India's rich cultural heritage properly indexed by Google, Bing, and other search engines.

## Sitemap Structure

### Sitemap Index (`/sitemap.xml`)
The main sitemap index that references all individual sitemaps:
- **Static Pages**: Home, article listings, search pages
- **Articles**: All published and approved articles about Northeast India
- **Categories**: Topic-based organization (culture, history, travel, etc.)
- **Tags**: Granular content labeling (traditional, heritage, cuisine, etc.)

### Individual Sitemaps

1. **Static Pages Sitemap** (`/sitemap-static.xml`)
   - Priority: 0.8
   - Change frequency: Weekly
   - Includes: Home page, article lists, category pages, search

2. **Articles Sitemap** (`/sitemap-articles.xml`)
   - Priority: 0.9-1.0 (highest for featured articles)
   - Change frequency: Weekly
   - Only includes published, approved articles
   - Featured articles get priority 1.0

3. **Categories Sitemap** (`/sitemap-categories.xml`)
   - Priority: 0.6-0.8 (based on article count)
   - Change frequency: Monthly
   - Only categories with published articles

4. **Tags Sitemap** (`/sitemap-tags.xml`)
   - Priority: 0.5-0.7 (based on usage)
   - Change frequency: Monthly
   - Only tags used by published articles

## File Locations

- **Sitemap Classes**: `/app/sitemaps.py`
- **URL Configuration**: `/core/urls.py`
- **Validation Command**: `/app/management/commands/validate_sitemaps.py`

## Usage

### Accessing Sitemaps
- **Main sitemap index**: `https://yourdomain.com/sitemap.xml`
- **Individual sitemaps**: `https://yourdomain.com/sitemap-{section}.xml`

### Validating Sitemaps
```bash
# Validate all sitemaps
python manage.py validate_sitemaps --settings=core.settings.dev

# Validate specific sitemap with verbose output
python manage.py validate_sitemaps --sitemap articles --verbose --settings=core.settings.dev
```

### Robots.txt Integration
The robots.txt file automatically includes the sitemap reference:
```
Sitemap: https://yourdomain.com/sitemap.xml
```

## Search Engine Submission

### Google Search Console
1. Add your domain to Google Search Console
2. Go to Sitemaps section
3. Submit: `https://yourdomain.com/sitemap.xml`
4. Monitor indexing status and coverage

### Bing Webmaster Tools
1. Add your site to Bing Webmaster Tools  
2. Go to Sitemaps section
3. Submit: `https://yourdomain.com/sitemap.xml`
4. Monitor crawling and indexing reports

## Content Quality Controls

The sitemap system includes several quality controls to ensure only appropriate content is indexed:

- **Only Published Content**: Drafts and pending articles are excluded
- **Only Approved Content**: Articles must pass admin review
- **Security Filtering**: Private user areas are excluded
- **Active Content Only**: Categories and tags must have associated published articles

## Maintenance

### Adding New Content Types
To add new content types (e.g., Personalities, Cultural Elements):

1. Create a new sitemap class in `/app/sitemaps.py`
2. Add the sitemap to the `SITEMAPS` registry
3. Ensure the model has a working `get_absolute_url()` method
4. Test with the validation command

### Monitoring
- Use the validation command regularly to ensure all sitemaps are working
- Monitor search console for crawling errors
- Check sitemap access logs for search engine bot activity

## SEO Benefits

This sitemap system provides several SEO benefits:

- **Efficient Discovery**: Search engines can find all content quickly
- **Update Notifications**: Last modification dates help with crawl prioritization
- **Priority Guidance**: Important content gets higher priority values
- **Clean URLs**: All URLs are absolute and use HTTPS when available
- **Cultural Focus**: Optimized specifically for Northeast India content

## Technical Implementation

- Built using Django's built-in sitemap framework
- Automatic protocol detection (HTTP/HTTPS)
- Dynamic content with real-time updates
- XML validation and error handling
- Memory-efficient querying for large content volumes

## Troubleshooting

If sitemaps are not working:

1. Check Django settings include `django.contrib.sitemaps`
2. Verify URL patterns are correctly configured
3. Run the validation command to identify issues
4. Check server logs for any errors
5. Ensure database contains published, approved content

For more details, see the sitemap classes in `/app/sitemaps.py` and the validation command output.