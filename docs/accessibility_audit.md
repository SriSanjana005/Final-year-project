# Accessibility Audit Report

## 1. Keyboard Navigation
- All interactive controls, navigation links, and quiz option selectors support keyboard navigation (`Tab`, `Shift+Tab`, `Enter`, `Space`).
- Focus rings are visibly styling using Tailwind `focus-visible:ring-2 focus-visible:ring-primary` tokens.

## 2. Color Contrast & Readability
- Color system built on WCAG 2.1 AA compliant contrast ratios:
  - Text primary: `#0F172A` (Slate 900) on `#FFFFFF` / `#F8FAFC` background.
  - Primary action: `#2563EB` (Blue 600) with white text.
  - Success badge: `#14B8A6` (Teal 500) with high-contrast text.
- Information state is never communicated solely through color; text badges and icons accompany state indicators.

## 3. Screen Reader & Semantic HTML
- Headings use proper H1 $\rightarrow$ H2 $\rightarrow$ H3 hierarchy across child, parent, and admin views.
- Form inputs have associated `<label>` elements and `aria-label` attributes where appropriate.

## 4. Touch Target Sizes
- Interactive buttons and cards maintain a minimum 44x44px touch/click target size for child accessibility.
