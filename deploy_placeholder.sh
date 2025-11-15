#!/bin/bash
# Deploy GIF placeholder to gozeroshot.dev
# Following Distro Dojo: unified deployment + unified asset paths

set -e

echo "🖼️ Deploying GIF Placeholder to gozeroshot.dev"
echo "==============================================="

# Check if placeholder directory exists
if [ ! -d "placeholder" ]; then
    echo "❌ Placeholder directory not found"
    exit 1
fi

# Verify all required files exist
REQUIRED_FILES=(
    "placeholder/index.html"
    "placeholder/rt_feature_eng.gif"
    "placeholder/vercel.json"
)

echo "🔍 Verifying unified asset paths..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing unified asset: $file"
        exit 1
    fi
done
echo "✅ All unified assets present"

echo ""
echo "🎯 DEPLOYMENT OPTIONS:"
echo "======================"
echo ""
echo "1. Vercel (Recommended for gozeroshot.dev):"
echo "   cd placeholder"
echo "   vercel --prod"
echo "   # Or through Vercel dashboard"
echo ""
echo "2. Netlify:"
echo "   cd placeholder"
echo "   netlify deploy --prod"
echo ""
echo "3. GitHub Pages:"
echo "   # Create new repo: gozeroshot.dev"
echo "   cp -r placeholder/* /path/to/gozeroshot.dev/"
echo "   git add . && git commit -m 'Add GIF placeholder'"
echo "   git push origin main"
echo ""
echo "4. Manual static hosting:"
echo "   Upload placeholder/ contents to any static host"
echo ""
echo "📁 Files ready in: placeholder/"
echo "   ├── index.html (main page)"
echo "   ├── rt_feature_eng.gif (demo GIF)"
echo "   └── vercel.json (deployment config)"
echo ""
echo "🎨 Preview locally:"
echo "   cd placeholder && python -m http.server 8000"
echo "   # Visit: http://localhost:8000"
echo ""
echo "✅ Distro Dojo compliant placeholder ready!"
