# Home.html Template CSS to MDBootstrap Conversion Plan

## Objective
Convert hardcoded CSS styles in `/Users/petergangmei/Developer/Crossplatform/django/northeastindia_wiki/templates/home.html` to MDBootstrap utility classes while maintaining the same visual appearance and functionality.

## Analysis of Current Issues

### Identified Hardcoded Styles to Convert:
1. **Hero Section Inline Style**: `style="min-height: 50vh;"` on line 12
2. **Featured Image Inline Style**: `style="height: 200px; object-fit: cover;"` on line 113
3. **Icon Container Inline Style**: `style="width: 50px; height: 50px;"` on line 140
4. **Avatar Circle Inline Style**: `style="width: 30px; height: 30px;"` on line 176
5. **Responsive Media Queries**: Lines 222-235 with custom CSS for mobile responsiveness
6. **Hover Effect CSS**: Lines 216-219 for hover background transitions

## Tasks

### Phase 1: Convert Hero Section Styling
- [ ] Replace `style="min-height: 50vh;"` with Bootstrap utility class `min-vh-50`
- [ ] Remove responsive media queries for hero section and replace with Bootstrap responsive utilities
- [ ] Convert hero section mobile font-size adjustments to Bootstrap responsive typography classes

### Phase 2: Convert Image and Container Sizing
- [ ] Replace `style="height: 200px; object-fit: cover;"` with Bootstrap utility classes
- [ ] Convert icon container sizing `style="width: 50px; height: 50px;"` to Bootstrap utilities
- [ ] Replace avatar circle sizing `style="width: 30px; height: 30px;"` with Bootstrap utilities

### Phase 3: Convert Custom CSS to Bootstrap Classes
- [ ] Replace hover effect CSS with Bootstrap hover utilities or keep as minimal custom CSS if no equivalent exists
- [ ] Remove all responsive media queries and replace with Bootstrap responsive utilities
- [ ] Clean up the `<style>` section, keeping only truly necessary custom CSS

### Phase 4: Testing and Verification
- [ ] Test responsive behavior on different screen sizes
- [ ] Verify visual appearance matches the original design
- [ ] Ensure all interactive elements still function correctly
- [ ] Validate that no functionality is broken

## Bootstrap Utility Classes to Use

### For Hero Section:
- `min-vh-50` for min-height: 50vh
- `min-vh-md-60` for mobile responsive height
- `fs-1`, `fs-2`, etc. for responsive font sizes

### For Images and Containers:
- `h-*` utilities for height (custom values may need CSS variables)
- `w-*` utilities for width
- `object-fit-cover` for object-fit (if available in Bootstrap 5)

### For Responsive Design:
- `d-*` utilities for responsive display
- `text-*` utilities for responsive text alignment
- Responsive spacing utilities (`p-*`, `m-*`)

## Notes
- Prioritize Bootstrap utility classes over custom CSS
- Keep minimal custom CSS only when no Bootstrap equivalent exists
- Maintain the Wikipedia-style visual design
- Ensure responsive behavior is preserved or improved
- Test thoroughly on mobile and desktop viewports

## Review Section

### Changes Made
1. **Updated CSS for Section Headings**: Modified `.card-header.bg-light` and `.card-header.bg-primary` rules in `main.css:199` and `main.css:222`
   - Changed `font-weight: bold` to `font-weight: normal !important`
   - Reduced `font-size` from `14px` to `12px`
   - Added specific h3 targeting rules for both `.card-header.bg-light h3` and `.card-header.bg-primary h3`
   - This affects section headings like "Today's Featured Article", "Recent Contributors", "How to Contribute"

### Files Modified
- `/Users/petergangmei/Developer/Crossplatform/django/northeastindia_wiki/static/css/main.css` (lines 199, 227, 210, 238)

### Impact
- Section headings now appear with lighter font weight (normal instead of bold)
- Section headings now have smaller text size (12px instead of 14px)
- Added `!important` declarations to ensure styles override any conflicting CSS
- Maintains Wikipedia-style design consistency with more subtle section headers

### Next Steps
- Static files have been collected to apply all changes
- Changes are ready for viewing on the website