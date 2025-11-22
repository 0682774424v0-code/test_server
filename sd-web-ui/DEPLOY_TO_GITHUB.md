# GitHub Pages Deployment Guide

## Step-by-Step Deployment

### Option 1: Deploy Existing Repository (Recommended)

#### 1. Initialize Git Repository
```bash
cd c:\Users\Administrator\Downloads\Stable_Diffusion\poyo_test_sd\sd-web-ui
git init
```

#### 2. Add Files to Git
```bash
git add .
git commit -m "Initial commit: Stable Diffusion Web UI"
```

#### 3. Create GitHub Repository
- Go to https://github.com/new
- Repository name: `sd-web-ui`
- Description: "Web-based UI for Stable Diffusion image generation"
- Choose: Public (so it's accessible)
- Click "Create repository"

#### 4. Connect Local to Remote
Replace `YOUR_USERNAME` with your GitHub username:
```bash
git remote add origin https://github.com/YOUR_USERNAME/sd-web-ui.git
git branch -M main
git push -u origin main
```

#### 5. Enable GitHub Pages
1. Go to repository: https://github.com/YOUR_USERNAME/sd-web-ui
2. Click "Settings" (top right)
3. In left sidebar, click "Pages"
4. Under "Source", select "Deploy from a branch"
5. Choose branch: `main`
6. Choose folder: `/ (root)`
7. Click "Save"

#### 6. Access Your Site
Wait 1-2 minutes for deployment, then visit:
```
https://YOUR_USERNAME.github.io/sd-web-ui/
```

### Option 2: Use GitHub Desktop (Visual)

1. Download [GitHub Desktop](https://desktop.github.com/)
2. Click "File" → "Clone Repository"
3. URL tab: `https://github.com/YOUR_USERNAME/sd-web-ui.git`
4. Choose local path
5. Click "Clone"
6. Make changes to files
7. GitHub Desktop will show changes
8. Write commit message
9. Click "Commit to main"
10. Click "Push origin"
11. Enable Pages in repository settings (steps above)

### Option 3: Deploy Using Git Command Line (Advanced)

```bash
# Navigate to project
cd sd-web-ui

# Initialize if not done
git init

# Configure git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Stable Diffusion Web UI"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/sd-web-ui.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main

# Verify
git remote -v
```

## Post-Deployment Configuration

### 1. Update Settings After First Push

If you need to update the site:
```bash
# Make changes to files
echo "// Updated code" >> app.js

# Commit changes
git add .
git commit -m "Update: Added new feature"

# Push to GitHub
git push origin main
```

The site will automatically update within 1-2 minutes.

### 2. Custom Domain (Optional)

To use your own domain instead of `github.io`:

1. Go to repository Settings → Pages
2. Under "Custom domain", enter your domain: `mydomain.com`
3. Click "Save"
4. You'll get instructions for DNS configuration
5. Update your domain's DNS records as shown
6. Wait for DNS propagation (5-30 minutes)

### 3. Enable HTTPS (Automatic)

- GitHub Pages automatically enables HTTPS
- Check the "Enforce HTTPS" checkbox in Pages settings
- Your site will be served as `https://...`

## Troubleshooting Deployment

### Issue: "No README found"
**Solution**: GitHub automatically creates pages from index.html. If it doesn't work:
- Verify `index.html` is in root directory
- Ensure it's a valid HTML file
- Try refreshing the page

### Issue: Site shows "404"
**Solution**:
1. Check repository is public
2. Verify Pages is enabled
3. Wait 2-5 minutes for deployment
4. Check branch is `main`
5. Verify files are pushed to GitHub: `git push origin main`

### Issue: Resources not loading (images, CSS)
**Solution**: Ensure paths are relative:
```html
<!-- ✅ CORRECT -->
<link rel="stylesheet" href="style.css">
<img src="img/logo.png">

<!-- ❌ WRONG -->
<link rel="stylesheet" href="/style.css">
<img src="C:/path/to/img/logo.png">
```

### Issue: "WebSocket connection refused"
**Solution**: This is expected! WebSocket won't work from file:// URLs.
- The app is designed to work with remote servers
- Ensure server (Colab) is running
- Verify endpoint URL is correct
- Check server password

## CI/CD with GitHub Actions (Optional)

Create `.github/workflows/test.yml`:

```yaml
name: Validate HTML

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate HTML
        run: |
          npm install -g html-validate
          html-validate index.html
      
      - name: Check for common errors
        run: |
          grep -E '(console\.error|TODO|FIXME)' *.js || echo "No errors found"
```

## Monitoring Deployment

### Check Build Status
1. Go to your repository
2. Click "Actions" tab
3. See build history
4. Red ✗ = failed, Green ✓ = success

### View Logs
Click on any build in Actions to see:
- Build steps
- Error messages
- Deployment time

## Rollback Changes

If something breaks:

```bash
# View commit history
git log --oneline

# Revert to previous version (replace COMMIT_ID)
git revert COMMIT_ID

# Or reset (⚠️ careful!)
git reset --hard HEAD~1

# Push changes
git push origin main
```

## Updating Your Site

### Update Single File
```bash
# Edit the file
vim index.html

# Commit and push
git add index.html
git commit -m "Update: Fixed connection panel"
git push origin main
```

### Update All Files
```bash
# Make changes to multiple files
# ...

# Add all changes
git add .

# Commit with message
git commit -m "Update: New features and bug fixes"

# Push to GitHub
git push origin main
```

## Sharing Your Site

Once deployed, share the URL:

### In Discord
```
Check out my Stable Diffusion Web UI:
https://YOUR_USERNAME.github.io/sd-web-ui/
```

### In Email
```
Subject: Stable Diffusion Image Generator

Hi,

I've created a web-based UI for Stable Diffusion image generation.
You can access it here: https://YOUR_USERNAME.github.io/sd-web-ui/

To use it, you need:
1. WebSocket endpoint from Colab server
2. Server password

Try it out!
```

### On Social Media
```
Just deployed my Stable Diffusion Web UI! 
Access it at: https://YOUR_USERNAME.github.io/sd-web-ui/

Features:
- Real-time image generation
- Multiple sampler options
- Image-to-Image support
- Settings persistence

Try it out! #StableDiffusion #WebUI #AI
```

## Advanced Deployment

### Deploy Multiple Branches

```bash
# Create production branch
git checkout -b production

# Make changes
# ...

# Commit and push
git add .
git commit -m "Production release v1.0"
git push origin production

# In GitHub Pages settings, select 'production' branch
```

### Deploy to Staging First

```bash
# Create staging branch
git checkout -b staging

# Push to GitHub
git push origin staging

# Enable Pages for staging branch (different repo or branch)
# Test at: https://YOUR_USERNAME.github.io/staging/

# When ready, merge to main
git checkout main
git merge staging
git push origin main
```

## Performance Tips

### 1. Enable Caching
GitHub Pages automatically caches static assets. For manual control, add `.htaccess`:
```apache
<IfModule mod_headers.c>
  <FilesMatch "\.(jpg|jpeg|png|gif|css|js)$">
    Header set Cache-Control "max-age=2592000, public"
  </FilesMatch>
</IfModule>
```

### 2. Minify CSS/JS
For production, minify your files:
```bash
# Using nodejs
npm install -g terser
terser app.js -o app.min.js

# Update HTML to use .min.js
```

### 3. Optimize Images
If you add images:
```bash
# Using ImageMagick
convert image.png -resize 50% image-optimized.png
```

## Maintenance

### Weekly Checklist
- [ ] Check site loads correctly
- [ ] Test WebSocket connection
- [ ] Review any error logs
- [ ] Update documentation if needed

### Monthly Checklist
- [ ] Review GitHub commits
- [ ] Check for browser compatibility issues
- [ ] Update dependencies in package.json
- [ ] Test on mobile devices
- [ ] Backup important configurations

## Support

### GitHub Pages Limits
- Repository size: 100 MB recommended (no hard limit)
- Bandwidth: Unlimited
- Sites per account: Unlimited
- Build time: 10 minutes
- Deployments: Automatic on push

### Need Help?
- GitHub Pages Docs: https://docs.github.com/pages
- GitHub Community: https://github.com/orgs/community
- Stack Overflow: Tag `github-pages`

## Next Steps After Deployment

1. ✅ Test the deployed site
2. ✅ Share the URL with team
3. ✅ Configure WebSocket endpoint
4. ✅ Start generating images!
5. ✅ Collect feedback
6. ✅ Plan improvements

---

**Congratulations! Your Stable Diffusion Web UI is now live on the internet!** 🎉

Access it at: `https://YOUR_USERNAME.github.io/sd-web-ui/`
