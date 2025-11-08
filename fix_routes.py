"""
Script to add trailing slashes to FastAPI route decorators
Run this IN your HF Space repository directory
"""
import re
import os

def fix_routes_in_file(filepath):
    """Add trailing slashes to route decorators"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match route decorators without trailing slash in the path
    # Matches: @router.get("/stats") -> @router.get("/stats/")
    # But NOT: @router.get("/") (already has slash)
    patterns = [
        (r'@router\.(get|post|put|patch|delete)\("(/[^"]+[^/])"\)', r'@router.\1("\2/")'),
    ]
    
    original = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Files to fix
files_to_fix = [
    'backend/api/agents.py',
    'backend/api/tickets.py',
    'backend/api/forecasting.py'
]

print("🔧 Adding trailing slashes to route decorators...\n")

for filepath in files_to_fix:
    if os.path.exists(filepath):
        if fix_routes_in_file(filepath):
            print(f"✅ Fixed: {filepath}")
        else:
            print(f"⏭️  No changes needed: {filepath}")
    else:
        print(f"❌ File not found: {filepath}")

print("\n✨ Done! Now run:")
print("   git add backend/api/")
print('   git commit -m "Add trailing slashes to API routes"')
print("   git push")
