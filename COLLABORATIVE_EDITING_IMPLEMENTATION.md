# Wikipedia-Style Collaborative Editing Implementation

## 🎯 Goal Achieved
Successfully transformed the author-only editing system into a Wikipedia-style collaborative platform where any contributor can edit articles and submit changes for review.

## ✅ Features Implemented

### 1. **Enhanced Permission System**
- **Before**: Only original authors + editors/admins could edit articles
- **After**: Any contributor or higher can edit unprotected articles
- **New Permission Logic**: 
  - `viewer`: Cannot edit articles
  - `contributor`: Can edit unprotected articles, semi-protected with sufficient reputation
  - `editor`: Can edit unprotected, semi-protected, and protected articles
  - `admin`: Can edit all articles including fully-protected

### 2. **Article Protection Levels** (Wikipedia-style)
- **Unprotected**: Any contributor+ can edit directly
- **Semi-protected**: Requires minimum 10 contributions + 50 reputation points
- **Protected**: Only editors and admins can edit
- **Fully Protected**: Only admins can edit

### 3. **Trust Score & Reputation System**
- **Trust Score Calculation**: Based on approval rate, edit volume, and revert penalty
- **Auto-approval**: High-trust users (7.0+ score, 20+ edits) get auto-approved edits
- **Reputation Tracking**: 
  - `approved_edit_count`: Number of approved edits
  - `rejected_edit_count`: Number of rejected edits  
  - `revert_count`: Number of reverted edits
  - `trust_score`: Calculated score (0.0-10.0)

### 4. **Article Watching System**
- Users can watch articles to get notifications of changes
- "Watch this page" / "Unwatch" button in article tools
- AJAX-powered toggle functionality
- Watchers get notified when articles are updated

### 5. **Enhanced Notifications**
- **Edit Proposals**: Notify watchers and authors when changes are submitted for review
- **Approved Changes**: Notify watchers when articles they watch are updated
- **Collaborative Feedback**: Clear messages about why edit permissions are denied

### 6. **UI Improvements**
- **Protection Indicators**: Visual badges showing article protection level
- **Smart Edit Button**: Shows disabled edit button with tooltip for users who can't edit
- **Enhanced Tools Dropdown**: Added "Watch this page" functionality
- **Protection Tooltips**: Hover information about protection reasons

## 📁 Files Modified

### Models (`app/models.py`)
```python
# Added to Content model:
PROTECTION_LEVELS = (
    ('unprotected', 'Unprotected'),
    ('semi_protected', 'Semi-protected'), 
    ('protected', 'Protected'),
    ('fully_protected', 'Fully Protected'),
)
protection_level = models.CharField(max_length=20, choices=PROTECTION_LEVELS, default='unprotected')
protection_reason = models.TextField(blank=True)
protection_expires = models.DateTimeField(null=True, blank=True)
protected_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
edit_count = models.PositiveIntegerField(default=0)
watchers = models.ManyToManyField(User, blank=True, related_name='watched_content')

# Enhanced can_be_edited_by() method with Wikipedia-style logic
```

### User Profiles (`accounts/models.py`)
```python
# Added trust and collaboration fields:
approved_edit_count = models.PositiveIntegerField(default=0)
rejected_edit_count = models.PositiveIntegerField(default=0)
revert_count = models.PositiveIntegerField(default=0)
trust_score = models.FloatField(default=0.0)
auto_approve_edits = models.BooleanField(default=False)
watch_notifications = models.BooleanField(default=True)
mention_notifications = models.BooleanField(default=True)

# Added calculate_trust_score() and update_trust_score() methods
```

### Views (`app/views.py`)
- **Enhanced `article_edit`**: Better permission feedback based on protection level and user role
- **Added `toggle_article_watch`**: AJAX endpoint for watching/unwatching articles
- **Enhanced revision review**: Updates trust scores when edits are approved/rejected
- **Collaborative notifications**: Notifies watchers when articles are edited or approved

### Templates (`templates/articles/article_detail.html`)
- **Protection indicators**: Visual badges for protected articles
- **Smart edit button**: Shows disabled state with helpful tooltips
- **Watch functionality**: JavaScript for toggling article watch status
- **Enhanced tools menu**: Added "Watch this page" option

### URLs (`app/urls.py`)
```python
path('articles/<slug:slug>/toggle-watch/', views.toggle_article_watch, name='article-toggle-watch'),
```

## 🗄️ Database Changes

### Migrations Created
- `accounts/migrations/0002_userprofile_approved_edit_count_and_more.py`
- `app/migrations/0014_content_edit_count_content_protected_by_and_more.py`

### New Database Fields
**UserProfile table:**
- `approved_edit_count` (PositiveIntegerField)
- `rejected_edit_count` (PositiveIntegerField) 
- `revert_count` (PositiveIntegerField)
- `trust_score` (FloatField)
- `auto_approve_edits` (BooleanField)
- `watch_notifications` (BooleanField)
- `mention_notifications` (BooleanField)

**Content table:**
- `protection_level` (CharField)
- `protection_reason` (TextField)
- `protection_expires` (DateTimeField)
- `protected_by` (ForeignKey to User)
- `edit_count` (PositiveIntegerField)
- `watchers` (ManyToManyField to User)

## 🚀 How It Works

### 1. **Collaborative Editing Flow**
1. Any contributor can click "Edit" on unprotected articles
2. Changes are submitted as revisions for review (approved articles)
3. Editors/admins review and approve/reject changes
4. Approved changes update the live article
5. Watchers get notified of updates

### 2. **Protection System**
- Articles can be protected by editors/admins
- Protection level determines who can edit
- Semi-protected articles require reputation threshold
- Protection can be temporary with expiration dates

### 3. **Trust System**
- Users build trust through approved edits
- High-trust users get auto-approval privileges
- Reverts and rejections lower trust scores
- Trust score affects editing permissions

### 4. **Watch System**
- Users can watch articles they're interested in
- JavaScript handles real-time watch status updates
- Notifications keep watchers informed of changes

## 🔧 Next Steps (Future Enhancements)

1. **Revert Functionality**: Add ability to revert bad edits
2. **Edit Conflicts**: Handle simultaneous editing by multiple users
3. **Page Move Protection**: Implement move protection for article titles
4. **Vandalism Detection**: Automated detection of problematic edits
5. **User Blocking**: Temporary blocks for disruptive users
6. **Edit Filters**: Automated filters to catch spam/vandalism
7. **Rollback Tools**: Quick rollback for trusted users

## 📖 User Guide

### For Contributors
- **Editing**: Click "Edit" on any unprotected article
- **Watching**: Use "Tools" → "Watch this page" to follow articles
- **Reputation**: Build trust through quality edits that get approved

### For Editors/Admins
- **Protection**: Set protection levels on controversial articles
- **Review**: Approve/reject pending edits from contributors
- **Monitoring**: Watch for vandalism and quality issues

### For Users with No Edit Access
- Clear messages explain why editing is restricted
- Guidance on how to gain editing privileges
- Alternative ways to contribute (reporting issues, suggestions)

---

## 🎉 Impact

This implementation transforms the site from an author-centric system to a true collaborative wiki like Wikipedia, encouraging community participation while maintaining quality through graduated permissions and review processes.

**Key Benefits:**
- ✅ Increased community engagement
- ✅ Faster content updates and improvements  
- ✅ Quality control through review system
- ✅ Protection against vandalism
- ✅ Scalable permission system
- ✅ User trust and reputation building