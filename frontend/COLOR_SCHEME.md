# Nature-Inspired Color Scheme

This document describes the new nature-inspired color palette implemented for the Elevate AI frontend.

## Color Palette Overview

The color scheme follows a five-step, nature-inspired approach:

### 1. **Primary Colors - Vibrant Cyan** (#0FA4AF)
*Interactive highlights and primary actions*
- Used for: Interactive elements, primary buttons, links, focus states
- Tailwind classes: `primary-50` through `primary-900`

### 2. **Secondary Colors - Deep Ocean/Forest Teal** (#003135 to #AFDDE5)
*Brooding backgrounds and text*
- Deep ocean teal (#003135): `secondary-900` - Dark backgrounds, headers
- Forest teal (#024950): `secondary-700` - Medium backgrounds, text
- Pale aqua (#AFDDE5): `secondary-50` - Light backgrounds, form fields
- Used for: Backgrounds, text, borders, secondary elements

### 3. **Accent Colors - Burnt Sienna** (#964734)
*Warm accent for calls-to-action*
- Used for: Important CTAs, accent buttons, highlights
- Tailwind classes: `accent-50` through `accent-900`

### 4. **Success Colors** 
*Harmonized with nature theme*
- Used for: Success states, positive feedback
- Tailwind classes: `success-50` through `success-900`

### 5. **Warning Colors**
*Harmonized with burnt sienna*
- Used for: Warning states, caution indicators
- Tailwind classes: `warning-50` through `warning-900`

### 6. **Danger Colors**
*Harmonized with nature theme*
- Used for: Error states, destructive actions
- Tailwind classes: `danger-50` through `danger-900`

## Usage Guidelines

### Button Variants
- **Primary**: Use `variant="primary"` for main actions (vibrant cyan)
- **Secondary**: Use `variant="secondary"` for secondary actions (teal tones)
- **Accent**: Use `variant="accent"` for important CTAs (burnt sienna)
- **Outline**: Use `variant="outline"` for subtle actions
- **Ghost**: Use `variant="ghost"` for minimal actions

### Background Usage
- **Light backgrounds**: Use `bg-secondary-50` (pale aqua) for form fields and panels
- **Medium backgrounds**: Use `bg-secondary-100` to `bg-secondary-300` for cards
- **Dark backgrounds**: Use `bg-secondary-700` to `bg-secondary-900` for headers and footers

### Text Colors
- **Primary text**: Use `text-secondary-900` or `text-secondary-800`
- **Secondary text**: Use `text-secondary-600` or `text-secondary-700`
- **Muted text**: Use `text-secondary-500`

### Interactive Elements
- **Focus states**: Use `ring-primary-500` for focus rings
- **Hover states**: Use lighter shades of the base color
- **Active states**: Use darker shades of the base color

## Examples

```tsx
// Primary button (vibrant cyan)
<Button variant="primary">Save Changes</Button>

// Accent button for important CTAs (burnt sienna)
<Button variant="accent">Get Started</Button>

// Card with pale aqua background
<div className="bg-secondary-50 border border-secondary-300 rounded-lg p-6">
  <h3 className="text-secondary-900">Card Title</h3>
  <p className="text-secondary-600">Card content</p>
</div>

// Input field with nature-inspired styling
<input className="bg-secondary-50 border-secondary-300 text-secondary-900 focus:ring-primary-500" />
```

## Color Values

### Primary (Vibrant Cyan)
- 50: #f0fdff
- 100: #ccf7fe
- 200: #99effd
- 300: #66e7fc
- 400: #33dffb
- 500: #0FA4AF (base)
- 600: #0e939e
- 700: #0c828d
- 800: #0a717c
- 900: #08606b

### Secondary (Ocean/Forest Teal)
- 50: #AFDDE5 (pale aqua)
- 100: #9dd6de
- 200: #7bc9d4
- 300: #59bcca
- 400: #37afc0
- 500: #2a8a98
- 600: #1d6570
- 700: #024950 (forest teal)
- 800: #013a40
- 900: #003135 (deep ocean teal)

### Accent (Burnt Sienna)
- 50: #fdf6f4
- 100: #fae8e3
- 200: #f4d1c7
- 300: #eeb9ab
- 400: #e8a28f
- 500: #e28b73
- 600: #c8704f
- 700: #964734 (base)
- 800: #7a3a2a
- 900: #5e2d20

## Migration Notes

- Old `blue-*` classes in stat cards have been replaced with `primary-*`
- Old `green-*` classes have been replaced with `success-*`
- Old hardcoded colors have been replaced with the new palette
- Glass morphism effects now use the pale aqua background
- Form fields and secondary panels use the pale aqua color (#AFDDE5)
