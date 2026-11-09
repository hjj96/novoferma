# Popsy homepage implementation — 9 November 2026

Source visual truth: output/research/home-hero-concepts-2026-11-09/popsy-hero-refined-v2.png.
Implementation: http://127.0.0.1:8765/; output/concept/index.html.
Browser: Codex in-app browser, rendered static site served locally.

## Comparison evidence

- Source and desktop implementation both 1585 × 992 px; CSS viewport1585 × 992, density1. No normalization required.
- Final desktop screenshot: output/research/popsy-home-implementation-2026-11-09/desktop-1585.jpg.
- Full source/implementation comparison: output/research/popsy-home-implementation-2026-11-09/desktop-comparison.jpg (3170 × 992; source left, implementation right).
- Focused type and package comparison: output/research/popsy-home-implementation-2026-11-09/type-and-pack-comparison.jpg.
- Mobile adaptations: mobile-390.jpg (390 × 844) and mobile-320.jpg (320 × 568), same research directory.
- Other visual evidence: tablet-768.jpg, landscape-844.jpg and desktop-short-1440.jpg.
- State: entrance complete, images loaded, navigation closed. No browser/device frame. Mobile is an intentional recomposition authorized by the user, rather than a scaled desktop screenshot.

## Findings and fixes

1. [P2, resolved] Initial desktop handwritten caption touched the last headline letter. Reduced headline scale to20.5cqw and note scale to4.7cqw; tablet uses21cqw headline. Recaptured desktop and768px tablet; clear separation now.
2. [P2, resolved] Initial mobile layout pushed the description and CTA away from the artwork with a large empty gap. Removed viewport-height stretching and automatic bottom spacing. Final390px capture shows contiguous title, artwork, description and CTA.
3. [P2, resolved] The320 × 568 viewport initially required scrolling to see the entire CTA. Added compact artwork composition for short phones. Final CTA bottom549.26px and hero bottom565.26px, both within568px; no horizontal overflow.
4. [P3, accepted] Header retains the site's existing logo/navigation sizing. Existing native-alpha package artwork is used with its original proportions and label; its exact angle differs slightly from the generated concept. This protects real packaging identity. Prepared food is a faithful independent native ImageGen cutout and its surface is a more natural golden brown. No standalone duplicate mascot.

## Required fidelity surfaces

- Typography: existing locally hosted Novoferma Protein poster font, Onest UI and Caveat handwritten caption. Live H1/copy/button; correct Russian text; no text rasterization outside the printed package. Large uppercase hierarchy and handwritten orange accent retain the concept.
- Spacing/layout: desktop maintains title behind packaging, prepared product to its right and bottom action row. Mobile stacks and overlaps products with protected label text. Tablet and short landscape have independent scales; no page-width overflow at320,360,390,430,768,844,1024,1440,1585 or1920px.
- Colors/tokens: uniform brand cream #F9EFDC, chocolate #432714 and burnt-orange handwritten text. No extra floor, gradient or UI surfaces were introduced.
- Assets: supplied package artwork preserved; ready food has genuine alpha, three whole pieces and two cut halves. Independent responsive WebP images; no baked screenshot, placeholders or drawn substitute assets. Label/cut face reviewed in focused comparisons.
- Content: headline Попсы, handwritten Хрусти в своём ритме, approved mini-nugget description and native О Попсах link. No invented weights, timing, claims or prices.

## Motion and interaction verification

- Staggered entrance ends after about1.4 seconds. Pointer parallax is bounded to5px for package and8px for food; observed values3.83px and−6.13px respectively. No perpetual motion loop.
- Reduced-motion disables entrance and pointer motion; coarse pointers do not receive the mouse effect. Script/image-decode failure cannot hide content indefinitely; a1.6s fallback is verified.
- Native CTA -> product-popsy.html -> where-to-buy.html?product=popsy confirmed in browser; Popсы selected on the purchase page.
- Mobile menu opened and closed; page interaction restored. Browser console error log empty.
- Static source checks:24 pages pass. Interaction suite:17/17 pass, including12 unchanged request-form scenarios, progressive startup, reduced motion, stalled image decoding and missing-hero safety.
- Generated section matches scripts/popsy_home.py exactly. Other homepage sections remain byte-for-byte identical to the pre-change homepage. Full generator was not run over existing direct edits.

## Implementation checklist

- [x] Replace homepage carousel with one approved product hero.
- [x] Preserve packaging and provide responsive prepared-food cutouts.
- [x] Live UI text, bounded motion and reduced-motion fallback.
- [x] Desktop, tablet, portrait and short-screen mobile verification.
- [x] Product/purchase navigation and mobile menu verified.
- [x] Static and interaction checks pass.
- [x] Compare same-size source and browser implementation; resolve P2 issues.

## Published verification

Permanent URL https://novoferma-team-preview.vercel.app/ verified after READY. Deployment dpl_5UN6BejL75JuPYpxyWkPFzz26BDk, commit bad6742639feb374802686999e4c078d5b1abfee. Finalizer confirmed version marker and noindex/robots. Published browser captures: published-desktop.jpg and published-mobile.jpg in the same research directory. Mobile390 × 844: both images loaded, no overflow, CTA bottom706px. Old carousel absent.

Final result: passed
