# Wikipedia-Like System Implementation

## Overview
This document outlines the implementation of a comprehensive Wikipedia-like collaborative editing system for the Northeast India Wiki, based on the requirements specified in wiki.md.

## Completed Features

### 1. Enhanced User Rights System ✅
**Implementation:** Updated `UserProfile` model with new role hierarchy
- **Viewer** → **Contributor** → **Autoconfirmed** → **Extended-confirmed** → **Reviewer** → **Editor** → **Admin**
- **Autoconfirmed Status:** Automatically granted after 4 days + 10 approved edits
- **Extended-confirmed Status:** Automatically granted after 30 days + 500 approved edits
- **Reviewer Role:** Can review pending changes and mark revisions as "sighted"

**Key Features:**
- Automatic role progression based on Wikipedia criteria
- Progress tracking for users approaching next role level
- Role-specific permissions for editing different protection levels

### 2. Advanced Protection Levels ✅
**Implementation:** Extended `Content.protection_level` with Wikipedia-style options
- **Unprotected:** Any contributor+ can edit
- **Semi-protected:** Requires autoconfirmed status (4 days + 10 edits)
- **Extended-confirmed Protected:** Requires extended-confirmed status (30 days + 500 edits)
- **Pending Changes:** All edits require reviewer approval before going live
- **Protected:** Only editors and admins can edit
- **Fully Protected:** Only admins can edit

**Key Features:**
- Visual protection indicators on article pages
- Context-aware permission messages
- Automatic protection level enforcement

### 3. Pending Changes & Flagged Revisions System ✅
**Implementation:** Enhanced `ContentRevision` model with dual-view capability
- **Public View:** Shows last approved version for pending changes protection
- **Live View:** Shows current content including pending changes (for reviewers)
- **Flagged Revisions:** Support for "sighted" and "flagged" revision statuses
- **Automatic Application:** Privileged users' edits are auto-approved

**Key Features:**
- Dual content rendering based on user role
- Pending changes queue for reviewers
- Automatic role-based edit approval

### 4. Recent Changes Patrol Dashboard ✅
**Implementation:** New `recent_changes_patrol` view with comprehensive monitoring
- **Real-time Monitoring:** Last 24 hours of activity
- **Unified Queue:** Pending revisions and new content in one view
- **Filter Options:** By type, status, and time
- **Quick Actions:** Direct links to review interfaces

**Key Features:**
- Wikipedia-style patrol interface
- Statistics dashboard
- Reviewer-only access with role checking

### 5. Deletion Workflow System ✅
**Implementation:** New `DeletionRequest` and `DeletionDiscussion` models
- **Speedy Deletion:** Immediate admin review for policy violations
- **PROD (Proposed Deletion):** 7-day grace period for uncontroversial deletions
- **AfD (Articles for Deletion):** Community discussion for complex cases

**Key Features:**
- Role-based deletion request permissions
- Automatic timing and notifications
- Community discussion system for AfD

### 6. Automatic Role Management ✅
**Implementation:** Django signals and management commands
- **Real-time Updates:** Automatic role checking on edit approval
- **Batch Processing:** Management command for bulk role updates
- **Notification System:** Users notified of role promotions

**Key Features:**
- `update_user_roles` management command
- Signal-based automatic updates
- Progress tracking and notifications

## Database Schema Changes

### UserProfile Model Enhancements
```python
# New roles added
USER_ROLES = (
    ('viewer', 'Viewer'),
    ('contributor', 'Contributor'),
    ('autoconfirmed', 'Autoconfirmed'),           # NEW
    ('extended_confirmed', 'Extended Confirmed'), # NEW
    ('reviewer', 'Reviewer'),                     # NEW
    ('editor', 'Editor'),
    ('admin', 'Administrator'),
)

# New methods added
- check_and_update_role()
- can_review_content()
- can_edit_semi_protected()
- can_edit_extended_confirmed_protected()
- get_role_progress()
```

### Content Model Enhancements
```python
# New protection levels
PROTECTION_LEVELS = (
    ('unprotected', 'Unprotected'),
    ('semi_protected', 'Semi-protected'),
    ('extended_confirmed', 'Extended Confirmed Protected'), # NEW
    ('pending_changes', 'Pending Changes'),                 # NEW
    ('protected', 'Protected'),
    ('fully_protected', 'Fully Protected'),
)

# New methods added
- needs_pending_changes_review()
- get_public_content()
- get_live_content()
- has_pending_changes()
```

### ContentRevision Model Enhancements
```python
# New revision statuses
REVISION_STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('pending_review', 'Pending Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('sighted', 'Sighted'),   # NEW - Flagged revisions
    ('flagged', 'Flagged'),   # NEW - Flagged revisions
)

# New fields for flagged revisions
- is_stable: Boolean
- quality_level: Integer (0=basic, 1=good, 2=featured)
- sighted_by: ForeignKey to User
- sighted_at: DateTime
```

### New Models Added
```python
# Deletion workflow
class DeletionRequest(TimeStampedModel):
    # Handles speedy, PROD, and AfD deletion requests
    
class DeletionDiscussion(TimeStampedModel):
    # Handles AfD community discussions
```

## Views and Templates

### New Views Added
1. **`recent_changes_patrol(request)`** - Patrol dashboard for reviewers
2. **`request_deletion(request, slug)`** - Deletion request interface

### Enhanced Views
1. **`article_edit(request, slug)`** - Updated for pending changes workflow
2. **`article_detail(request, slug)`** - Added protection level displays

### New Templates Added
1. **`articles/recent_changes_patrol.html`** - Patrol dashboard interface
2. **`articles/request_deletion.html`** - Deletion request form

### Enhanced Templates
1. **`articles/article_detail.html`** - Updated protection indicators and tools menu

## URL Routes Added
```python
# New patrol and deletion routes
path('wiki/recent-changes-patrol/', views.recent_changes_patrol, name='recent-changes-patrol'),
path('wiki/<slug:slug>/request-deletion/', views.request_deletion, name='request-deletion'),
```

## Management Commands
```bash
# Role management
python manage.py update_user_roles --dry-run  # Preview changes
python manage.py update_user_roles            # Apply role updates
```

## Key Wikipedia Features Implemented

### ✅ Graduated Trust Levels
- Time + edit count based role progression
- Automatic promotion notifications
- Progress tracking toward next role

### ✅ Multi-layer Review System
- Pending changes protection
- Reviewer approval workflow
- Flagged revisions support

### ✅ Topic-based Protection
- Content-specific protection levels
- Role-based editing permissions
- Visual protection indicators

### ✅ Human Patrol Systems
- Recent changes monitoring
- Unified patrol queue
- Role-based access control

### ✅ Deletion Workflow
- Three-tier deletion system (Speedy/PROD/AfD)
- Community discussion framework
- Automatic timing and notifications

### ✅ Transparent History
- Complete revision tracking
- Public/live content views
- Immutable edit log

## Benefits Achieved

1. **Quality Control:** Multi-layer review prevents vandalism and poor content
2. **User Engagement:** Clear progression path encourages long-term participation
3. **Scalability:** Automated role management reduces administrative overhead
4. **Community Building:** Collaborative editing with role-based responsibilities
5. **Content Protection:** Flexible protection levels for sensitive topics
6. **Transparency:** Full audit trail of all changes and decisions

## Future Enhancements (Not Yet Implemented)

1. **Revision Flagging System** - Advanced quality scoring
2. **New Page Patrol** - Dedicated queue for new content
3. **Abuse Filters** - Automated spam and vandalism detection
4. **User Block System** - Temporary and permanent user restrictions

## Notes

- All features exclude anonymous editing as requested
- System maintains backward compatibility with existing content
- Role progression is fully automated based on contribution metrics
- Protection levels can be applied selectively to sensitive content
- Community discussion features support collaborative decision-making

This implementation provides a robust foundation for Wikipedia-style collaborative editing while maintaining quality control appropriate for a cultural heritage wiki.