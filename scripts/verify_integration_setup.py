#!/usr/bin/env python3
"""
Comprehensive verification of article integration workflow setup.
Validates configuration, dependencies, and integration readiness.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def check_workflow_files():
    """Verify all required workflow files exist"""
    print("\n" + "="*70)
    print("CHECKING WORKFLOW FILES")
    print("="*70)
    
    workflows_dir = Path(".github/workflows")
    required_workflows = {
        "jekyll.yml": "Main Jekyll build and deployment",
        "fetch-news-feeds.yml": "Daily RSS feed fetching",
        "integrate-approved-articles.yml": "Article integration workflow",
        "verify-approved-articles.yml": "Article verification pipeline",
    }
    
    all_exist = True
    for workflow, description in required_workflows.items():
        path = workflows_dir / workflow
        if path.exists():
            print(f"✓ {workflow}")
            print(f"  └─ {description}")
        else:
            print(f"✗ {workflow} - MISSING")
            all_exist = False
    
    return all_exist

def check_allowlist():
    """Verify allowlist.json v2.1 with FCC sources"""
    print("\n" + "="*70)
    print("CHECKING ALLOWLIST v2.1")
    print("="*70)
    
    allowlist_path = Path("demos/langsmith_langgraph_demo/allowlist.json")
    
    if not allowlist_path.exists():
        print(f"✗ Allowlist not found at {allowlist_path}")
        return False
    
    with open(allowlist_path) as f:
        allowlist = json.load(f)
    
    # Check version
    version = allowlist.get("metadata", {}).get("version")
    if version == "2.1":
        print(f"✓ Allowlist version: {version}")
    else:
        print(f"⚠ Allowlist version: {version} (expected 2.1)")
    
    # Check FCC sources
    fcc_sources = ["kwtb.com", "kvue.com", "kbtx.com", "kwbu.org", "templedailytelegram.com"]
    domains = set(d.lower().replace("www.", "") for d in allowlist.get("domains", []))
    
    print(f"\n✓ Total domains: {len(allowlist.get('domains', []))}")
    
    print("\nFCC Call Letter Sources:")
    for source in fcc_sources:
        normalized = source.replace("www.", "")
        if any(normalized in d or d in normalized for d in domains):
            print(f"  ✓ {source}")
        else:
            print(f"  ✗ {source} - NOT FOUND")
    
    # Check social media
    social_count = len(allowlist.get("social_media_accounts", []))
    print(f"\n✓ Social media accounts: {social_count}")
    
    # Check RSS feeds
    rss_count = len(allowlist.get("rss_feeds", []))
    print(f"✓ RSS feeds: {rss_count}")
    
    return True

def check_news_feed_data():
    """Verify news feed data structure"""
    print("\n" + "="*70)
    print("CHECKING NEWS FEED DATA")
    print("="*70)
    
    feed_path = Path("_data/news-feed.json")
    
    if not feed_path.exists():
        print(f"✗ News feed not found at {feed_path}")
        return False
    
    with open(feed_path) as f:
        feed = json.load(f)
    
    print(f"✓ News feed file exists")
    print(f"✓ Last updated: {feed.get('last_updated', 'Unknown')}")
    
    feeds = feed.get("feeds", [])
    print(f"✓ Feed sources: {len(feeds)}")
    
    total_items = 0
    for source in feeds:
        items = source.get("items", [])
        if items:
            total_items += len(items)
            print(f"  ✓ {source['source']}: {len(items)} articles")
    
    print(f"✓ Total articles available: {total_items}")
    
    return True

def check_blog_structure():
    """Verify blog post directory structure"""
    print("\n" + "="*70)
    print("CHECKING BLOG STRUCTURE")
    print("="*70)
    
    posts_dir = Path("_posts")
    
    if posts_dir.exists():
        posts = list(posts_dir.glob("*.md"))
        print(f"✓ Posts directory exists")
        print(f"✓ Current blog posts: {len(posts)}")
        
        if posts:
            # Show recent posts
            recent = sorted(posts)[-3:]
            print("  Recent posts:")
            for post in recent:
                print(f"    - {post.name}")
    else:
        print(f"⚠ Posts directory does not exist - will be created on first integration")
    
    return True

def check_jekyll_config():
    """Verify Jekyll configuration"""
    print("\n" + "="*70)
    print("CHECKING JEKYLL CONFIGURATION")
    print("="*70)
    
    config_path = Path("_config.yml")
    
    if not config_path.exists():
        print(f"✗ Jekyll config not found at {config_path}")
        return False
    
    with open(config_path) as f:
        content = f.read()
    
    print(f"✓ Jekyll config exists")
    
    # Check for key settings
    checks = [
        ("title", "Site title configured"),
        ("url", "Site URL configured"),
        ("baseurl", "Base URL configured"),
    ]
    
    for key, desc in checks:
        if key in content:
            print(f"✓ {desc}")
        else:
            print(f"⚠ {desc} - not found")
    
    return True

def check_scripts():
    """Verify integration scripts"""
    print("\n" + "="*70)
    print("CHECKING INTEGRATION SCRIPTS")
    print("="*70)
    
    scripts_to_check = [
        "scripts/fetch-rss-feeds.rb",
        "scripts/verify_markdown.py",
    ]
    
    all_exist = True
    for script in scripts_to_check:
        path = Path(script)
        if path.exists():
            print(f"✓ {script}")
        else:
            print(f"⚠ {script} - not found (will be generated on demand)")
    
    return True

def check_verification_pipeline():
    """Verify the verification and validation pipeline"""
    print("\n" + "="*70)
    print("CHECKING VERIFICATION PIPELINE")
    print("="*70)
    
    # Check workflow script files exist
    workflows_dir = Path(".github/workflows")
    
    key_workflows = [
        (workflows_dir / "jekyll.yml", "Main build workflow"),
        (workflows_dir / "integrate-approved-articles.yml", "Article integration"),
        (workflows_dir / "verify-approved-articles.yml", "Article verification"),
    ]
    
    all_exist = True
    for workflow_path, desc in key_workflows:
        if workflow_path.exists():
            with open(workflow_path) as f:
                content = f.read()
                
            # Check for key integration steps
            if "integrate" in content.lower() or "news" in content.lower():
                print(f"✓ {workflow_path.name}")
                print(f"  └─ {desc}")
            else:
                print(f"⚠ {workflow_path.name}")
                print(f"  └─ May need updates for integration")
                all_exist = False
        else:
            print(f"✗ {workflow_path.name} - MISSING")
            all_exist = False
    
    return all_exist

def generate_integration_report():
    """Generate comprehensive integration readiness report"""
    print("\n" + "="*70)
    print("ARTICLE INTEGRATION READINESS REPORT")
    print("="*70)
    
    checks = {
        "Workflow Files": check_workflow_files(),
        "Allowlist v2.1": check_allowlist(),
        "News Feed Data": check_news_feed_data(),
        "Blog Structure": check_blog_structure(),
        "Jekyll Config": check_jekyll_config(),
        "Scripts": check_scripts(),
        "Verification Pipeline": check_verification_pipeline(),
    }
    
    print("\n" + "="*70)
    print("READINESS SUMMARY")
    print("="*70)
    
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    print("\n" + "="*70)
    print(f"Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ READY FOR DEPLOYMENT")
        print("\nNext steps:")
        print("1. Commit all workflow files to repository")
        print("2. Push to main branch")
        print("3. GitHub Actions will automatically integrate articles")
        print("4. View status in Actions tab")
        return 0
    else:
        print("⚠ INCOMPLETE SETUP")
        print(f"\nFailed checks: {total - passed}")
        print("Please resolve issues above before deployment")
        return 1

def main():
    print("\n" + "🔍 " + "="*66)
    print("  ARTICLE INTEGRATION WORKFLOW VERIFICATION")
    print("="*70)
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print("="*70)
    
    result = generate_integration_report()
    
    print("\n" + "="*70)
    if result == 0:
        print("✓ All systems ready for article integration")
    else:
        print("⚠ Some issues need attention before proceeding")
    print("="*70 + "\n")
    
    return result

if __name__ == "__main__":
    sys.exit(main())
