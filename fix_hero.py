with open('app_pro.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hero banner icon and add version
content = content.replace(
    '<div class="hero-title">🎯 AI Visual Insight Pro</div>',
    '<div class="hero-title">🎬 AI Visual Insight Pro</div>'
)

content = content.replace(
    '<div class="hero-subtitle">Advanced Video Analysis • AI Summarization • Content Moderation</div>',
    '<div class="hero-subtitle">Advanced Video Analysis • AI Summarization • Content Moderation • Version 2.0</div>'
)

# Fix emoji encoding issues in badges
content = content.replace('� Multi-Language', '🌍 Multi-Language')
content = content.replace('�🎤 Speech-to-Text', '🎤 Speech-to-Text')

with open('app_pro.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Updated hero banner with new icon and fixed emojis')
