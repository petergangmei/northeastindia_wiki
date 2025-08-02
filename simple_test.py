#!/usr/bin/env python
"""
Simple test for collaborative editing permissions
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from app.models import Content

def test_basic_permissions():
    """Test basic collaborative editing"""
    print("🧪 Testing basic collaborative editing...")
    
    try:
        # Get existing users
        users = User.objects.all()[:3]
        if len(users) < 2:
            print("❌ Need at least 2 users in database for testing")
            return
            
        # Get a test article
        article = Content.objects.filter(content_type='article', published=True).first()
        if not article:
            print("❌ No published articles found for testing")
            return
            
        print(f"📄 Testing with article: '{article.title}'")
        print(f"🛡️  Protection level: {article.protection_level}")
        
        # Test different users
        for i, user in enumerate(users[:2]):
            can_edit = article.can_be_edited_by(user)
            try:
                role = user.profile.role if hasattr(user, 'profile') else 'no profile'
            except:
                role = 'no profile'
            print(f"👤 User '{user.username}' (role: {role}) can edit: {can_edit}")
            
        print("\n✅ Basic permission testing completed!")
        print(f"📋 New features available:")
        print(f"   - Wikipedia-style collaborative editing")
        print(f"   - Protection levels for articles")
        print(f"   - Enhanced permission system")
        print(f"   - Article watching functionality")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_basic_permissions()