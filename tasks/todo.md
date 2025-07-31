# Views.py Cleanup Plan

## Objective
Clean up `/Users/petergangmei/Developer/Crossplatform/django/northeastindia_wiki/app/views.py` by removing account-related function definitions and updating imports.

## Tasks

### Phase 1: Identify Account-Related Functions
- [ ] Identify all 10 account-related functions to be removed:
  1. `user_login` (line 124)
  2. `user_logout` (line 152) 
  3. `register` (line 160)
  4. `profile` (line 180)
  5. `edit_profile` (line 197)
  6. `password_reset_request` (line 1198)
  7. `password_reset_done` (line 1242)
  8. `password_reset_confirm` (line 1248)
  9. `password_reset_complete` (line 1274)
  10. `user_contributions` (line 1281)

### Phase 2: Remove Functions
- [ ] Remove `user_login` function and its implementation
- [ ] Remove `user_logout` function and its implementation  
- [ ] Remove `register` function and its implementation
- [ ] Remove `profile` function and its implementation
- [ ] Remove `edit_profile` function and its implementation
- [ ] Remove `password_reset_request` function and its implementation
- [ ] Remove `password_reset_done` function and its implementation
- [ ] Remove `password_reset_confirm` function and its implementation
- [ ] Remove `password_reset_complete` function and its implementation
- [ ] Remove `user_contributions` function and its implementation

### Phase 3: Update Imports
- [ ] Remove unused authentication-related imports:
  - `from django.contrib.auth import login, authenticate, logout`
  - `from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm`
  - `from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode`
  - `from django.utils.encoding import force_bytes, force_str`
  - `from django.contrib.auth.tokens import default_token_generator`
  - `from django.template.loader import render_to_string`
  - `from django.core.mail import send_mail, BadHeaderError`
- [ ] Remove `CustomUserCreationForm` from forms import
- [ ] Keep necessary imports that are still used by remaining functions

### Phase 4: Verification
- [ ] Ensure no syntax errors in the cleaned file
- [ ] Verify remaining functions are intact
- [ ] Check that all necessary imports are still present for remaining functions

## Notes
- Keep all non-account related functions intact
- Maintain proper code formatting and structure
- Ensure no breaking changes to existing functionality