# Typography System

This document describes the comprehensive typography system implemented for the Elevate AI frontend, following the specified font theme.

## Font Stack

### 1. **Inter (400–600)** - Body and UI Text
- **Usage**: All body text, UI elements, buttons, form inputs
- **Size**: 16px
- **Line Height**: 1.6
- **Weights**: 400 (regular), 500 (medium), 600 (semibold)
- **Google Fonts**: `Inter:wght@400;500;600`

### 2. **Montserrat (600–800)** - Headings
- **Usage**: All headings (H1-H6), titles, section headers
- **Scale**: 48px → 22px
- **Line Height**: 1.2
- **Weights**: 600 (semibold), 700 (bold), 800 (extrabold)
- **Google Fonts**: `Montserrat:wght@600;700;800`

### 3. **Fira Code (400)** - Code and Technical Content
- **Usage**: Code snippets, technical text, monospace content
- **Size**: 14px
- **Line Height**: 1.4
- **Weight**: 400 (regular)
- **Features**: Ligatures enabled
- **Google Fonts**: `Fira+Code:wght@400`

## Heading Scale (Montserrat)

### H1 - `.heading-1`
- **Size**: 48px
- **Weight**: 800 (extrabold)
- **Line Height**: 1.2
- **Usage**: Page titles, hero headings

### H2 - `.heading-2`
- **Size**: 40px
- **Weight**: 700 (bold)
- **Line Height**: 1.2
- **Usage**: Section titles, major headings

### H3 - `.heading-3`
- **Size**: 32px
- **Weight**: 700 (bold)
- **Line Height**: 1.2
- **Usage**: Subsection titles

### H4 - `.heading-4`
- **Size**: 28px
- **Weight**: 600 (semibold)
- **Line Height**: 1.2
- **Usage**: Card titles, component headings

### H5 - `.heading-5`
- **Size**: 24px
- **Weight**: 600 (semibold)
- **Line Height**: 1.2
- **Usage**: Small section headings

### H6 - `.heading-6`
- **Size**: 22px
- **Weight**: 600 (semibold)
- **Line Height**: 1.2
- **Usage**: Smallest headings, labels

## Body Text Classes (Inter)

### `.body-text`
- **Size**: 16px
- **Weight**: 400 (regular)
- **Line Height**: 1.6
- **Usage**: Default body text, paragraphs

### `.body-text-medium`
- **Size**: 16px
- **Weight**: 500 (medium)
- **Line Height**: 1.6
- **Usage**: Emphasized text, important content

### `.body-text-semibold`
- **Size**: 16px
- **Weight**: 600 (semibold)
- **Line Height**: 1.6
- **Usage**: Strong emphasis, labels, UI text

## Code Text Classes (Fira Code)

### `.code-text`
- **Size**: 14px
- **Weight**: 400
- **Line Height**: 1.4
- **Features**: Ligatures enabled
- **Styling**: Background, padding, rounded corners
- **Usage**: Inline code snippets

### `.code-block`
- **Size**: 14px
- **Weight**: 400
- **Line Height**: 1.4
- **Features**: Ligatures enabled
- **Styling**: Block background, padding, border
- **Usage**: Code blocks, preformatted text

## Usage Examples

### HTML Elements
```html
<!-- Headings automatically use Montserrat -->
<h1>Main Page Title</h1>
<h2>Section Title</h2>
<h3>Subsection Title</h3>

<!-- Body text uses Inter by default -->
<p>This is body text using Inter at 16px/1.6</p>

<!-- Code elements use Fira Code -->
<code>inline code</code>
<pre>code block</pre>
```

### CSS Classes
```html
<!-- Explicit heading classes -->
<div class="heading-1">Custom H1 Style</div>
<div class="heading-4">Custom H4 Style</div>

<!-- Body text variants -->
<p class="body-text">Regular body text</p>
<p class="body-text-medium">Medium weight text</p>
<p class="body-text-semibold">Semibold text</p>

<!-- Code text -->
<span class="code-text">inline code</span>
<div class="code-block">code block content</div>
```

### React Components
```tsx
// Button components use Inter 600 (semibold)
<Button variant="primary">Action Button</Button>

// Input components use Inter 400 at 16px
<input className="input" placeholder="Enter text..." />

// Custom heading with Montserrat
<h2 className="heading-2 text-secondary-900">
  Dashboard Overview
</h2>
```

## Font Loading

Fonts are loaded via Google Fonts CDN in `index.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400&display=swap');
```

## CSS Variables

Typography-related CSS variables in the theme:

```css
--font-family-sans: Inter, system-ui, sans-serif;
--font-family-heading: Montserrat, system-ui, sans-serif;
--font-family-mono: 'Fira Code', 'Consolas', 'Monaco', monospace;
--font-size-body: 16px;
--line-height-body: 1.6;
--line-height-heading: 1.2;
--line-height-code: 1.4;
```

## Best Practices

1. **Use semantic HTML elements** (h1-h6, p, code, pre) when possible
2. **Apply explicit classes** when you need specific styling outside semantic context
3. **Maintain consistent line heights** (1.6 for body, 1.2 for headings, 1.4 for code)
4. **Use appropriate font weights** within the specified ranges
5. **Enable ligatures** for code fonts to improve readability
6. **Test font loading** and provide fallbacks for better performance

## Accessibility

- All fonts meet WCAG contrast requirements when used with the nature-inspired color palette
- Font sizes are large enough for comfortable reading (minimum 16px for body text)
- Line heights provide adequate spacing for readability
- Semantic HTML elements ensure proper screen reader support
